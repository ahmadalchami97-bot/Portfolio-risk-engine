import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.templates import FACTORS
from src.factor_model import compute_results, get_asset_factor_contributions
from src.narrative import generate_narrative
from src.ui import apply_theme, POS, NEG, ACC, BORDER, LIGHT, CHART_LAYOUT, narrative_box

st.set_page_config(page_title="Contribution Analysis", page_icon="🌪️", layout="wide")
apply_theme()

# ── Session state ──────────────────────────────────────────────────────────────

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
if "scenario" not in st.session_state:
    st.session_state.scenario = {f: 0.0 for f in FACTORS}

# ── Header ─────────────────────────────────────────────────────────────────────

st.title("🌪️ Contribution Analysis")
st.markdown(
    "Decompose the portfolio result: which macro factors drove gains or losses, "
    "and which assets were most affected."
)
st.divider()

# ── Guards ─────────────────────────────────────────────────────────────────────

if not st.session_state.portfolio:
    st.warning("No portfolio found.")
    st.page_link("pages/1_Portfolio_Builder.py", label="← Go to Portfolio Builder")
    st.stop()

active_shocks = {f: v for f, v in st.session_state.scenario.items() if abs(v) > 0.001}
if not active_shocks:
    st.warning("No macro shocks are active.")
    st.page_link("pages/2_Scenario_Builder.py", label="← Go to Scenario Builder")
    st.stop()

# ── Compute ────────────────────────────────────────────────────────────────────

results_df, summary, factor_contribs = compute_results(
    st.session_state.portfolio,
    st.session_state.scenario,
)

if results_df is None:
    st.error("Could not compute results.")
    st.stop()

long_df = get_asset_factor_contributions(results_df, st.session_state.scenario)
active_factor_names = list(active_shocks.keys())
active_contribs = {f: v for f, v in factor_contribs.items() if abs(v) > 0.0001}

# ── 1. Tornado Chart ───────────────────────────────────────────────────────────

st.subheader("Tornado Chart — Factor Contributions to Portfolio Return")
st.caption(
    "Each bar is one macro factor's weighted contribution to the total portfolio return. "
    "Sorted by absolute magnitude."
)

if active_contribs:
    tornado_df = pd.DataFrame([
        {
            "Factor": FACTORS[f]["icon"] + "  " + FACTORS[f]["label"],
            "Contribution (%)": v,
            "Direction": "Positive" if v >= 0 else "Negative",
        }
        for f, v in active_contribs.items()
    ]).sort_values("Contribution (%)", key=abs, ascending=True)

    max_abs = tornado_df["Contribution (%)"].abs().max()
    pad     = max_abs * 0.25 or 0.1

    fig_t = px.bar(
        tornado_df,
        x="Contribution (%)",
        y="Factor",
        orientation="h",
        color="Direction",
        color_discrete_map={"Positive": POS, "Negative": NEG},
        text=tornado_df["Contribution (%)"].apply(lambda x: f"{x:+.3f}%"),
    )
    fig_t.update_traces(textposition="outside", cliponaxis=False)
    fig_t.update_layout(
        **{**CHART_LAYOUT, "height": max(320, len(active_contribs) * 62 + 80)},
        showlegend=False,
        xaxis=dict(
            title="Contribution to Portfolio Return (%)",
            zeroline=True, zerolinewidth=2, zerolinecolor="#94a3b8",
            range=[
                min(tornado_df["Contribution (%)"]) - pad,
                max(tornado_df["Contribution (%)"]) + pad,
            ],
        ),
        yaxis=dict(title=""),
    )
    st.plotly_chart(fig_t, width="stretch")
else:
    st.info("No material factor contributions to display.")

st.divider()

# ── 2. Factor contribution table ────────────────────────────────────────────────

st.subheader("Factor Contribution Breakdown")

if active_contribs:
    total_return = summary["total_return_pct"]
    rows = []
    for factor, contrib in sorted(active_contribs.items(), key=lambda x: abs(x[1]), reverse=True):
        cfg   = FACTORS[factor]
        shock = st.session_state.scenario[factor]
        share = (contrib / total_return * 100) if abs(total_return) > 0.0001 else 0
        rows.append({
            "Factor":                   f"{cfg['icon']} {cfg['label']}",
            "Shock":                    f"{'+' if shock >= 0 else ''}{shock} {cfg['unit']}",
            "Portfolio Contribution (%)": round(contrib, 4),
            "Share of Total Return (%)":  round(share, 1),
        })

    cdf = pd.DataFrame(rows)

    def _color(val):
        try:
            f = float(val)
            if f > 0: return f"color:{POS}; font-weight:600"
            if f < 0: return f"color:{NEG}; font-weight:600"
        except (TypeError, ValueError):
            pass
        return ""

    styled_c = (
        cdf.style
        .map(_color, subset=["Portfolio Contribution (%)", "Share of Total Return (%)"])
        .format({
            "Portfolio Contribution (%)": "{:+.4f}%",
            "Share of Total Return (%)":  "{:+.1f}%",
        }, na_rep="—")
    )
    st.dataframe(styled_c, width="stretch", hide_index=True)

