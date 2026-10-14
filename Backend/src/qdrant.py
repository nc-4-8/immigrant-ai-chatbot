from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from qdrant_client import QdrantClient, models
from decouple import config


qdrant_api_key = config("QDRANT_API_KEY")
qdrant_url = config("QDRANT_URL")

client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
    timeout=10,
)

COLLECTION_NAME = config("QDRANT_COLLECTION_NAME", default="rag_chatbot")
EMBEDDING_DIM = 768 

def ensure_collection(collection_name: str):
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=EMBEDDING_DIM, distance=models.Distance.COSINE),
        )
        print(f"Collection {collection_name} created successfully")
    else:
        print(f"Collection {collection_name} already exists")

ensure_collection(COLLECTION_NAME)

embedding = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=config("GOOGLE_API_KEY"),
    output_dimensionality=768,
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embedding,
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=20,
    length_function=len
)

def upload_website_to_collection(url: str):
    loader = WebBaseLoader(url)
    documents = loader.load()
    chunks = text_splitter.split_documents(documents)
    vector_store.add_documents(chunks)
    print(f"Indexed {len(chunks)} chunks from {url}")