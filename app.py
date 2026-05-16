import streamlit as st
import os
import traceback

DB_PATH = "vector_db"

st.set_page_config(
    page_title="IntelliDocs AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:        #020812;
    --bg2:       #060f20;
    --border:    rgba(56,189,248,0.12);
    --accent:    #38BDF8;
    --accent2:   #818CF8;
    --accent3:   #34D399;
    --text:      #CBD5E1;
    --text-dim:  rgba(148,163,184,0.55);
    --glow:      rgba(56,189,248,0.18);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, .stApp {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
}

/* animated mesh background */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 0%, rgba(56,189,248,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(129,140,248,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 60% 40%, rgba(52,211,153,0.04) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 900px !important;
    padding: 0 2rem 6rem !important;
    position: relative;
    z-index: 1;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #040c1c 0%, #060f20 100%) !important;
    border-right: 1px solid var(--border) !important;
    position: relative;
}
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 200px;
    background: radial-gradient(ellipse at 50% 0%, rgba(56,189,248,0.10) 0%, transparent 70%);
    pointer-events: none;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    color: #F0F9FF !important;
    letter-spacing: -0.5px !important;
}
section[data-testid="stSidebar"] .stSuccess {
    background: rgba(52,211,153,0.08) !important;
    border: 1px solid rgba(52,211,153,0.25) !important;
    border-radius: 10px !important;
}

/* ── TOP-RIGHT MODEL PILL ── */
div[data-testid="stSelectbox"] > label {
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--accent) !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: rgba(6,15,32,0.9) !important;
    border: 1px solid rgba(56,189,248,0.30) !important;
    border-radius: 50px !important;
    color: #E2E8F0 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 4px 14px !important;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 20px rgba(56,189,248,0.08), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: all 0.2s;
}
div[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(56,189,248,0.6) !important;
    box-shadow: 0 0 30px rgba(56,189,248,0.15) !important;
}

/* ── HERO ── */
.hero-wrap {
    text-align: center;
    padding: 3rem 0 2.5rem;
    position: relative;
}
.hero-wrap::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 500px; height: 200px;
    background: radial-gradient(ellipse, rgba(56,189,248,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56,189,248,0.05);
    border: 1px solid rgba(56,189,248,0.20);
    border-radius: 100px;
    padding: 5px 16px;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 24px;
    font-weight: 600;
}
.badge-dot {
    width: 5px; height: 5px;
    background: var(--accent3);
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 6px var(--accent3);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(48px, 8vw, 80px);
    font-weight: 800;
    line-height: 1;
    letter-spacing: -3px;
    color: #F0F9FF;
    margin-bottom: 16px;
}
.hero-title .g1 {
    background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #34D399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 16px;
    color: var(--text-dim);
    max-width: 440px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── STATS ROW ── */
.stats-row {
    display: flex;
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    margin: 2rem 0;
}
.stat-item {
    flex: 1;
    padding: 18px 20px;
    background: rgba(6,15,32,0.6);
    text-align: center;
    backdrop-filter: blur(8px);
}
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #F0F9FF;
    letter-spacing: -1px;
}
.stat-label {
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-top: 2px;
}

/* ── SECTION HEADINGS ── */
.section-head {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 2rem 0 1rem;
}
.section-head-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border), transparent);
}
.section-head-text {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
}

/* ── UPLOAD AREA ── */
div[data-testid="stFileUploader"] {
    background: rgba(6,15,32,0.5) !important;
    border: 1px dashed rgba(56,189,248,0.25) !important;
    border-radius: 16px !important;
    padding: 8px !important;
    transition: all 0.3s;
}
div[data-testid="stFileUploader"]:hover {
    border-color: rgba(56,189,248,0.5) !important;
    background: rgba(56,189,248,0.03) !important;
}

/* ── TEXT INPUT ── */
div[data-testid="stTextInput"] input {
    background: rgba(6,15,32,0.8) !important;
    border: 1px solid rgba(56,189,248,0.20) !important;
    border-radius: 14px !important;
    color: #E2E8F0 !important;
    padding: 18px 22px !important;
    font-size: 15px !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.3s;
    box-shadow: 0 0 0 0 rgba(56,189,248,0);
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(56,189,248,0.5) !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.08) !important;
}
div[data-testid="stTextInput"] input::placeholder { color: rgba(148,163,184,0.4) !important; }

/* ── ANSWER BLOCK ── */
.answer-wrap {
    background: linear-gradient(135deg, rgba(6,15,32,0.9) 0%, rgba(8,18,36,0.9) 100%);
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 20px;
    padding: 28px 32px;
    margin-top: 20px;
    position: relative;
    overflow: hidden;
}
.answer-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}
.answer-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.answer-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── SOURCE CARDS ── */
.src-head {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-dim);
    margin: 32px 0 14px;
}
div[data-testid="stContainer"] {
    background: rgba(6,15,32,0.6) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    transition: all 0.2s;
}
div[data-testid="stContainer"]:hover {
    border-color: rgba(56,189,248,0.25) !important;
    background: rgba(56,189,248,0.02) !important;
}

