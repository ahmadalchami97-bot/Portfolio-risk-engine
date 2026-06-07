import streamlit as st
import pandas as pd

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

st.markdown(
    "This tool estimates how a portfolio may react under different macroeconomic scenarios.\n\n"
    "The model uses a set of assumed economic sensitivities for each asset class. "
    "These sensitivities are based on commonly observed market relationships and are intended "
    "for scenario analysis rather than forecasting.\n\n"
    "Results should be interpreted as directional estimates of potential portfolio impact "
    "under the selected macro environment."
)

st.markdown("#### How to Read the Table")
st.markdown(
    "Each number below represents the estimated percentage impact on an asset for a "
    "one-unit change in the corresponding macro factor.\n\n"
    "**Examples:**\n\n"
    "- Gold / Fed Funds = **−2.0** means a 1.0 percentage point increase in the Fed Funds Rate "
    "is assumed to reduce Gold by approximately 2.0%.\n"
    "- Gold / Inflation = **+3.0** means a 1.0 percentage point increase in Inflation "
    "is assumed to increase Gold by approximately 3.0%.\n"
    "- Gold / DXY = **−0.8** means a 1% increase in the US Dollar Index "
    "is assumed to reduce Gold by approximately 0.8%.\n\n"
    "Positive values indicate the asset generally benefits when that factor rises.  \n"
    "Negative values indicate the asset generally faces headwinds when that factor rises."
)

_sensitivity_data = {
    "Asset Class":                         ["🥇 Gold", "📈 US Equities", "🏛️ US Treasuries", "🏠 Swiss Real Estate"],
    "Fed Funds\n(% per +1.0pp)":           [-2.0, -3.0, -5.0, -1.5],
    "US 10Y Yield\n(% per +1.0pp)":        [-3.0, -2.0, -8.0, -3.0],
    "Inflation\n(% per +1.0pp)":           [+3.0, -1.5, -3.0, +2.0],
    "DXY\n(% per +1%)":                    [-0.8, -0.3, +0.1, -0.5],
    "Oil\n(% per +1%)":                    [+0.3, +0.2, -0.1,  0.0],
}

_sens_df = pd.DataFrame(_sensitivity_data)

def _color_sens(val):
    try:
        f = float(val)
        if f > 0: return "color:#059669; font-weight:600"
        if f < 0: return "color:#dc2626; font-weight:600"
    except (TypeError, ValueError):
        pass
    return ""

_numeric_cols = [c for c in _sens_df.columns if c != "Asset Class"]
_styled_sens = _sens_df.style.map(_color_sens, subset=_numeric_cols).format(
    {c: "{:+.1f}" for c in _numeric_cols}
)
st.dataframe(_styled_sens, width="stretch", hide_index=True)

st.markdown("#### Important Note")
st.warning(
    "These sensitivities are assumptions used for scenario analysis.\n\n"
    "They are economically motivated and intended to reflect typical market behaviour, "
    "but they are not statistically estimated from historical data and should not be "
    "interpreted as forecasts or precise market betas.\n\n"
    "Actual market outcomes may differ, particularly during unusual market environments "
    "or periods when historical relationships break down.",
    icon="⚠️",
)
st.page_link("pages/5_Assumptions.py", label="📋 View Assumptions & Methodology →")
