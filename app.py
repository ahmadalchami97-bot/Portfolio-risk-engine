import streamlit as st

st.set_page_config(
    page_title="Portfolio Risk Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialise shared session state used by all pages
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

if "scenario" not in st.session_state:
    st.session_state.scenario = {
        "Fed Funds Rate": 0.0,
        "US 10Y Yield":   0.0,
        "Inflation":      0.0,
        "GDP Growth":     0.0,
        "DXY":            0.0,
        "Oil Price":      0.0,
    }

# ── Header ────────────────────────────────────────────────────────────────────

st.title("📊 Portfolio Risk Engine")
st.markdown(
    "**Macro scenario analysis for investment portfolios.** "
    "Build your portfolio, define a macro shock, and instantly see the estimated impact."
)

st.divider()

# ── Workflow guide ─────────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### Step 1")
    st.markdown("**Portfolio Builder**")
    st.markdown(
        "Add your assets using one of the pre-built templates "
        "(Gold, US Equities, Treasuries, Swiss Real Estate) "
        "and enter the amount invested in each."
    )
    st.page_link("pages/1_Portfolio_Builder.py", label="Open Portfolio Builder →")

with col2:
    st.markdown("### Step 2")
    st.markdown("**Scenario Builder**")
    st.markdown(
        "Define a macro scenario by moving sliders for each factor: "
        "Fed Funds Rate, 10Y Yield, Inflation, GDP, DXY, and Oil. "
        "Or load a pre-built scenario template."
    )
    st.page_link("pages/2_Scenario_Builder.py", label="Open Scenario Builder →")

with col3:
    st.markdown("### Step 3")
    st.markdown("**Results Dashboard**")
    st.markdown(
        "See the estimated return, P&L, and ending value for each asset "
        "and the portfolio as a whole."
    )
    st.page_link("pages/3_Results_Dashboard.py", label="Open Results →")

with col4:
    st.markdown("### Step 4")
    st.markdown("**Contribution Analysis**")
    st.markdown(
        "Understand what drove the result: a tornado chart ranks each macro "
        "factor by its impact, and a narrative summary explains the outcome "
        "in plain English."
    )
    st.page_link("pages/4_Contribution_Analysis.py", label="Open Analysis →")

st.divider()

# ── Status panel ───────────────────────────────────────────────────────────────

st.markdown("### Current Status")
status_col1, status_col2 = st.columns(2)

with status_col1:
    n_assets = len(st.session_state.portfolio)
    if n_assets == 0:
        st.warning("No portfolio built yet. Start with Step 1.")
    else:
        total = sum(a["amount"] for a in st.session_state.portfolio)
        st.success(
            f"Portfolio: **{n_assets} asset(s)** — "
            f"Total invested: **${total:,.0f}**"
        )

with status_col2:
    active_shocks = {
        f: v for f, v in st.session_state.scenario.items() if abs(v) > 0
    }
    if not active_shocks:
        st.warning("No scenario defined yet. Continue with Step 2.")
    else:
        shock_labels = []
        for f, v in active_shocks.items():
            sign = "+" if v >= 0 else ""
            shock_labels.append(f"{f}: {sign}{v}")
        st.success("Scenario active: " + " | ".join(shock_labels))

st.divider()

# ── Methodology note ────────────────────────────────────────────────────────────

with st.expander("How does the model work?"):
    st.markdown(
        """
        **Factor Sensitivity Model**

        Each asset has a set of pre-calibrated *factor betas* — numbers that describe
        how sensitive the asset is to each macro variable.

        The formula is simple:

        > **Asset Return (%) = Σ ( Beta_k × Shock_k )**

        Where:
        - **Beta_k** = % return of the asset per 1 unit of change in factor _k_
        - **Shock_k** = the macro change you define in the Scenario Builder

        **Units:**
        - Rate factors (Fed Funds, 10Y Yield, Inflation, GDP): shock is in **percentage points** (pp).
          A shock of `+1.0` means a 1 percentage point increase (e.g. Fed hikes 100bps).
        - Market factors (DXY, Oil): shock is in **percent change** (%).
          A shock of `+10.0` means the index/price rises 10%.

        **Pre-calibrated betas** are based on historical asset-factor relationships
        and institutional consensus. They are intentionally simplified for
        transparency and ease of use.

        **Important limitation:** This is a *linear*, single-period model.
        It does not capture non-linear effects, path dependency, or tail risk.
        Use it for directional intuition, not precise forecasting.
        """
    )
