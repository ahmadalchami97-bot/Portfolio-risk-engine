import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.templates import FACTORS
from src.factor_model import compute_results

st.set_page_config(page_title="Results Dashboard", page_icon="📈", layout="wide")

# ── Session state init ─────────────────────────────────────────────────────────

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

if "scenario" not in st.session_state:
    st.session_state.scenario = {f: 0.0 for f in FACTORS}

# ── Header ─────────────────────────────────────────────────────────────────────

st.title("📈 Results Dashboard")
st.markdown(
    "Estimated portfolio impact under the active macro scenario. "
    "Returns are computed using the pre-calibrated factor sensitivity model."
)
st.divider()

# ── Guard: need portfolio and scenario ────────────────────────────────────────

if not st.session_state.portfolio:
    st.warning("No portfolio found. Please build your portfolio first.")
    st.page_link("pages/1_Portfolio_Builder.py", label="← Go to Portfolio Builder")
    st.stop()

active_shocks = {f: v for f, v in st.session_state.scenario.items() if abs(v) > 0}
if not active_shocks:
    st.warning("No macro scenario is active. All factor shocks are set to zero.")
    st.page_link("pages/2_Scenario_Builder.py", label="← Go to Scenario Builder")
    st.stop()

# ── Compute results ────────────────────────────────────────────────────────────

results_df, portfolio_summary, factor_contributions = compute_results(
    st.session_state.portfolio,
    st.session_state.scenario,
)

if results_df is None:
    st.error("Could not compute results. Check your portfolio and scenario.")
    st.stop()

total_invested = portfolio_summary["total_invested"]
total_pnl = portfolio_summary["total_pnl"]
total_return_pct = portfolio_summary["total_return_pct"]
ending_value = portfolio_summary["ending_value"]

# ── Portfolio-level KPIs ──────────────────────────────────────────────────────

st.subheader("Portfolio Summary")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "Total Invested",
        f"${total_invested:,.0f}",
    )
with kpi2:
    st.metric(
        "Ending Value",
        f"${ending_value:,.0f}",
        delta=f"${total_pnl:+,.0f}",
    )
with kpi3:
    st.metric(
        "Portfolio Return",
        f"{total_return_pct:+.2f}%",
    )
with kpi4:
    st.metric(
        "Portfolio P&L",
        f"${total_pnl:+,.0f}",
    )

st.divider()

# ── Asset-level results table ──────────────────────────────────────────────────

st.subheader("Asset-Level Results")

display_df = results_df[
    ["Asset", "Asset Class", "Invested ($)", "Weight (%)", "Return (%)", "P&L ($)", "Ending Value ($)"]
].copy()

# Append totals row
totals_row = pd.DataFrame(
    [
        {
            "Asset": "PORTFOLIO TOTAL",
            "Asset Class": "",
            "Invested ($)": total_invested,
            "Weight (%)": 100.0,
            "Return (%)": round(total_return_pct, 3),
            "P&L ($)": round(total_pnl, 2),
            "Ending Value ($)": round(ending_value, 2),
        }
    ]
)
display_df = pd.concat([display_df, totals_row], ignore_index=True)

def color_return(val):
    if isinstance(val, (int, float)):
        if val > 0:
            return "color: #2ca02c; font-weight: bold"
        elif val < 0:
            return "color: #d62728; font-weight: bold"
    return ""

styled = display_df.style.applymap(
    color_return, subset=["Return (%)", "P&L ($)"]
).format(
    {
        "Invested ($)": "${:,.0f}",
        "Weight (%)": "{:.1f}%",
        "Return (%)": "{:+.2f}%",
        "P&L ($)": "${:+,.0f}",
        "Ending Value ($)": "${:,.0f}",
    }
)

st.dataframe(styled, use_container_width=True, hide_index=True)

st.divider()

# ── Asset return bar chart ─────────────────────────────────────────────────────

col_bar, col_waterfall = st.columns(2)

with col_bar:
    st.subheader("Return by Asset (%)")

    chart_df = results_df[["Asset", "Return (%)"]].copy()
    chart_df["Color"] = chart_df["Return (%)"].apply(
        lambda x: "#2ca02c" if x >= 0 else "#d62728"
    )

    fig_bar = px.bar(
        chart_df,
        x="Return (%)",
        y="Asset",
        orientation="h",
        color="Color",
        color_discrete_map="identity",
        text=chart_df["Return (%)"].apply(lambda x: f"{x:+.2f}%"),
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        showlegend=False,
        xaxis_title="Estimated Return (%)",
        yaxis_title="",
        margin=dict(t=20, b=20),
        height=max(300, len(results_df) * 60 + 80),
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="black"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_waterfall:
    st.subheader("P&L Breakdown ($)")

    assets = results_df["Asset"].tolist()
    pnls = results_df["P&L ($)"].tolist()
    measures = ["relative"] * len(assets) + ["total"]
    x_labels = assets + ["Portfolio Total"]
    y_vals = pnls + [total_pnl]

    fig_waterfall = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=measures,
            x=x_labels,
            y=y_vals,
            text=[f"${v:+,.0f}" for v in y_vals],
            textposition="outside",
            connector={"line": {"color": "rgb(63,63,63)"}},
            increasing={"marker": {"color": "#2ca02c"}},
            decreasing={"marker": {"color": "#d62728"}},
            totals={"marker": {"color": "#1f77b4"}},
        )
    )
    fig_waterfall.update_layout(
        showlegend=False,
        yaxis_title="P&L ($)",
        margin=dict(t=20, b=20),
        height=max(300, len(results_df) * 60 + 80),
        yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="black"),
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

st.divider()

# ── Active scenario recap ──────────────────────────────────────────────────────

st.subheader("Active Macro Scenario")

active_shocks = {f: v for f, v in st.session_state.scenario.items() if abs(v) > 0}
if active_shocks:
    shock_cols = st.columns(len(active_shocks))
    for i, (factor, shock) in enumerate(active_shocks.items()):
        cfg = FACTORS[factor]
        sign = "+" if shock >= 0 else ""
        with shock_cols[i]:
            st.metric(
                label=f"{cfg['icon']} {cfg['label']}",
                value=f"{sign}{shock} {cfg['unit']}",
            )

st.divider()

# ── Navigation ─────────────────────────────────────────────────────────────────

col_prev, col_next = st.columns(2)
with col_prev:
    st.page_link("pages/2_Scenario_Builder.py", label="← Adjust Scenario")
with col_next:
    st.page_link("pages/4_Contribution_Analysis.py", label="Continue to Contribution Analysis →")
