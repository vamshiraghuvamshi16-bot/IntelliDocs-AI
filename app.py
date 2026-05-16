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

html, body, .stApp {
    background-color: #080E1F !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #C7D9F5 !important;
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 75% 55% at 50% -5%, rgba(37,99,235,0.38) 0%, transparent 65%),
        radial-gradient(ellipse 45% 35% at 5%  85%, rgba(29,78,216,0.20) 0%, transparent 55%),
        radial-gradient(ellipse 40% 30% at 95% 75%, rgba(59,130,246,0.14) 0%, transparent 55%);
    pointer-events: none;
    z-index: 0;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 860px !important;
    padding: 0 2rem 6rem !important;
    position: relative;
    z-index: 1;
}

/* ══ SIDEBAR ══════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(170deg, #060C1C 0%, #0A1228 100%) !important;
    border-right: 1px solid rgba(37,99,235,0.20) !important;
}
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 220px;
    background: radial-gradient(ellipse at 50% 0%, rgba(37,99,235,0.18) 0%, transparent 70%);
    pointer-events: none;
}
section[data-testid="stSidebar"] * { color: #C7D9F5 !important; }
section[data-testid="stSidebar"] .stSuccess > div {
    background: rgba(37,99,235,0.12) !important;
    border: 1px solid rgba(59,130,246,0.30) !important;
    border-radius: 12px !important;
    color: #93C5FD !important;
}

/* ══ MODEL SELECTBOX ══════════════════════════════════════ */
div[data-testid="stSelectbox"] label {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    color: #60A5FA !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: rgba(8,14,31,0.85) !important;
    border: 1px solid rgba(59,130,246,0.35) !important;
    border-radius: 50px !important;
    color: #E0EEFF !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    box-shadow: 0 0 24px rgba(37,99,235,0.15), inset 0 1px 0 rgba(255,255,255,0.04) !important;
    transition: all 0.25s;
}
div[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(96,165,250,0.70) !important;
    box-shadow: 0 0 36px rgba(37,99,235,0.30) !important;
}

/* ══ HERO ═════════════════════════════════════════════════ */
.hero-wrap {
    text-align: center;
    padding: 3.5rem 0 2rem;
    position: relative;
}
.hero-orb {
    width: 54px; height: 54px;
    background: linear-gradient(135deg, #2563EB 0%, #60A5FA 100%);
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin-bottom: 28px;
    box-shadow:
        0 0 0 8px rgba(37,99,235,0.12),
        0 0 0 18px rgba(37,99,235,0.06),
        0 0 60px rgba(37,99,235,0.50);
    animation: orb-float 3s ease-in-out infinite;
}
@keyframes orb-float {
    0%, 100% { transform: translateY(0px);   box-shadow: 0 0 0 8px rgba(37,99,235,0.12), 0 0 0 18px rgba(37,99,235,0.06), 0 0 60px rgba(37,99,235,0.50); }
    50%       { transform: translateY(-8px);  box-shadow: 0 0 0 10px rgba(37,99,235,0.10), 0 0 0 22px rgba(37,99,235,0.05), 0 0 80px rgba(37,99,235,0.60); }
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(52px, 9vw, 88px);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -3px;
    color: #EFF6FF;
    margin-bottom: 18px;
}
.hero-title .shine {
    background: linear-gradient(135deg, #93C5FD 0%, #3B82F6 40%, #BFDBFE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 16px;
    color: rgba(199,217,245,0.55);
    max-width: 420px;
    margin: 0 auto 2.5rem;
    line-height: 1.65;
}
.badge-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 32px;
}
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(37,99,235,0.10);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 100px;
    padding: 5px 14px;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #93C5FD;
    font-weight: 600;
}
.live-dot {
    width: 5px; height: 5px;
    background: #34D399;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 6px #34D399;
    animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ══ STATS ROW ════════════════════════════════════════════ */
.stats-row {
    display: flex;
    gap: 1px;
    background: rgba(37,99,235,0.12);
    border: 1px solid rgba(37,99,235,0.18);
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 2.5rem;
}
.stat-item {
    flex: 1;
    padding: 20px 16px;
    background: rgba(8,14,31,0.70);
    text-align: center;
    backdrop-filter: blur(10px);
}
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #EFF6FF;
    letter-spacing: -0.5px;
}
.stat-label {
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(147,197,253,0.50);
    margin-top: 3px;
}

