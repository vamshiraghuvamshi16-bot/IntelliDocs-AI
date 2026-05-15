import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
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
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# CSS  — only safe rules, no content injected via HTML strings
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;700;800&family=Instrument+Sans:wght@300;400;500&display=swap');

html, body, .stApp {
    background-color: #050C1A !important;
    font-family: 'Instrument Sans', sans-serif !important;
    color: #C8D8F0 !important;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 960px !important;
    padding: 1.5rem 2rem 5rem !important;
}

/* ── Native Streamlit element overrides ── */

/* Title rendered by st.title() */
h1 {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    font-size: 64px !important;
    font-weight: 800 !important;
    text-align: center !important;
    color: #EFF6FF !important;
    letter-spacing: -2px !important;
    line-height: 1.05 !important;
    padding-bottom: 0 !important;
}

/* Subtitle rendered by st.markdown plain text centred */
.hero-sub {
    text-align: center;
    font-size: 17px;
    color: rgba(140,175,225,0.55);
    margin-bottom: 32px;
    margin-top: -8px;
}

/* Coloured word inside h1 — injected via a SAFE single span */
.grad-word {
    background: linear-gradient(90deg, #60A5FA 0%, #38BDF8 50%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 64px;
    font-weight: 800;
    letter-spacing: -2px;
}

/* Badge */
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
    font-weight: 500;
}

/* ── Input ── */
div[data-testid="stTextInput"] input {
    background: rgba(10,20,50,0.85) !important;
    border: 1px solid rgba(59,130,246,0.30) !important;
    border-radius: 14px !important;
    color: #E2E8F0 !important;
    padding: 16px 20px !important;
    font-size: 15px !important;
    font-family: 'Instrument Sans', sans-serif !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(59,130,246,0.65) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.10) !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: rgba(70,110,170,0.5) !important;
}

/* ── Answer card (wraps st.info / st.markdown naturally) ── */
div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stMarkdownContainer"] > .answer-inner) {
    background: linear-gradient(140deg, rgba(12,22,48,0.95), rgba(14,26,56,0.92)) !important;
    border: 1px solid rgba(59,130,246,0.22) !important;
    border-radius: 20px !important;
    padding: 28px 32px !important;
    margin-top: 24px !important;
    box-shadow: 0 4px 40px rgba(0,0,0,0.4) !important;
}

/* Label above answer */
.answer-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #3B82F6;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.answer-label::before {
    content: '';
    width: 16px; height: 1px;
    background: #3B82F6;
    display: inline-block;
}

/* Markdown content colours */
div[data-testid="stMarkdownContainer"] p {
    color: #C8D8F0 !important;
    font-size: 15px !important;
    line-height: 1.85 !important;
    font-family: 'Instrument Sans', sans-serif !important;
}
div[data-testid="stMarkdownContainer"] li {
    color: #C8D8F0 !important;
    font-size: 15px !important;
    line-height: 1.75 !important;
}
div[data-testid="stMarkdownContainer"] strong {
    color: #93C5FD !important;
}
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3 {
    color: #E2E8F0 !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
}

/* ── Source cards ── */
.src-head {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: rgba(80,120,180,0.45);
    margin: 36px 0 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.src-head::after {
    content: '';
    flex: 1; height: 1px;
    background: rgba(255,255,255,0.04);
}

/* st.container gets this style via a data attribute trick */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(10,20,46,0.70) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 4px 8px !important;
    margin-bottom: 10px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(59,130,246,0.22) !important;
    transform: translateY(-1px);
    transition: all 0.2s;
}

/* st.caption */
div[data-testid="stCaptionContainer"] p {
    color: rgba(100,140,195,0.60) !important;
    font-size: 13px !important;
    line-height: 1.72 !important;
    border-left: 2px solid rgba(59,130,246,0.18) !important;
    padding-left: 12px !important;
}

/* File uploader */
div[data-testid="stFileUploader"] {
    background: rgba(10,20,50,0.5) !important;
    border: 1px dashed rgba(59,130,246,0.25) !important;
    border-radius: 14px !important;
    padding: 12px !important;
}

