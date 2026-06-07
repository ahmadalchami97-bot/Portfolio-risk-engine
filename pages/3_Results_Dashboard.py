import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.templates import FACTORS
from src.factor_model import compute_results
from src.ui import apply_theme, POS, NEG, ACC, BORDER, LIGHT, CHART_LAYOUT

st.set_page_config(page_title="Results Dashboard", page_icon="📈", layout="wide")
apply_theme()

# ── Session state ──────────────────────────────────────────────────────────────

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
if "scenario" not in st.session_state:
    st.session_state.scenario = {f: 0.0 for f in FACTORS}

# ── Header ─────────────────────────────────────────────────────────────────────

st.title("📈 Results Dashboard")
st.markdown(
    "Estimated portfolio impact under the active macro scenario, "
    "computed using the pre-defined factor sensitivity model."
)
st.divider()

# ── Guards ─────────────────────────────────────────────────────────────────────

if not st.session_state.portfolio:
    st.warning("No portfolio defined — please build your portfolio first.")
    st.page_link("pages/1_Portfolio_Builder.py", label="← Go to Portfolio Builder")
    st.stop()

active_shocks = {f: v for f, v in st.session_state.scenario.items() if abs(v) > 0.001}
if not active_shocks:
    st.warning("No macro shocks are active — all factors are set to zero.")
    st.page_link("pages/2_Scenario_Builder.py", label="← Go to Scenario Builder")
    st.stop()

# ── Compute ────────────────────────────────────────────────────────────────────

results_df, summary, factor_contribs = compute_results(
    st.session_state.portfolio,
    st.session_state.scenario,
)

if results_df is None:
    st.error("Could not compute results. Check portfolio and scenario inputs.")
    st.stop()

total_invested   = summary["total_invested"]
total_pnl        = summary["total_pnl"]
total_return_pct = summary["total_return_pct"]
ending_value     = summary["ending_value"]
is_gain          = total_pnl >= 0

# ── Portfolio KPIs ──────────────────────────────────────────────────────────────

st.subheader("Portfolio Summary")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Invested",  f"${total_invested:,.0f}")
k2.metric(
    "Ending Value",
    f"${ending_value:,.0f}",
    delta=f"${total_pnl:+,.0f}",
    delta_color="normal",
)
k3.metric(
    "Portfolio Return",
    f"{total_return_pct:+.2f}%",
    delta_color="off",
)
k4.metric(
    "Portfolio P&L",
    f"${total_pnl:+,.0f}",
    delta_color="off",
)

st.divider()

# ── Asset results table ────────────────────────────────────────────────────────

st.subheader("Asset-Level Results")

display_df = results_df[
    ["Asset", "Asset Class", "Invested ($)", "Weight (%)", "Return (%)", "P&L ($)", "Ending Value ($)"]
].copy()

# Totals row
totals = pd.DataFrame([{
    "Asset":             "PORTFOLIO TOTAL",
    "Asset Class":       "",
    "Invested ($)":      total_invested,
    "Weight (%)":        100.0,
    "Return (%)":        round(total_return_pct, 3),
    "P&L ($)":           round(total_pnl, 2),
    "Ending Value ($)":  round(ending_value, 2),
}])
display_df = pd.concat([display_df, totals], ignore_index=True)

def _color(val):
    try:
        f = float(val)
        if f > 0: return f"color:{POS}; font-weight:600"
        if f < 0: return f"color:{NEG}; font-weight:600"
    except (TypeError, ValueError):
        pass
    return ""

styled = (
    display_df.style
    .map(_color, subset=["Return (%)", "P&L ($)"])
    .format({
        "Invested ($)":     "${:,.0f}",
        "Weight (%)":       "{:.1f}%",
        "Return (%)":       "{:+.2f}%",
        "P&L ($)":          "${:+,.0f}",
        "Ending Value ($)": "${:,.0f}",
    }, na_rep="—")
)
st.dataframe(styled, width="stretch", hide_index=True)

st.divider()

# ── Charts ─────────────────────────────────────────────────────────────────────

col_returns, col_waterfall = st.columns(2)

# Asset returns bar chart
with col_returns:
    st.subheader("Return by Asset")
    rdf = results_df[["Asset", "Return (%)"]].copy()
    rdf["color"] = rdf["Return (%)"].apply(lambda x: POS if x >= 0 else NEG)

    fig_r = go.Figure(go.Bar(
        x=rdf["Return (%)"],
        y=rdf["Asset"],
        orientation="h",
        marker_color=rdf["color"],
        text=rdf["Return (%)"].apply(lambda x: f"{x:+.2f}%"),
        textposition="outside",
        cliponaxis=False,
    ))
    x_pad = max(abs(rdf["Return (%)"]).max() * 0.25, 0.5)
    fig_r.update_layout(
        **{**CHART_LAYOUT, "height": max(300, len(results_df) * 62 + 60)},
        xaxis=dict(
            title="Estimated Return (%)",
            zeroline=True, zerolinewidth=2, zerolinecolor="#94a3b8",
            range=[rdf["Return (%)"].min() - x_pad, rdf["Return (%)"].max() + x_pad],
        ),
        yaxis=dict(title=""),
        showlegend=False,
    )
    st.plotly_chart(fig_r, width="stretch")

# P&L waterfall chart
with col_waterfall:
    st.subheader("P&L Waterfall ($)")
    assets = results_df["Asset"].tolist()
    pnls   = results_df["P&L ($)"].tolist()

    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative"] * len(assets) + ["total"],
        x=assets + ["Total"],
        y=pnls + [total_pnl],
        text=[f"${v:+,.0f}" for v in pnls + [total_pnl]],
        textposition="outside",
        cliponaxis=False,
        connector={"line": {"color": BORDER, "width": 1}},
        increasing={"marker": {"color": POS}},
        decreasing={"marker": {"color": NEG}},
        totals={"marker": {"color": ACC}},
    ))
    fig_wf.update_layout(
        **{**CHART_LAYOUT, "height": max(300, len(results_df) * 62 + 60)},
        yaxis=dict(
            title="P&L ($)",
            zeroline=True, zerolinewidth=2, zerolinecolor="#94a3b8",
            showgrid=True, gridcolor=BORDER,
        ),
        showlegend=False,
    )
    st.plotly_chart(fig_wf, width="stretch")

st.divider()

# ── Active scenario recap ──────────────────────────────────────────────────────

st.subheader("Active Macro Scenario")
st.caption("Shocks applied in this analysis.")

shock_cols = st.columns(min(len(active_shocks), 6))
for i, (factor, shock) in enumerate(active_shocks.items()):
    cfg  = FACTORS[factor]
    sign = "+" if shock >= 0 else ""
    with shock_cols[i % 6]:
        st.metric(
            label=f"{cfg['icon']} {cfg['label']}",
            value=f"{sign}{shock} {cfg['unit']}",
            delta=f"Base: {cfg['baseline_label']}",
            delta_color="off",
        )

st.divider()

col_prev, col_next = st.columns(2)
with col_prev:
    st.page_link("pages/2_Scenario_Builder.py", label="← Adjust Scenario")
with col_next:
    st.page_link("pages/4_Contribution_Analysis.py", label="Continue to Contribution Analysis →")