st.divider()

# ── 3. Asset × Factor heatmap ──────────────────────────────────────────────────

st.subheader("Asset × Factor Contribution Heatmap")
st.caption(
    "Each cell = contribution (%) of one factor to one asset's return. "
    "Green = positive, Red = negative."
)

asset_names = results_df["Asset"].tolist()
heatmap_data = []
for asset in st.session_state.portfolio:
    row = [
        round(asset["betas"].get(f, 0.0) * st.session_state.scenario.get(f, 0.0), 3)
        for f in active_factor_names
    ]
    heatmap_data.append(row)

heatmap_matrix = np.array(heatmap_data)
factor_labels  = [FACTORS[f]["icon"] + "  " + FACTORS[f]["label"] for f in active_factor_names]

if heatmap_matrix.size > 0:
    # Annotation strings
    annotations = [[f"{v:+.2f}%" for v in row] for row in heatmap_matrix]

    fig_hm = go.Figure(go.Heatmap(
        z=heatmap_matrix,
        x=factor_labels,
        y=asset_names,
        colorscale=[
            [0.0,  "#fca5a5"],   # light red
            [0.45, "#ffffff"],
            [0.55, "#ffffff"],
            [1.0,  "#86efac"],   # light green
        ],
        zmid=0,
        text=annotations,
        texttemplate="%{text}",
        textfont=dict(size=13, color="#1e293b"),
        colorbar=dict(title="Return (%)", ticksuffix="%"),
        showscale=True,
    ))
    fig_hm.update_layout(
        **{**CHART_LAYOUT, "height": max(300, len(asset_names) * 70 + 120)},
        xaxis=dict(title="Macro Factor", tickangle=-20),
        yaxis=dict(title="Asset"),
    )
    st.plotly_chart(fig_hm, width="stretch")

st.divider()

# ── 4. Stacked bar decomposition ───────────────────────────────────────────────

if len(st.session_state.portfolio) > 0 and active_factor_names:
    st.subheader("Asset Return Decomposition")
    st.caption("Each bar shows one asset's total estimated return, coloured by the factor that drove it.")

    long_active = long_df[long_df["Factor"].isin(active_factor_names)].copy()
    long_active["Factor Label"] = long_active["Factor"].apply(
        lambda f: FACTORS[f]["icon"] + "  " + FACTORS[f]["label"]
    )

    # Professional sequential palette for factors
    n_factors = len(active_factor_names)
    palette   = px.colors.sample_colorscale("Blues", [i / max(n_factors - 1, 1) for i in range(n_factors)])

    fig_s = px.bar(
        long_active,
        x="Asset",
        y="Contribution (%)",
        color="Factor Label",
        barmode="relative",
        color_discrete_sequence=palette,
    )
    fig_s.add_hline(y=0, line_width=1.5, line_color="#94a3b8")
    fig_s.update_layout(
        **{**CHART_LAYOUT, "height": 400},
        xaxis_title="",
        yaxis=dict(
            title="Return Contribution (%)",
            zeroline=True, zerolinewidth=2, zerolinecolor="#94a3b8",
            showgrid=True, gridcolor=BORDER,
        ),
        legend=dict(title="Macro Factor", orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig_s, width="stretch")
    st.divider()

# ── 5. Narrative Summary ───────────────────────────────────────────────────────

st.subheader("Narrative Summary")
st.caption("Auto-generated plain-English explanation of the scenario outcome.")

narrative = generate_narrative(
    portfolio_summary=summary,
    factor_contributions=factor_contribs,
    results_df=results_df,
    scenario=st.session_state.scenario,
)
narrative_box(narrative)

st.divider()

col_prev, col_home = st.columns(2)
with col_prev:
    st.page_link("pages/3_Results_Dashboard.py", label="← Back to Results")
with col_home:
    st.page_link("app.py", label="↩ Home")
