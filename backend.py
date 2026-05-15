from fastapi import FastAPI
from pydantic import BaseModel

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

import os

# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI(
    title="IntelliDocs AI API",
    version="1.0"
)

# -----------------------------
# VECTOR DB PATH
# -----------------------------
DB_PATH = "vector_db"

# -----------------------------
# EMBEDDING MODEL
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# LOAD CHROMA DB
# -----------------------------
db = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embedding_model
)

# -----------------------------
# GEMINI MODEL
# -----------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

# -----------------------------
# REQUEST MODEL
# -----------------------------
class QueryRequest(BaseModel):
    question: str

# -----------------------------
# HOME ROUTE
# -----------------------------
@app.get("/")
def home():

    return {
        "message": "IntelliDocs AI FastAPI Backend Running"
    }

# -----------------------------
# ASK ROUTE
# -----------------------------
@app.post("/ask")
def ask_question(request: QueryRequest):

    question = request.question

    # Semantic Retrieval
    results = db.similarity_search_with_score(
        question,
        k=5
    )

    # Context Creation
    context = "\n\n".join(
        [doc.page_content for doc, score in results]
    )

    # Prompt
    prompt = f"""
You are an enterprise AI assistant.

Answer ONLY using the provided context.

Context:
{context}

Question:
{question}
"""

    # Gemini Response
    response = llm.invoke(prompt)

    # Sources
    sources = []

    for doc, score in results:

        sources.append({
            "filename": doc.metadata.get(
                "filename",
                "Unknown"
            ),
            "score": round(score, 4),
            "content": doc.page_content[:300]
        })

    return {
        "question": question,
        "answer": response.content,
        "sources": sources
    }