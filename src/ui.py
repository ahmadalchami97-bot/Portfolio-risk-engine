"""
Shared UI utilities: theme CSS, color constants, chart defaults.
Call apply_theme() once at the top of every page.
"""

import streamlit as st

# ── Brand palette ──────────────────────────────────────────────────────────────
POS   = "#059669"   # emerald green  — gains, positive returns
NEG   = "#dc2626"   # rose red       — losses, negative returns
NEU   = "#64748b"   # slate grey     — neutral / zero
ACC   = "#1e3a5f"   # deep navy      — primary accent
LIGHT = "#f8fafc"   # off-white      — card backgrounds
BORDER= "#e2e8f0"   # light border   — card / table borders

# ── Plotly chart defaults ──────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    font=dict(family="Inter, Helvetica Neue, Arial, sans-serif", size=13, color="#1e293b"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(t=32, b=32, l=16, r=16),
    hoverlabel=dict(bgcolor="white", font_size=13, bordercolor=BORDER),
)


def apply_theme() -> None:
    """Inject shared CSS. Call once at the top of every page."""
    st.markdown(
        f"""
        <style>
        /* ── Metric cards ─────────────────────────────────────────── */
        [data-testid="metric-container"] {{
            background-color: {LIGHT};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 1rem 1.25rem;
        }}
        [data-testid="stMetricValue"] {{
            font-size: 1.55rem !important;
            font-weight: 700 !important;
            color: {ACC};
        }}
        [data-testid="stMetricLabel"] {{
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {NEU};
        }}

        /* ── DataFrames ───────────────────────────────────────────── */
        [data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: 8px;
            overflow: hidden;
        }}

        /* ── Section headers ──────────────────────────────────────── */
        h3 {{
            color: {ACC} !important;
            font-weight: 700 !important;
            margin-top: 0.25rem !important;
        }}

        /* ── Info / warning boxes ─────────────────────────────────── */
        [data-testid="stAlert"] {{
            border-radius: 8px;
        }}

        /* ── Sidebar nav ─────────────────────────────────────────── */
        [data-testid="stSidebarNav"] li span {{
            font-size: 0.9rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def color_value(val) -> str:
    """Return CSS style string for positive/negative numeric cells."""
    try:
        f = float(val)
        if f > 0:
            return f"color:{POS}; font-weight:600"
        if f < 0:
            return f"color:{NEG}; font-weight:600"
    except (TypeError, ValueError):
        pass
    return ""


def sign_color(val) -> str:
    """Green for positive, red for negative, grey for zero. The single
    source of truth for gain/loss colouring across the app."""
    try:
        f = float(val)
        if f > 0:
            return POS
        if f < 0:
            return NEG
    except (TypeError, ValueError):
        pass
    return NEU


def sign_arrow(val) -> str:
    """▲ for positive, ▼ for negative, • for zero."""
    try:
        f = float(val)
        if f > 0:
            return "▲"
        if f < 0:
            return "▼"
    except (TypeError, ValueError):
        pass
    return "•"


def kpi_card(label: str, value: str, color: str = ACC, sublabel: str = "") -> str:
    """Return HTML for a KPI card with a colour-controlled value.
    Use with st.markdown(..., unsafe_allow_html=True) inside a column."""
    sub = (
        f"<div style='font-size:0.78rem;color:{NEU};margin-top:2px;'>{sublabel}</div>"
        if sublabel else ""
    )
    return (
        f"<div style='background:{LIGHT};border:1px solid {BORDER};border-radius:10px;"
        f"padding:1rem 1.25rem;'>"
        f"<div style='font-size:0.8rem;font-weight:600;text-transform:uppercase;"
        f"letter-spacing:0.05em;color:{NEU};'>{label}</div>"
        f"<div style='font-size:1.55rem;font-weight:700;color:{color};margin-top:4px;'>{value}</div>"
        f"{sub}"
        f"</div>"
    )


def narrative_box(text: str) -> None:
    """Render a narrative summary in a styled callout box."""
    html = text.replace("\n\n", "<br><br>").replace("\n", " ")
    st.markdown(
        f"""
        <div style="
            background:{LIGHT};
            border-left:4px solid {ACC};
            border-radius:0 8px 8px 0;
            padding:1.1rem 1.4rem;
            line-height:1.75;
            font-size:0.95rem;
            color:#1e293b;
        ">{html}</div>
        """,
        unsafe_allow_html=True,
    )
