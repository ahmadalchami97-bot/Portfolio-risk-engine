import streamlit as st

from src.ui import apply_theme, ACC
from src.templates import FACTORS

st.set_page_config(
    page_title="Portfolio Risk Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

# ── Session state ──────────────────────────────────────────────────────────────

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

if "scenario" not in st.session_state:
    st.session_state.scenario = {f: 0.0 for f in FACTORS}

# ── Header ─────────────────────────────────────────────────────────────────────

st.title("📊 Portfolio Risk Engine")
st.markdown(
    "**Macro scenario analysis for investment portfolios.** "
    "Build a portfolio, define a macro shock, and instantly see the estimated impact "
    "on each asset and the portfolio as a whole."
)
st.divider()

# ── Workflow ───────────────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("### Step 1")
    st.markdown("**🏗️ Portfolio Builder**")
    st.markdown(
        "Add assets from four templates: Gold, US Equities, US Treasuries, Swiss Real Estate. "
        "Enter the dollar amount invested in each."
    )
    st.page_link("pages/1_Portfolio_Builder.py", label="Open Portfolio Builder →")

with c2:
    st.markdown("### Step 2")
    st.markdown("**⚙️ Scenario Builder**")
    st.markdown(
        "Set shocks to five macro factors: Fed Funds Rate, US 10Y Yield, Inflation, "
        "DXY, and Oil Price. Or load a pre-built scenario template."
    )
    st.page_link("pages/2_Scenario_Builder.py", label="Open Scenario Builder →")

with c3:
    st.markdown("### Step 3")
    st.markdown("**📈 Results Dashboard**")
    st.markdown(
        "See the estimated return, P&L, and ending value for each asset and the "
        "portfolio total, with bar and waterfall charts."
    )
    st.page_link("pages/3_Results_Dashboard.py", label="Open Results →")

with c4:
    st.markdown("### Step 4")
    st.markdown("**🌪️ Contribution Analysis**")
    st.markdown(
        "Tornado chart, asset×factor heatmap, stacked decomposition, and a plain-English "
        "narrative explaining what drove the result."
    )
    st.page_link("pages/4_Contribution_Analysis.py", label="Open Analysis →")

st.divider()

# ── Status ─────────────────────────────────────────────────────────────────────

st.subheader("Current Session Status")

s1, s2 = st.columns(2)
with s1:
    n = len(st.session_state.portfolio)
    if n == 0:
        st.warning("No portfolio built yet. Start with Step 1.")
    else:
        total = sum(a["amount"] for a in st.session_state.portfolio)
        st.success(f"Portfolio: **{n} asset(s)** — Total invested: **${total:,.0f}**")

with s2:
    active = {f: v for f, v in st.session_state.scenario.items() if abs(v) > 0}
    if not active:
        st.warning("No scenario defined yet. Continue with Step 2.")
    else:
        parts = [f"{f}: {'+' if v >= 0 else ''}{v}" for f, v in active.items()]
        st.success("Scenario active: " + " | ".join(parts))

st.divider()

# ── Model summary ──────────────────────────────────────────────────────────────

st.subheader("How the Analysis Works")

col_model, col_warn = st.columns([3, 2])

with col_model:
    st.markdown(
        "This tool estimates how a portfolio may react to changes in key macroeconomic "
        "variables such as interest rates, inflation, the US dollar, and oil prices. "
        "Each asset class is assigned a set of economic sensitivities based on typical "
        "market behaviour. For example:\n\n"
        "- Gold generally benefits from higher inflation and a weaker US dollar.\n"
        "- Equities typically benefit from lower interest rates.\n"
        "- Long-duration bonds are usually sensitive to changes in yields.\n"
        "- Real estate can be affected by both interest rates and inflation.\n\n"
        "The analysis should be viewed as a scenario-planning tool rather than a forecast."
    )

with col_warn:
    st.warning(
        "**Important:** All factor sensitivities are **assumption-based**, "
        "not statistically estimated from historical data. "
        "Results are directional estimates for analytical discussion — "
        "not investment advice or precise forecasts.\n\n"
        "See the Assumptions & Methodology page for full disclosure.",
        icon="⚠️",
    )
    st.page_link("pages/5_Assumptions.py", label="📋 View Assumptions & Methodology →")