/* ══ SECTION HEADS ════════════════════════════════════════ */
.sec-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2.2rem 0 1rem;
}
.sec-line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(37,99,235,0.30), transparent);
}
.sec-text {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #60A5FA;
}

/* ══ FILE UPLOADER ════════════════════════════════════════ */
div[data-testid="stFileUploader"] {
    background: rgba(8,14,31,0.60) !important;
    border: 1.5px dashed rgba(59,130,246,0.28) !important;
    border-radius: 18px !important;
    transition: all 0.3s;
}
div[data-testid="stFileUploader"]:hover {
    border-color: rgba(96,165,250,0.55) !important;
    background: rgba(37,99,235,0.04) !important;
    box-shadow: 0 0 40px rgba(37,99,235,0.10) !important;
}

/* ══ TEXT INPUT ═══════════════════════════════════════════ */
div[data-testid="stTextInput"] input {
    background: rgba(8,14,31,0.80) !important;
    border: 1px solid rgba(59,130,246,0.22) !important;
    border-radius: 50px !important;
    color: #E0EEFF !important;
    padding: 18px 26px !important;
    font-size: 15px !important;
    box-shadow: 0 0 0 0 rgba(37,99,235,0), inset 0 1px 0 rgba(255,255,255,0.03) !important;
    transition: all 0.3s;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(96,165,250,0.55) !important;
    box-shadow: 0 0 0 4px rgba(37,99,235,0.12), 0 0 40px rgba(37,99,235,0.15) !important;
}
div[data-testid="stTextInput"] input::placeholder { color: rgba(147,197,253,0.35) !important; }

/* ══ ANSWER BLOCK ═════════════════════════════════════════ */
.answer-box {
    background: linear-gradient(135deg, rgba(8,14,31,0.92) 0%, rgba(10,18,38,0.92) 100%);
    border: 1px solid rgba(59,130,246,0.20);
    border-radius: 20px;
    padding: 28px 32px 24px;
    margin-top: 18px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 60px rgba(37,99,235,0.08);
}
.answer-box::before {
    content:'';
    position:absolute; top:0; left:0; right:0; height:1px;
    background: linear-gradient(90deg, transparent, #3B82F6, transparent);
}
.answer-box::after {
    content:'';
    position:absolute; bottom:0; right:0;
    width:160px; height:160px;
    background: radial-gradient(circle, rgba(37,99,235,0.08) 0%, transparent 70%);
    pointer-events:none;
}
.answer-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #60A5FA;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.answer-tag::after {
    content:''; flex:1; height:1px;
    background: rgba(37,99,235,0.20);
}

/* ══ SOURCE CARDS ═════════════════════════════════════════ */
.src-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(147,197,253,0.40);
    margin: 2rem 0 0.8rem;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(8,14,31,0.65) !important;
    border: 1px solid rgba(37,99,235,0.18) !important;
    border-radius: 14px !important;
    transition: all 0.2s;
    box-shadow: none !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    border-color: rgba(96,165,250,0.35) !important;
    box-shadow: 0 0 30px rgba(37,99,235,0.08) !important;
}

