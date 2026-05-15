import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

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
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;600;800&family=Instrument+Sans:wght@300;400;500&display=swap');

/* ── Base ── */
html, body, .stApp {
    background-color: #050C1A !important;
    color: #C8D8F0;
    font-family: 'Instrument Sans', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 960px;
    padding: 2rem 2rem 5rem;
}

/* ── Hero ── */
.hero-wrap { text-align: center; padding: 40px 0 36px; }

.hero-badge {
    display: inline-block;
    background: rgba(56,189,248,0.06);
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 100px;
    padding: 5px 16px;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #38BDF8;
    font-weight: 500;
    margin-bottom: 20px;
}

.hero-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 68px;
    font-weight: 800;
    color: #EFF6FF;
    letter-spacing: -2px;
    line-height: 1.02;
    margin-bottom: 14px;
}

.hero-title .grad {
    background: linear-gradient(90deg, #60A5FA 0%, #38BDF8 50%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 17px;
    color: rgba(140,175,225,0.55);
    margin-bottom: 0;
    line-height: 1.7;
}

/* ── Search input ── */
div[data-testid="stTextInput"] label {
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: rgba(80,120,180,0.5) !important;
}

div[data-testid="stTextInput"] input {
    background: rgba(10,20,50,0.85) !important;
    border: 1px solid rgba(59,130,246,0.30) !important;
    border-radius: 14px !important;
    color: #E2E8F0 !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 15px !important;
    padding: 16px 20px !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: rgba(59,130,246,0.65) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.10) !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: rgba(70,110,170,0.5) !important;
}

/* ── Answer section ── */
.answer-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #3B82F6;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.answer-label::before {
    content: '';
    display: inline-block;
    width: 18px; height: 1px;
    background: #3B82F6;
}

/* Style st.markdown output inside the answer area */
div[data-testid="stMarkdownContainer"] p {
    color: #C8D8F0 !important;
    font-size: 15px !important;
    line-height: 1.82 !important;
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

div[data-testid="stMarkdownContainer"] h1,
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3 {
    color: #E2E8F0 !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
}

/* ── Streamlit container border trick ── */
div[data-testid="stVerticalBlock"] > div:has(.answer-label) {
    background: linear-gradient(140deg, rgba(12,22,48,0.95), rgba(14,26,56,0.92));
    border: 1px solid rgba(59,130,246,0.20);
    border-radius: 20px;
    padding: 28px 32px;
    box-shadow: 0 4px 40px rgba(0,0,0,0.35);
}

/* ── Sources head ── */
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
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.04);
}

/* ── Source cards via st.container ── */
div[data-testid="stVerticalBlock"] > div:has(.src-card-title) {
    background: rgba(10,20,46,0.70);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 18px 22px !important;
    margin-bottom: 10px;
}

.src-card-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: #60A5FA;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.src-score {
    font-size: 11px;
    color: rgba(80,120,180,0.5);
    margin-left: auto;
}

.src-excerpt {
    font-size: 13px;
    color: rgba(100,140,195,0.60);
    line-height: 1.70;
    border-left: 2px solid rgba(59,130,246,0.18);
    padding-left: 12px;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(5,12,28,0.96) !important;
    border-right: 1px solid rgba(40,90,200,0.10) !important;
}
section[data-testid="stSidebar"] * {
    color: rgba(180,210,255,0.65) !important;
}

.sb-logo {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    color: #EFF6FF !important;
    letter-spacing: -0.5px;
}
.sb-logo .acc { color: #38BDF8 !important; }

.sb-live {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(16,185,129,0.07);
    border: 1px solid rgba(16,185,129,0.18);
    border-radius: 8px;
    padding: 9px 13px;
    font-size: 12px;
    color: #34D399 !important;
    font-weight: 500;
    margin: 14px 0 20px;
}
.sb-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #34D399;
    box-shadow: 0 0 7px rgba(52,211,153,0.8);
    flex-shrink: 0;
    animation: blink 2s infinite;
}
@keyframes blink {
    0%,100% { opacity:1; }
    50% { opacity:0.4; }
}

.sb-cap {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: rgba(60,100,160,0.45) !important;
    margin: 16px 0 6px !important;
}

.sb-feat {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 7px;
    font-size: 13px;
    color: rgba(140,180,240,0.55) !important;
}
.sb-feat-dot {
    width: 4px; height: 4px;
    border-radius: 50%;
    background: #3B82F6;
    flex-shrink: 0;
}

.sb-model {
    background: linear-gradient(135deg, rgba(29,78,216,0.12), rgba(14,165,233,0.07));
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 11px;
    padding: 13px 16px;
    text-align: center;
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: #60A5FA !important;
    margin-top: 6px;
}
.sb-model-sub {
    font-family: 'Instrument Sans', sans-serif;
    font-size: 11px;
    color: rgba(80,120,180,0.5) !important;
    margin-top: 2px;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-weight: 400;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #38BDF8 !important; }

/* ── Alert ── */
.stAlert {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.20) !important;
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-logo">✦ Intelli<span class="acc">Docs</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-live"><div class="sb-dot"></div>Gemini 2.5 Flash — Live</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-cap">Capabilities</div>', unsafe_allow_html=True)
    for f in ["PDF Processing","Smart Chunking","HuggingFace Embeddings",
              "Chroma Vector Database","Semantic Search","Gemini AI Answers","Source Citation"]:
        st.markdown(f'<div class="sb-feat"><div class="sb-feat-dot"></div>{f}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-cap" style="margin-top:20px;">Active Model</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-model">gemini-2.5-flash<div class="sb-model-sub">Google DeepMind</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">✦ Enterprise Knowledge Intelligence</div>
    <div class="hero-title">Intelli<span class="grad">Docs</span> AI</div>
    <div class="hero-sub">Ask anything. Get precise answers grounded in your enterprise documents.</div>
</div>
""", unsafe_allow_html=True)

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
Write in clean paragraphs. Use bullet points only when listing items.
Do NOT output any HTML tags.

Context:
{context}

Question:
{question}
"""
            response = llm.invoke(prompt)
            clean_response = response.content

        # ── AI ANSWER ──
        # Use st.container so Streamlit renders markdown properly inside it
        with st.container():
            # Label rendered as HTML (simple, safe single-div)
            st.markdown('<div class="answer-label">AI Generated Answer</div>', unsafe_allow_html=True)
            # Answer rendered by Streamlit markdown engine — NO HTML injection
            st.markdown(clean_response)

        # ── SOURCES ──
        st.markdown('<div class="src-head">Source Documents</div>', unsafe_allow_html=True)

        for i, (doc, score) in enumerate(results, 1):
            filename = doc.metadata.get("filename", "Unknown Document")
            excerpt  = " ".join(doc.page_content.split())[:500]

            # Each source is a native st.container — CSS targets it via :has()
            with st.container():
                # Title row: filename + score using columns
                col1, col2 = st.columns([8, 2])
                with col1:
                    st.markdown(
                        f'<div class="src-card-title">📄 &nbsp;{filename}</div>',
                        unsafe_allow_html=True
                    )
                with col2:
                    st.markdown(
                        f'<div class="src-score">Score: {round(score, 3)}</div>',
                        unsafe_allow_html=True
                    )
                # Excerpt rendered as plain markdown text (no HTML injection)
                st.caption(excerpt)

except Exception as e:
    st.error(f"⚠ System error: {e}")