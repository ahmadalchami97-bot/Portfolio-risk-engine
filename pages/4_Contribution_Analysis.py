import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.templates import FACTORS
from src.factor_model import compute_results, get_asset_factor_contributions
from src.narrative import generate_narrative

st.set_page_config(page_title="Contribution Analysis", page_icon="🌪️", layout="wide")

# ── Session state init ─────────────────────────────────────────────────────────

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

if "scenario" not in st.session_state:
    st.session_state.scenario = {f: 0.0 for f in FACTORS}

# ── Header ─────────────────────────────────────────────────────────────────────

st.title("🌪️ Contribution Analysis")
st.markdown(
    "Understand **what drove** the portfolio result: which macro factors mattered most "
    "and which assets were hit hardest."
)
st.divider()

# ── Guard ──────────────────────────────────────────────────────────────────────

if not st.session_state.portfolio:
    st.warning("No portfolio found.")
    st.page_link("pages/1_Portfolio_Builder.py", label="← Go to Portfolio Builder")
    st.stop()

active_shocks = {f: v for f, v in st.session_state.scenario.items() if abs(v) > 0}
if not active_shocks:
    st.warning("No macro scenario is active.")
    st.page_link("pages/2_Scenario_Builder.py", label="← Go to Scenario Builder")
    st.stop()

# ── Compute ────────────────────────────────────────────────────────────────────

results_df, portfolio_summary, factor_contributions = compute_results(
    st.session_state.portfolio,
    st.session_state.scenario,
)

if results_df is None:
    st.error("Could not compute results.")
    st.stop()

long_df = get_asset_factor_contributions(results_df, st.session_state.scenario)

# ── 1. Tornado Chart ───────────────────────────────────────────────────────────

st.subheader("Tornado Chart — Factor Contributions to Portfolio Return")
st.markdown(
    "Each bar shows the estimated contribution of one macro factor to the "
    "total portfolio return, sorted by magnitude. "
    "Longer bars = bigger impact."
)

# Only show active factors
active_factor_contribs = {
    f: v for f, v in factor_contributions.items() if abs(v) > 0
}

if active_factor_contribs:
    tornado_df = pd.DataFrame(
        [
            {
                "Factor": FACTORS[f]["icon"] + " " + FACTORS[f]["label"],
                "Contribution (%)": v,
                "Direction": "Positive" if v >= 0 else "Negative",
            }
            for f, v in active_factor_contribs.items()
        ]
    ).sort_values("Contribution (%)", key=abs, ascending=True)

    fig_tornado = px.bar(
        tornado_df,
        x="Contribution (%)",
        y="Factor",
        orientation="h",
        color="Direction",
        color_discrete_map={"Positive": "#2ca02c", "Negative": "#d62728"},
        text=tornado_df["Contribution (%)"].apply(lambda x: f"{x:+.3f}%"),
    )
    fig_tornado.update_traces(textposition="outside")
    fig_tornado.update_layout(
        showlegend=False,
        xaxis_title="Contribution to Portfolio Return (%)",
        yaxis_title="",
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="black"),
        margin=dict(t=20, b=20),
        height=max(300, len(active_factor_contribs) * 60 + 80),
    )
    st.plotly_chart(fig_tornado, use_container_width=True)
else:
    st.info("No factor contributions to display — all shocks are zero.")

st.divider()

# ── 2. Factor Contribution Table ───────────────────────────────────────────────

st.subheader("Factor Contribution Breakdown")