/* glowing submit / spinner */
div[data-testid="stSpinner"] { color: #60A5FA !important; }
</style>
""", unsafe_allow_html=True)

# ── MODEL SWITCHER TOP-RIGHT ──────────────────────────────
col_gap, col_model = st.columns([5, 1])
with col_model:
    model_choice = st.selectbox(
        "🤖 Model",
        ["Groq Llama 3", "Gemini 2.5 Flash"],
        label_visibility="visible"
    )

# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✦ IntelliDocs")
    st.markdown("<p style='font-size:12px;color:rgba(147,197,253,0.45);margin-top:-6px;margin-bottom:18px;'>Enterprise Knowledge AI</p>", unsafe_allow_html=True)
    st.divider()
    if model_choice == "Groq Llama 3":
        st.success("⚡ Groq Llama 3 — Active")
    else:
        st.info("✦ Gemini 2.5 Flash — Active")
    st.divider()
    st.markdown("<p style='font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:rgba(96,165,250,0.70);margin-bottom:10px;'>Capabilities</p>", unsafe_allow_html=True)
    st.markdown("""
- ✦ Multi-PDF Ingestion
- ✦ Smart Chunking
- ✦ Vector Embeddings
- ✦ Semantic Search
- ✦ Cited AI Answers
- ✦ Dual Model Support
""")
    st.divider()
    st.markdown("<p style='font-size:10px;color:rgba(147,197,253,0.30);text-align:center;'>LangChain · ChromaDB · HuggingFace</p>", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-orb">✦</div>
    <div class="hero-title">
        Intelli<span class="shine">Docs</span> AI
    </div>
    <div class="hero-sub">
        Upload your documents. Ask anything.<br>Get precise, cited answers — instantly.
    </div>
    <div class="badge-row">
        <div class="badge-pill"><span class="live-dot"></span> Live System</div>
        <div class="badge-pill">✦ Enterprise Grade</div>
        <div class="badge-pill">⚡ Dual AI Models</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── STATS ─────────────────────────────────────────────────
st.markdown("""
<div class="stats-row">
    <div class="stat-item"><div class="stat-num">MiniLM</div><div class="stat-label">Embeddings</div></div>
    <div class="stat-item"><div class="stat-num">300</div><div class="stat-label">Chunk Size</div></div>
    <div class="stat-item"><div class="stat-num">ChromaDB</div><div class="stat-label">Vector Store</div></div>
    <div class="stat-item"><div class="stat-num">Top-3</div><div class="stat-label">Retrieval</div></div>
    <div class="stat-item"><div class="stat-num">2 AI</div><div class="stat-label">Models</div></div>
</div>
""", unsafe_allow_html=True)

# ── IMPORTS ───────────────────────────────────────────────
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

# ── MAIN ──────────────────────────────────────────────────
try:
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = None
    if os.path.exists(DB_PATH):
        db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_model)

    if model_choice == "Gemini 2.5 Flash":
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", temperature=0,
            google_api_key=st.secrets["GOOGLE_API_KEY"]
        )
    else:
        llm = ChatGroq(
            groq_api_key=st.secrets["GROQ_API_KEY"],
            model_name="llama-3.1-8b-instant", temperature=0
        )

    # PDF UPLOAD
    st.markdown('<div class="sec-head"><span class="sec-text">📄 Upload Documents</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Drop PDFs", type=["pdf"],
        accept_multiple_files=True, label_visibility="collapsed"
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
        st.info(f"⚡ {len(chunks)} chunks ready from {len(uploaded_files)} file(s)")
        uploaded_db = Chroma.from_documents(
            documents=chunks, embedding=embedding_model,
            persist_directory="uploaded_vector_db"
        )

    # QUESTION
    st.markdown('<div class="sec-head"><div class="sec-line" style="background:linear-gradient(90deg,transparent,rgba(37,99,235,0.30));"></div><span class="sec-text">💬 Ask Anything</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    question = st.text_input(
        "Q", placeholder="e.g.  What is the refund policy?  ·  Summarize section 3...",
        label_visibility="collapsed"
    )

    if question:
        if uploaded_db is None and db is None:
            st.warning("⚠ Please upload a PDF first.")
        else:
            with st.spinner("Searching knowledge base..."):
                results = uploaded_db.similarity_search_with_score(question, k=3) if uploaded_db else db.similarity_search_with_score(question, k=3)
                context = "\n\n".join([doc.page_content for doc, _ in results])
                prompt = f"""You are an enterprise AI assistant.
Answer professionally and clearly using ONLY the context below.
Write in readable paragraphs or bullet points. Do NOT use HTML tags.

Context:
{context}

Question:
{question}"""
                response = llm.invoke(prompt)
                answer = response.content

            st.markdown('<div class="answer-box"><div class="answer-tag">✦ AI Answer</div>', unsafe_allow_html=True)
            st.markdown(answer)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="src-label">↳ Source References</div>', unsafe_allow_html=True)
            for i, (doc, score) in enumerate(results, 1):
                filename = doc.metadata.get("filename", "Unknown")
                excerpt = " ".join(doc.page_content.split())[:380]
                with st.container(border=True):
                    c1, c2 = st.columns([7, 3])
                    with c1:
                        st.markdown(f"**📄 {filename}**")
                    with c2:
                        pct = round((1 - score) * 100 if score <= 1 else 100 / score, 1)
                        st.markdown(f"<p style='text-align:right;color:rgba(96,165,250,0.6);font-size:12px;font-weight:600;'>{pct}% match</p>", unsafe_allow_html=True)
                    st.caption(excerpt)

except Exception as e:
    st.error(f"⚠ System error: {e}")
    st.code(traceback.format_exc())
