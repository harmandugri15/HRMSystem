"""
Fireart Studio Exact Light Theme Design System
Complete commercial styling for Landing Page, Pricing Cards, Auth Portals, and Executive Suite.
"""

import plotly.graph_objects as go

FIREART_CSS = """
<script>
    try {
        window.localStorage.setItem("theme", "light");
        window.localStorage.setItem("stActiveTheme", "light");
        document.documentElement.setAttribute("data-theme", "light");
    } catch(e) {}
</script>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap');

    /* Global Canvas */
    html, body, .stApp {
        background-color: #F8F9FA !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        color: #000000 !important;
    }

    /* Force all text elements */
    p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #000000;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E4E4E7 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] label {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        color: #000000 !important;
    }

    /* Fireart Studio Tagline Badge */
    .fireart-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 71, 10, 0.08);
        border: 1px solid rgba(255, 71, 10, 0.35);
        border-radius: 9999px;
        padding: 6px 16px;
        font-size: 0.74rem;
        font-weight: 700;
        color: #FF470A !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 1.2rem;
    }

    .fireart-dot {
        width: 6px;
        height: 6px;
        background-color: #FF470A;
        border-radius: 50%;
        display: inline-block;
    }

    .fireart-hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        line-height: 1.1;
        color: #000000 !important;
        margin-bottom: 0.85rem;
        letter-spacing: -0.035em;
    }

    .fireart-hero-title span {
        color: #FF470A !important;
    }

    .fireart-hero-subtitle {
        font-size: 1.15rem;
        color: #3F3F46 !important;
        line-height: 1.7;
        max-width: 860px;
        margin-bottom: 2.2rem;
        font-weight: 450;
    }

    /* Fireart Bento HTML Card */
    .fireart-card {
        background: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 1.6rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04) !important;
    }

    .fireart-card p,
    .fireart-card span,
    .fireart-card div,
    .fireart-card strong {
        color: #000000 !important;
    }

    .fireart-card h4,
    .fireart-card h3,
    .fireart-card h2 {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    .fireart-card:hover {
        border-color: #FF470A !important;
        box-shadow: 0 12px 30px rgba(255, 71, 10, 0.1) !important;
        transform: translateY(-2px) !important;
    }

    /* Pricing Card Special */
    .pricing-card {
        background: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 18px;
        padding: 2rem;
        position: relative;
        transition: all 0.25s ease;
        height: 100%;
    }
    .pricing-card:hover {
        border-color: #FF470A;
        box-shadow: 0 16px 36px rgba(255, 71, 10, 0.12);
        transform: translateY(-4px);
    }
    .pricing-featured {
        border: 2px solid #FF470A !important;
        box-shadow: 0 12px 32px rgba(255, 71, 10, 0.15) !important;
    }

    /* Native Streamlit Bordered Container Styling */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03) !important;
        margin-bottom: 1rem !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #FF470A !important;
        box-shadow: 0 8px 24px rgba(255, 71, 10, 0.08) !important;
    }

    /* Metric Values */
    .fireart-metric-val {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        color: #000000 !important;
        line-height: 1.15 !important;
        margin-top: 8px !important;
    }

    .fireart-metric-label {
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        color: #52525B !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        margin-top: 6px !important;
    }

    /* Status Pills */
    .pill {
        display: inline-block !important;
        padding: 4px 12px !important;
        border-radius: 9999px !important;
        font-size: 0.74rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }
    .pill-orange { background: rgba(255, 71, 10, 0.12) !important; color: #EA3800 !important; border: 1px solid rgba(255, 71, 10, 0.4) !important; }
    .pill-green { background: rgba(16, 185, 129, 0.12) !important; color: #047857 !important; border: 1px solid rgba(16, 185, 129, 0.4) !important; }
    .pill-blue { background: rgba(37, 99, 235, 0.12) !important; color: #1D4ED8 !important; border: 1px solid rgba(37, 99, 235, 0.4) !important; }
    .pill-gray { background: #F1F5F9 !important; color: #334155 !important; border: 1px solid #CBD5E1 !important; }
    .pill-red { background: rgba(239, 68, 68, 0.12) !important; color: #B91C1C !important; border: 1px solid rgba(239, 68, 68, 0.4) !important; }

    /* Action Button */
    .stButton > button {
        background: #FF470A !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9999px !important;
        padding: 0.75rem 2.4rem !important;
        font-weight: 700 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 18px rgba(255, 71, 10, 0.25) !important;
        transition: all 0.25s ease !important;
    }

    .stButton > button * {
        color: #FFFFFF !important;
    }

    .stButton > button:hover {
        background: #FF561D !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 26px rgba(255, 71, 10, 0.4) !important;
    }

    /* Form Inputs */
    label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] * {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
    }

    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    div[data-baseweb="select"] > div {
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] div,
    ul[role="listbox"],
    ul[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12) !important;
    }

    li[role="option"],
    li[role="option"] div,
    li[role="option"] span,
    ul[role="listbox"] li,
    ul[role="listbox"] li div,
    ul[role="listbox"] li span {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    li[role="option"]:hover,
    li[role="option"]:hover div,
    li[role="option"]:hover span,
    li[aria-selected="true"],
    li[aria-selected="true"] div,
    li[aria-selected="true"] span {
        background-color: #FFF2ED !important;
        background: #FFF2ED !important;
        color: #FF470A !important;
        font-weight: 700 !important;
    }

    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="input"] input,
    input {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    div[data-baseweb="input"] > div {
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }

    div[data-testid="stNumberInput"] button,
    div[data-testid="stNumberInput"] button * {
        background-color: #F4F4F6 !important;
        color: #000000 !important;
        fill: #000000 !important;
    }

    div[data-testid="stSlider"] *,
    div[data-testid="stSlider"] div,
    div[data-testid="stSlider"] span {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMultiSelect"] * {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
    }

    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: #F1F5F9 !important;
        padding: 6px !important;
        border-radius: 14px !important;
        border: 1px solid #CBD5E1 !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        color: #475569 !important;
        padding: 8px 22px !important;
        font-weight: 700 !important;
    }

    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #000000 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        border: 1px solid #CBD5E1 !important;
    }

    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
    }

    [data-testid="stExpander"] * {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    [data-testid="stDataFrame"] {
        background: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #CBD5E1 !important;
    }

    .stAlert {
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    
    .stAlert * {
        color: #000000 !important;
    }
</style>
"""


def apply_fireart_plotly_theme(fig, height=380, title=None):
    """Applies Fireart Studio high-contrast light palette to Plotly figures."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#000000", size=12),
        title=dict(
            text=f"<b>{title.upper()}</b>" if title else "",
            font=dict(family="Space Grotesk, sans-serif", color="#000000", size=14),
            x=0.02,
            y=0.95
        ),
        margin=dict(l=30, r=30, t=50 if title else 25, b=30),
        height=height,
        xaxis=dict(
            gridcolor="#F1F5F9",
            linecolor="#CBD5E1",
            tickfont=dict(color="#000000", size=11)
        ),
        yaxis=dict(
            gridcolor="#F1F5F9",
            linecolor="#CBD5E1",
            tickfont=dict(color="#000000", size=11)
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            font=dict(color="#000000", size=12)
        )
    )
    return fig