if active_factor_contribs:
    contrib_rows = []
    total_return = portfolio_summary["total_return_pct"]
    for factor, contrib in sorted(
        active_factor_contribs.items(), key=lambda x: abs(x[1]), reverse=True
    ):
        cfg = FACTORS[factor]
        shock = st.session_state.scenario[factor]
        pct_of_total = (contrib / total_return * 100) if abs(total_return) > 0.0001 else 0
        contrib_rows.append(
            {
                "Factor": f"{cfg['icon']} {cfg['label']}",
                "Shock": f"{'+' if shock >= 0 else ''}{shock} {cfg['unit']}",
                "Contribution (%)": round(contrib, 4),
                "Share of Total Return (%)": round(pct_of_total, 1),
            }
        )

    contrib_df = pd.DataFrame(contrib_rows)

    def color_contrib(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return "color: #2ca02c; font-weight: bold"
            elif val < 0:
                return "color: #d62728; font-weight: bold"
        return ""

    styled_contrib = contrib_df.style.map(
        color_contrib, subset=["Contribution (%)", "Share of Total Return (%)"]
    ).format(
        {
            "Contribution (%)": "{:+.4f}%",
            "Share of Total Return (%)": "{:+.1f}%",
        }
    )
    st.dataframe(styled_contrib, use_container_width=True, hide_index=True)

st.divider()

# ── 3. Asset × Factor Heatmap ──────────────────────────────────────────────────

st.subheader("Asset × Factor Contribution Heatmap (%)")
st.markdown(
    "Each cell shows the contribution of one factor to one asset's return. "
    "Red = negative contribution, Green = positive."
)

active_factor_names = [f for f in st.session_state.scenario if abs(st.session_state.scenario[f]) > 0]
asset_names = results_df["Asset"].tolist()

heatmap_data = []
for asset in st.session_state.portfolio:
    row = []
    for factor in active_factor_names:
        beta = asset["betas"].get(factor, 0.0)
        shock = st.session_state.scenario.get(factor, 0.0)
        contrib = beta * shock  # in %
        row.append(round(contrib, 3))
    heatmap_data.append(row)

heatmap_matrix = np.array(heatmap_data)
factor_labels = [
    FACTORS[f]["icon"] + " " + FACTORS[f]["label"] for f in active_factor_names
]

if heatmap_matrix.size > 0:
    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_matrix,
            x=factor_labels,
            y=asset_names,
            colorscale=[
                [0.0, "#d62728"],
                [0.5, "#ffffff"],
                [1.0, "#2ca02c"],
            ],
            zmid=0,
            text=[[f"{v:+.2f}%" for v in row] for row in heatmap_matrix],
            texttemplate="%{text}",
            textfont={"size": 13},
            colorbar=dict(title="Return (%)"),
        )
    )
    fig_heatmap.update_layout(
        xaxis_title="Macro Factor",
        yaxis_title="Asset",
        margin=dict(t=20, b=40),
        height=max(300, len(asset_names) * 60 + 120),
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

st.divider()

# ── 4. Stacked Bar — Per-Asset Factor Contributions ───────────────────────────

if len(st.session_state.portfolio) > 1 and len(active_factor_names) > 0:
    st.subheader("Asset Return Decomposition — Factor Stacking")
    st.markdown(
        "Each bar shows one asset's total return, coloured by which factor drove it."
    )

    long_active = long_df[long_df["Factor"].isin(active_factor_names)].copy()
    long_active["Factor Label"] = long_active["Factor"].apply(
        lambda f: FACTORS[f]["icon"] + " " + FACTORS[f]["label"]
    )

    fig_stack = px.bar(
        long_active,
        x="Asset",
        y="Contribution (%)",
        color="Factor Label",
        barmode="relative",
        text=long_active["Contribution (%)"].apply(lambda x: f"{x:+.2f}%"),
    )
    fig_stack.update_traces(textposition="inside", textfont_size=11)
    fig_stack.update_layout(
        xaxis_title="Asset",
        yaxis_title="Return Contribution (%)",
        legend_title="Macro Factor",
        margin=dict(t=20, b=20),
        height=420,
        yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="black"),
    )
    st.plotly_chart(fig_stack, use_container_width=True)
    st.divider()

# ── 5. Narrative Summary ───────────────────────────────────────────────────────

st.subheader("Narrative Summary")
st.markdown("*Auto-generated plain-English explanation of the scenario outcome.*")

narrative = generate_narrative(
    portfolio_summary=portfolio_summary,
    factor_contributions=factor_contributions,
    results_df=results_df,
    scenario=st.session_state.scenario,
)

st.markdown(
    f"""
    <div style="
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 16px 20px;
        border-radius: 4px;
        line-height: 1.7;
    ">
    {narrative.replace(chr(10), '<br>')}
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── Navigation ─────────────────────────────────────────────────────────────────

col_prev, col_home = st.columns(2)
with col_prev:
    st.page_link("pages/3_Results_Dashboard.py", label="← Back to Results Dashboard")
with col_home:
    st.page_link("app.py", label="↩ Back to Home")