/* Section headers (st.markdown "###") */
h3 {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    color: #E2E8F0 !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    margin: 28px 0 10px !important;
    letter-spacing: -0.3px !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(5,12,28,0.97) !important;
    border-right: 1px solid rgba(40,90,200,0.10) !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] label {
    color: rgba(160,200,255,0.65) !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #EFF6FF !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #38BDF8 !important; }

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✦ IntelliDocs")
    st.success("Gemini 2.5 Flash Active")
    st.markdown("### Features")
    for f in [
        "PDF Processing", "Smart Chunking", "HuggingFace Embeddings",
        "ChromaDB", "Semantic Retrieval", "AI Answers", "Dynamic PDF Upload"
    ]:
        st.markdown(f"✓ {f}")
    st.markdown("---")
    st.markdown("**Model:** `gemini-2.5-flash`")
    st.caption("Google DeepMind")

# ─────────────────────────────────────────────────────────────
# HERO  — built entirely from native Streamlit calls
# ─────────────────────────────────────────────────────────────

# Badge: one simple <span> inside a <div> — minimal, safe
st.markdown(
    '<div class="badge"><span>✦ Enterprise Knowledge Intelligence</span></div>',
    unsafe_allow_html=True
)

# Title: "Intelli" plain + "Docs" gradient span + " AI" plain
# We render this as a centred markdown H1 with one inline span — safe
st.markdown(
    '<h1>Intelli<span class="grad-word">Docs</span> AI</h1>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="hero-sub">Ask anything. Get precise answers grounded in your enterprise documents.</p>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────
try:
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_model
    )
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    # ── PDF UPLOAD ────────────────────────────────────────────
    st.markdown("### Upload PDF Documents")

    uploaded_files = st.file_uploader(
        "Drop one or more PDFs here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        os.makedirs("uploaded_docs", exist_ok=True)
        all_documents = []

        for uploaded_file in uploaded_files:
            file_path = os.path.join("uploaded_docs", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✓ Uploaded: **{uploaded_file.name}**")

            loader = PyPDFLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["filename"] = uploaded_file.name
            all_documents.extend(docs)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(all_documents)
        st.info(f"Created **{len(chunks)} chunks** from {len(uploaded_files)} file(s)")

        db.add_documents(chunks)
        st.success("Documents added to knowledge base ✓")

    # ── QUESTION INPUT ────────────────────────────────────────
    st.markdown("### Ask a Question")

    question = st.text_input(
        "Question",
        placeholder="e.g. What is the leave policy?",
        label_visibility="collapsed"
    )

    if question:
        with st.spinner("Analyzing enterprise documents..."):
            results = db.similarity_search_with_score(question, k=3)
            context = "\n\n".join([doc.page_content for doc, score in results])

            prompt = f"""You are an enterprise AI assistant.
Answer professionally and clearly using ONLY the context below.
Write in clean readable paragraphs or bullet points.
Do NOT use any HTML tags in your answer.

Context:
{context}

Question:
{question}
"""
            response = llm.invoke(prompt)
            answer = response.content

        # ── AI ANSWER ─────────────────────────────────────────
        # Label as simple safe HTML (no dynamic content injected)
        st.markdown(
            '<div class="answer-label">AI Generated Answer</div>',
            unsafe_allow_html=True
        )
        # Answer rendered by Streamlit's own markdown engine — NEVER injected into HTML
        st.markdown(answer)

        # ── SOURCES ───────────────────────────────────────────
        st.markdown(
            '<div class="src-head">Source Documents</div>',
            unsafe_allow_html=True
        )

        for i, (doc, score) in enumerate(results, 1):
            filename = doc.metadata.get("filename", "Unknown Document")
            excerpt  = " ".join(doc.page_content.split())[:500]

            # Native st.container with border — styled via CSS above
            with st.container(border=True):
                col1, col2 = st.columns([7, 3])
                with col1:
                    st.markdown(f"**📄 {filename}**")
                with col2:
                    st.markdown(
                        f"<p style='text-align:right;color:rgba(80,120,180,0.5);font-size:12px;'>Score: {round(score,3)}</p>",
                        unsafe_allow_html=True
                    )
                st.caption(excerpt)

except Exception as e:
    st.error(f"⚠ System error: {e}")