/* ── SUCCESS / INFO / WARNING ── */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TOP-RIGHT MODEL SWITCHER
# ─────────────────────────────────────────────────────────────
col_gap, col_model = st.columns([5, 1])
with col_model:
    model_choice = st.selectbox(
        "🤖 Model",
        ["Groq Llama 3", "Gemini 2.5 Flash"],
        label_visibility="visible"
    )

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✦ IntelliDocs")
    st.markdown("<p style='font-size:12px;color:rgba(148,163,184,0.5);margin-top:-8px;margin-bottom:16px;'>Enterprise Knowledge Intelligence</p>", unsafe_allow_html=True)
    st.divider()

    # Active model badge
    if model_choice == "Groq Llama 3":
        st.success("⚡ Groq Llama 3 Active")
    else:
        st.info("✦ Gemini 2.5 Flash Active")

    st.divider()
    st.markdown("<p style='font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:rgba(56,189,248,0.7);'>Capabilities</p>", unsafe_allow_html=True)
    st.markdown("""
- ✦ Multi-PDF Ingestion
- ✦ Smart Chunking
- ✦ Vector Embeddings
- ✦ Semantic Search
- ✦ Cited AI Answers
- ✦ Dual Model Support
""")
    st.divider()
    st.markdown("<p style='font-size:10px;color:rgba(148,163,184,0.4);text-align:center;'>Built with LangChain + ChromaDB</p>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="badge-pill">
        <span class="badge-dot"></span>
        Enterprise Knowledge Intelligence
    </div>
    <div class="hero-title">
        Intelli<span class="g1">Docs</span> AI
    </div>
    <div class="hero-sub">
        Upload your documents. Ask anything.<br>Get precise, cited answers in seconds.
    </div>
</div>
""", unsafe_allow_html=True)

# ── STATS ROW ──
st.markdown("""
<div class="stats-row">
    <div class="stat-item">
        <div class="stat-num">300</div>
        <div class="stat-label">Chunk Size</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">MiniLM</div>
        <div class="stat-label">Embeddings</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">ChromaDB</div>
        <div class="stat-label">Vector Store</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">Top-3</div>
        <div class="stat-label">Retrieval</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception as e:
    st.error(f"⚠ Import error: {e}")
    st.code(traceback.format_exc())
    st.stop()

# ─────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────
try:
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = None
    if os.path.exists(DB_PATH):
        db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_model)

    if model_choice == "Gemini 2.5 Flash":
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=st.secrets["GOOGLE_API_KEY"]
        )
    else:
        llm = ChatGroq(
            groq_api_key=st.secrets["GROQ_API_KEY"],
            model_name="llama-3.1-8b-instant",
            temperature=0
        )

    # ── PDF UPLOAD ──
    st.markdown("""
    <div class="section-head">
        <span class="section-head-text">📄 Upload Documents</span>
        <div class="section-head-line"></div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop PDFs here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    uploaded_db = None

    if uploaded_files:
        os.makedirs("uploaded_docs", exist_ok=True)
        all_documents = []

        for uploaded_file in uploaded_files:
            file_path = os.path.join("uploaded_docs", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✦ Indexed: {uploaded_file.name}")
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["filename"] = uploaded_file.name
            all_documents.extend(docs)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300, chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(all_documents)
        st.info(f"⚡ {len(chunks)} chunks created from {len(uploaded_files)} file(s) — ready to query")

        uploaded_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory="uploaded_vector_db"
        )

    # ── QUESTION ──
    st.markdown("""
    <div class="section-head">
        <span class="section-head-text">💬 Ask a Question</span>
        <div class="section-head-line"></div>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_input(
        "Question",
        placeholder="e.g. What is the refund policy? Summarize section 3...",
        label_visibility="collapsed"
    )

    if question:
        if uploaded_db is None and db is None:
            st.warning("⚠ Please upload a PDF document first.")
        else:
            with st.spinner("Searching knowledge base..."):
                if uploaded_db:
                    results = uploaded_db.similarity_search_with_score(question, k=3)
                else:
                    results = db.similarity_search_with_score(question, k=3)

                context = "\n\n".join([doc.page_content for doc, score in results])
                prompt = f"""You are an enterprise AI assistant.
Answer professionally and clearly using ONLY the context below.
Write in readable paragraphs or bullet points.
Do NOT use HTML tags.

Context:
{context}

Question:
{question}"""
                response = llm.invoke(prompt)
                answer = response.content

            # ANSWER
            st.markdown('<div class="answer-wrap"><div class="answer-label">✦ AI Answer</div>', unsafe_allow_html=True)
            st.markdown(answer)
            st.markdown('</div>', unsafe_allow_html=True)

            # SOURCES
            st.markdown('<div class="src-head">↳ Source References</div>', unsafe_allow_html=True)

            for i, (doc, score) in enumerate(results, 1):
                filename = doc.metadata.get("filename", "Unknown Document")
                excerpt = " ".join(doc.page_content.split())[:400]
                with st.container(border=True):
                    col1, col2 = st.columns([7, 3])
                    with col1:
                        st.markdown(f"**📄 {filename}**")
                    with col2:
                        st.markdown(
                            f"<p style='text-align:right;color:rgba(56,189,248,0.5);font-size:12px;font-weight:600;'>match {round((1-score)*100 if score<=1 else 100/score, 1)}%</p>",
                            unsafe_allow_html=True
                        )
                    st.caption(excerpt)

except Exception as e:
    st.error(f"⚠ System error: {e}")
    st.code(traceback.format_exc())
