import json
from fastapi import FastAPI, Security, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl
from contextlib import asynccontextmanager
from decouple import config
from src.rag import stream_answer_and_docs
from src.qdrant import upload_website_to_collection, ensure_collection, COLLECTION_NAME

APP_API_KEY = config("APP_API_KEY") 

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Security(api_key_header)):
    if key != APP_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_collection(COLLECTION_NAME)
    yield

app = FastAPI(
    title="Chat Bot",
    description="A simple chat bot API",
    version="1.0.0",
    lifespan=lifespan,
)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: str = Field(default="English", max_length=30)

class IndexRequest(BaseModel):
    url: HttpUrl

class IndexResponse(BaseModel):
    url: HttpUrl

@app.post(
    "/chat",
    description="Chat with the API (streamed via SSE)",
    dependencies=[Security(verify_api_key)],
)
async def chat(message: Message):
    async def event_generator():
        try:
            async for event in stream_answer_and_docs(message.message, message.language):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            print(f"[/chat] error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': 'Failed to generate an answer'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post(
    "/indexing",
    description="Index a new website",
    response_model=IndexResponse,
    dependencies=[Security(verify_api_key)],
)
def indexing(request: IndexRequest):
    try:
        upload_website_to_collection(str(request.url))
        return IndexResponse(url=request.url)  
    except Exception as e:
        print(f"[/indexing] error: {e}")
        raise HTTPException(status_code=400, detail="Failed to index the provided URL.")
