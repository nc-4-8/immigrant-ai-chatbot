from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from decouple import config
from .qdrant import vector_store



model = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=config("GOOGLE_API_KEY"),
    max_retries=3,
)
backup = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=config("GOOGLE_API_KEY"),
    max_retries=2,
)


prompt_template = """
You are a helpful assistant for immigrants in the United States.
Answer ONLY using the context below. Use simple words and short sentences, with bullet points where helpful. Answer in {language}.
If the context does not contain the answer, say you don't have that information and suggest checking an official source like uscis.gov or finding free legal help. Do not guess.
Context: {context}
Question: {question}
Answer:
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

retriever = vector_store.as_retriever(search_kwargs={"k": 4})

llm_chain = prompt | model

def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
        return "".join(parts)
    return ""


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

async def stream_answer_and_docs(question: str, language: str = "English"):
    context = await retriever.ainvoke(question)

    async for chunk in llm_chain.astream(
        {"context": format_docs(context), "question": question, "language": language}
    ):
        text = extract_text(chunk.content)
        if text:
            yield {"type": "token", "content": text}

    yield {
        "type": "done",
        "documents": [doc.model_dump() for doc in context],
    }

def get_answer_and_docs(question: str, language: str = "English"):
    context = retriever.invoke(question)
    response = llm_chain.invoke(
        {"context": format_docs(context), "question": question, "language": language}
    )
    return {"answer": extract_text(response.content), "context": context}