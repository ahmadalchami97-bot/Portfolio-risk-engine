import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from src.templates import ASSET_TEMPLATES, BETA_RATIONALE, FACTORS
from src.ui import apply_theme, POS, NEG, ACC, BORDER, LIGHT, CHART_LAYOUT

st.set_page_config(page_title="Assumptions & Methodology", page_icon="📋", layout="wide")
apply_theme()

st.title("📋 Assumptions & Methodology")
st.markdown(
    "This page documents every modeling assumption behind the Portfolio Risk Engine. "
    "Read this before drawing conclusions from scenario results."
)
st.divider()

# ── 1. Model overview ──────────────────────────────────────────────────────────

st.subheader("1. Model Overview")
st.markdown("""
The model uses a **linear single-factor sensitivity approach**:

> **Asset Return (%) = Σ ( Beta_k × Shock_k )**

Where:
- **Beta_k** is the sensitivity of the asset to macro factor *k*
- **Shock_k** is the user-defined change in factor *k*

The portfolio return is the **investment-weighted average** of asset returns.

**What this model is good for:**
- Understanding the *directional* impact of macro changes on a portfolio
- Comparing relative sensitivities across asset classes
- Quickly stress-testing known scenarios (rate hikes, recessions, stagflation)

**What this model does NOT capture:**
- Non-linear or threshold effects (e.g. credit crises, liquidity seizures)
- Interactions between factors (e.g. oil spike *combined with* a rate hike)
- Path dependency (the order in which shocks occur)
- Time dimension (the model is single-period, not a path forecast)
- Fat-tail / tail-risk events beyond the linear range
""")

st.divider()

# ── 2. Beta disclosure ─────────────────────────────────────────────────────────

st.subheader("2. Factor Sensitivity (Beta) Disclosure")

st.error(
    "**All betas in this application are ASSUMED, not statistically estimated.** "
    "They have not been derived from regression analysis, historical data fitting, "
    "or any formal quantitative procedure. They reflect directional consensus from "
    "financial economics literature and institutional practice, adjusted for "
    "plausibility. They should be treated as informed starting points for discussion, "
    "not as precise empirical estimates.",
    icon="⚠️",
)

st.markdown("""
**Beta definition:** % return of the asset per 1 unit of factor shock.

**Shock units:**
| Factor | Shock Unit | Example |
|---|---|---|
| Fed Funds Rate | Percentage points (pp) | +1.0 = Fed hikes 100bps |
| US 10Y Yield | Percentage points (pp) | +0.5 = 10Y yield rises 50bps |
| Inflation (CPI) | Percentage points (pp) | +1.0 = CPI rises from 3% to 4% |
| DXY | % change | +5.0 = dollar strengthens 5% |
| Oil Price (WTI) | % change | +15.0 = oil rises 15% |
""")

st.divider()

# ── 3. Beta table with rationale ───────────────────────────────────────────────

st.subheader("3. Beta Rationale by Asset and Factor")

for asset_name, template in ASSET_TEMPLATES.items():
    icon = template["icon"]
    st.markdown(f"#### {icon} {asset_name} — {template['description']}")

    rationale = BETA_RATIONALE.get(asset_name, {})
    rows = []
    for factor, beta in template["betas"].items():
        rat = rationale.get(factor, ("", "", ""))
        sign_ok, magnitude, explanation = rat
        rows.append({
            "Factor": FACTORS[factor]["icon"] + "  " + factor,
            "Beta": beta,
            "Sign": sign_ok,
            "Magnitude Assessment": magnitude,
            "Economic Rationale": explanation,
        })

    df = pd.DataFrame(rows)

    def _color_beta(val):
        try:
            f = float(val)
            if f > 0: return f"background-color:#dcfce7; color:#166534; font-weight:600"
            if f < 0: return f"background-color:#fee2e2; color:#991b1b; font-weight:600"
        except (TypeError, ValueError):
            pass
        return "color:#64748b"

    styled = df.style.map(_color_beta, subset=["Beta"]).format({"Beta": "{:+.1f}"})
    st.dataframe(styled, width="stretch", hide_index=True)
    st.markdown("")

