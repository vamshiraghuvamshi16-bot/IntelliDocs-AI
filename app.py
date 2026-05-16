import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

DB_PATH = "vector_db"

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IntelliDocs AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

#

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;700;800&family=Instrument+Sans:wght@300;400;500&display=swap');

html, body, .stApp {
    background-color: #050C1A !important;
    font-family: 'Instrument Sans', sans-serif !important;
    color: #C8D8F0 !important;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 960px !important;
    padding: 1.5rem 2rem 5rem !important;
}

h1 {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    font-size: 64px !important;
    font-weight: 800 !important;
    text-align: center !important;
    color: #EFF6FF !important;
    letter-spacing: -2px !important;
}

.hero-sub {
    text-align: center;
    font-size: 17px;
    color: rgba(140,175,225,0.55);
    margin-bottom: 32px;
}

.grad-word {
    background: linear-gradient(
        90deg,
        #60A5FA 0%,
        #38BDF8 50%,
        #818CF8 100%
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.badge {
    display: block;
    text-align: center;
    margin-bottom: 16px;
}

.badge span {
    background: rgba(56,189,248,0.06);
    border: 1px solid rgba(56,189,248,0.20);
    border-radius: 100px;
    padding: 5px 18px;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #38BDF8;
}

div[data-testid="stTextInput"] input {
    background: rgba(10,20,50,0.85) !important;
    border: 1px solid rgba(59,130,246,0.30) !important;
    border-radius: 14px !important;
    color: #E2E8F0 !important;
    padding: 16px 20px !important;
    font-size: 15px !important;
}

.answer-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #3B82F6;
    margin-top: 25px;
    margin-bottom: 10px;
}

.src-head {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(80,120,180,0.45);
    margin: 36px 0 14px;
}

section[data-testid="stSidebar"] {
    background: rgba(5,12,28,0.97) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown("## ✦ IntelliDocs")

    st.success("Hybrid AI System Active")

    st.markdown("### Features")

    features = [
        "PDF Processing",
        "Smart Chunking",
        "HuggingFace Embeddings",
        "ChromaDB",
        "Semantic Retrieval",
        "AI Answers",
        "Dynamic PDF Upload",
        "Gemini + Groq Hybrid AI"
    ]

    for feature in features:
        st.markdown(f"✓ {feature}")

# ─────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="badge"><span>✦ Enterprise Knowledge Intelligence</span></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<h1>Intelli<span class="grad-word">Docs</span> AI</h1>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="hero-sub">Ask anything. Get precise answers grounded in enterprise documents.</p>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────
try:

    # Embedding model
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Permanent enterprise vector DB
    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_model
    )

    # ─────────────────────────────────────────
    # MODEL SELECTION
    # ─────────────────────────────────────────
    model_choice = st.sidebar.selectbox(
        "Choose AI Model",
        [
            "Gemini 2.5 Flash",
            "Groq Llama 3"
        ]
    )

    # Gemini
    if model_choice == "Gemini 2.5 Flash":

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=st.secrets["GOOGLE_API_KEY"]
        )

    # Groq
    else:

        llm = ChatGroq(
            groq_api_key=st.secrets["GROQ_API_KEY"],
            model_name="llama-3.1-8b-instant",
            temperature=0
        )

    # ─────────────────────────────────────────
    # PDF UPLOAD
    # ─────────────────────────────────────────
    st.markdown("### Upload PDF Documents")

    uploaded_files = st.file_uploader(
        "Drop one or more PDFs here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    uploaded_db = None

    if uploaded_files:

        os.makedirs("uploaded_docs", exist_ok=True)

        all_documents = []

        for uploaded_file in uploaded_files:

            file_path = os.path.join(
                "uploaded_docs",
                uploaded_file.name
            )

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"✓ Uploaded: {uploaded_file.name}")

            loader = PyPDFLoader(file_path)

            docs = loader.load()

            for doc in docs:
                doc.metadata["filename"] = uploaded_file.name

            all_documents.extend(docs)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = splitter.split_documents(all_documents)

        st.info(
            f"Created {len(chunks)} chunks from {len(uploaded_files)} file(s)"
        )

        uploaded_db_path = "uploaded_vector_db"

        uploaded_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=uploaded_db_path
        )

        st.success(
            "Temporary uploaded knowledge base created ✓"
        )

    # ─────────────────────────────────────────
    # QUESTION INPUT
    # ─────────────────────────────────────────
    st.markdown("### Ask a Question")

    question = st.text_input(
        "Question",
        placeholder="e.g. What is the leave policy?",
        label_visibility="collapsed"
    )

    if question:

        with st.spinner("Analyzing enterprise documents..."):

            if uploaded_db:

                results = uploaded_db.similarity_search_with_score(
                    question,
                    k=3
                )

            else:

                results = db.similarity_search_with_score(
                    question,
                    k=3
                )

            context = "\n\n".join(
                [doc.page_content for doc, score in results]
            )

            prompt = f"""
You are an enterprise AI assistant.

Answer professionally and clearly using ONLY the context below.

Write in readable paragraphs or bullet points.

Do NOT use HTML tags.

Context:
{context}

Question:
{question}
"""

            response = llm.invoke(prompt)

            answer = response.content

        # ─────────────────────────────────────────
        # AI ANSWER
        # ─────────────────────────────────────────
        st.markdown(
            '<div class="answer-label">AI Generated Answer</div>',
            unsafe_allow_html=True
        )

        st.markdown(answer)

        # ─────────────────────────────────────────
        # SOURCES
        # ─────────────────────────────────────────
        st.markdown(
            '<div class="src-head">Source Documents</div>',
            unsafe_allow_html=True
        )

        for i, (doc, score) in enumerate(results, 1):

            filename = doc.metadata.get(
                "filename",
                "Unknown Document"
            )

            excerpt = " ".join(
                doc.page_content.split()
            )[:500]

            with st.container(border=True):

                col1, col2 = st.columns([7, 3])

                with col1:
                    st.markdown(f"**📄 {filename}**")

                with col2:
                    st.markdown(
                        f"""
<p style='text-align:right;
color:rgba(80,120,180,0.5);
font-size:12px;'>
Score: {round(score,3)}
</p>
""",
                        unsafe_allow_html=True
                    )

                st.caption(excerpt)

except Exception as e:

    st.error(f"⚠ System error: {e}")
