from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

DATA_PATH = "data"
DB_PATH = "vector_db"

documents = []

# Load all PDFs
documents = []

files = os.listdir(DATA_PATH)

print("Files found:", files)

for file in files:

    if file.lower().endswith(".pdf"):

        file_path = os.path.join(DATA_PATH, file)

        print(f"Loading: {file}")

        loader = PyPDFLoader(file_path)

        docs = loader.load()

        for doc in docs:
            doc.metadata["filename"] = file

        documents.extend(docs)

print(f"Documents loaded: {len(documents)}")

# Smart chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", " ", ""]
)

chunks = splitter.split_documents(documents)

print(f"Chunks created: {len(chunks)}")

# Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded")

# Vector DB creation
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=DB_PATH
)

print("Knowledge base created successfully")