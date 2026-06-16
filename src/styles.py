from __future__ import annotations


def dashboard_css() -> str:
    """Return Streamlit CSS inspired by the public Gemüsegärtner website."""

    return """
    <style>
    :root {
        --gg-green: #4f7f3b;
        --gg-green-dark: #26351f;
        --gg-leaf: #779d45;
        --gg-carrot: #d97732;
        --gg-cream: #fffaf0;
        --gg-paper: #ffffff;
        --gg-line: #eadcc4;
    }
    .stApp {
        background: var(--gg-cream);
        color: var(--gg-green-dark);
    }
    section[data-testid="stSidebar"] {
        background: #f3ead6;
        border-right: 1px solid var(--gg-line);
    }
    h1, h2, h3 {
        color: var(--gg-green-dark);
        letter-spacing: 0;
    }
    .hero {
        border-bottom: 1px solid var(--gg-line);
        padding: 1.2rem 0 1.4rem 0;
        margin-bottom: 1rem;
    }
    .hero-eyebrow {
        color: var(--gg-carrot);
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.78rem;
    }
    .hero-title {
        font-size: 2.35rem;
        line-height: 1.1;
        font-weight: 800;
        margin: 0.2rem 0;
    }
    .hero-copy {
        color: #59644c;
        max-width: 780px;
        font-size: 1.02rem;
    }
    div[data-testid="stMetric"] {
        background: var(--gg-paper);
        border: 1px solid var(--gg-line);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 8px 22px rgba(38, 53, 31, 0.06);
    }
    div[data-testid="stMetricValue"] {
        color: var(--gg-green);
    }
    .stButton > button, .stDownloadButton > button {
        background: var(--gg-carrot);
        color: white;
        border: 0;
        border-radius: 6px;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--gg-line);
        border-radius: 8px;
    }
    </style>
    """