st.divider()

# ── 4. Beta heatmap (overview) ─────────────────────────────────────────────────

st.subheader("4. Factor Sensitivity Heatmap (All Assets)")
st.caption("Green = positive sensitivity, Red = negative. Intensity reflects magnitude.")

asset_names  = list(ASSET_TEMPLATES.keys())
factor_names = list(FACTORS.keys())
factor_labels = [FACTORS[f]["icon"] + "  " + f for f in factor_names]

matrix = [
    [ASSET_TEMPLATES[a]["betas"].get(f, 0.0) for f in factor_names]
    for a in asset_names
]

annotations = [[f"{v:+.1f}" for v in row] for row in matrix]

fig_hm = go.Figure(go.Heatmap(
    z=matrix,
    x=factor_labels,
    y=asset_names,
    colorscale=[
        [0.0,  "#fca5a5"],
        [0.45, "#ffffff"],
        [0.55, "#ffffff"],
        [1.0,  "#86efac"],
    ],
    zmid=0,
    text=annotations,
    texttemplate="%{text}",
    textfont=dict(size=14, color="#1e293b"),
    colorbar=dict(title="Beta"),
    showscale=True,
))
fig_hm.update_layout(
    **{**CHART_LAYOUT, "height": 280},
    xaxis=dict(title="Macro Factor", tickangle=-15),
    yaxis=dict(title=""),
)
st.plotly_chart(fig_hm, width="stretch")

st.divider()

# ── 5. Key limitations ─────────────────────────────────────────────────────────

st.subheader("5. Key Limitations")

lim_col1, lim_col2 = st.columns(2)

with lim_col1:
    st.markdown("""
**Model limitations:**

- **Linearity** — real asset returns are non-linear. A 500bps shock will not produce
  exactly 5× the impact of a 100bps shock.

- **Factor independence** — the model applies shocks independently. It does not account
  for simultaneous factor interactions (e.g. an oil shock that *also* drives inflation).

- **Compressed bond duration** — the US Treasuries beta to US 10Y Yield (-8.0) is
  deliberately set below true modified duration (~16–17 years for TLT) to avoid
  double-counting rate exposure with the Fed Funds Rate factor. Users should be aware
  that the true interest-rate sensitivity of long bonds is larger.

- **Gold inflation beta** — gold's empirical inflation sensitivity is historically
  unstable: very strong in the 1970s, near zero in the 2010s. The +3.0 beta is a
  moderate assumption. Treat it as directional only.
""")

with lim_col2:
    st.markdown("""
**Data limitations:**

- **No statistical estimation** — betas have not been derived from regression.
  There is no confidence interval, R², or p-value behind any number.

- **No regime sensitivity** — the same beta applies in all market conditions.
  In reality, asset sensitivities change materially across regimes
  (e.g. the equity-bond correlation shifted sharply in 2022).

- **Single asset class per template** — each template (Gold, US Equities, etc.)
  represents the broad asset class. Individual securities within that class
  will differ.

- **Baselines are static** — factor baseline values are illustrative and
  not updated in real time. Adjust your shock interpretation accordingly.

- **No currency hedging modeled** — Swiss Real Estate is treated as an
  unhedged USD position. Hedged returns would differ.
""")

st.divider()

# ── 6. Recommended use ─────────────────────────────────────────────────────────

st.subheader("6. Recommended Use")

st.success("""
**This tool is best used for:**
- Directional stress testing ("what happens to my portfolio if rates rise 100bps?")
- Comparing relative factor exposures across asset classes
- Investment committee scenario discussions
- Educational understanding of macro-asset relationships

**Not appropriate for:**
- Precise P&L forecasting
- Risk capital allocation
- Regulatory VaR or stress testing
- Trading decisions
""")

st.divider()
st.caption(
    "Portfolio Risk Engine — MVP v1. Betas are assumption-based. "
    "Results are for analytical discussion only, not investment advice."
)
