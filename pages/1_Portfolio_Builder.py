import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.templates import ASSET_TEMPLATES, FACTORS
from src.ui import apply_theme, POS, NEG, ACC, LIGHT, BORDER, CHART_LAYOUT

st.set_page_config(page_title="Portfolio Builder", page_icon="🏗️", layout="wide")
apply_theme()

# ── Session state ──────────────────────────────────────────────────────────────

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
if "scenario" not in st.session_state:
    st.session_state.scenario = {f: 0.0 for f in FACTORS}

# ── Header ─────────────────────────────────────────────────────────────────────

st.title("🏗️ Portfolio Builder")
st.markdown(
    "Select an asset template, enter your invested amount, and build your portfolio. "
    "Each template carries pre-defined factor sensitivities used in the scenario analysis."
)
st.divider()

# ── Add asset form ─────────────────────────────────────────────────────────────

st.subheader("Add an Asset")

with st.form("add_asset_form", clear_on_submit=True):
    col_tmpl, col_name, col_amt = st.columns([2, 2, 2])

    with col_tmpl:
        template_choice = st.selectbox(
            "Asset Template",
            options=list(ASSET_TEMPLATES.keys()),
            help="Each template has pre-calibrated macro factor sensitivities.",
        )

    with col_name:
        custom_name = st.text_input(
            "Display Name (optional)",
            placeholder=f"e.g. My {template_choice}",
            help="Leave blank to use the template name.",
        )

    with col_amt:
        # No max_value cap → supports institutional-sized positions (millions to billions).
        amount = st.number_input(
            "Amount Invested ($)",
            min_value=0,
            value=1_000_000,
            step=100_000,
            format="%d",
            help="Enter the dollar value of this position. Supports institutional sizes — e.g. 250,000,000.",
        )
        st.caption(f"💵 Amount entered: **${amount:,.0f}**")

    tmpl = ASSET_TEMPLATES[template_choice]
    st.markdown(
        f"**{tmpl['icon']} {template_choice}** — {tmpl['description']} &nbsp;|&nbsp; "
        f"Asset class: `{tmpl['asset_class']}`"
    )

    if st.form_submit_button("➕ Add to Portfolio", width="stretch", type="primary"):
        display_name = custom_name.strip() or template_choice
        st.session_state.portfolio.append({
            "id": len(st.session_state.portfolio),  # stable unique id
            "name": display_name,
            "template": template_choice,
            "asset_class": tmpl["asset_class"],
            "amount": amount,
            "betas": tmpl["betas"],
            "icon": tmpl["icon"],
        })
        st.success(f"Added **{display_name}** — ${amount:,.0f}")

st.divider()

# ── Portfolio ──────────────────────────────────────────────────────────────────

st.subheader("Current Portfolio")

if not st.session_state.portfolio:
    st.info("Your portfolio is empty. Add assets above to get started.")
else:
    portfolio = st.session_state.portfolio
    total_invested = sum(a["amount"] for a in portfolio)

    # KPI row
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Invested", f"${total_invested:,.0f}")
    k2.metric("Number of Assets", len(portfolio))
    largest = max(portfolio, key=lambda a: a["amount"])
    k3.metric("Largest Position", f"{largest['name']} ({largest['amount']/total_invested*100:.1f}%)")

    st.markdown("")

    # Holdings table — Amount pre-formatted as a comma string for reliable
    # thousands separators regardless of Streamlit version.
    rows = []
    for i, a in enumerate(portfolio):
        rows.append({
            "#": i + 1,
            "Asset": f"{a['icon']} {a['name']}",
            "Template": a["template"],
            "Class": a["asset_class"],
            "Amount ($)": f"${a['amount']:,.0f}",
            "Weight": round(a["amount"] / total_invested * 100, 1),
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config={
            "Amount ($)": st.column_config.TextColumn(label="Amount ($)"),
            "Weight": st.column_config.ProgressColumn(
                label="Weight (%)",
                min_value=0,
                max_value=100,
                format="%.1f%%",
            ),
        },
    )

    st.divider()

    # ── Charts ─────────────────────────────────────────────────────────────────

    col_pie, col_bar = st.columns(2)

    with col_pie:
        st.subheader("Allocation")
        fig_pie = px.pie(
            values=[a["amount"] for a in portfolio],
            names=[a["name"] for a in portfolio],
            hole=0.45,
            color_discrete_sequence=["#1e3a5f", "#2563eb", "#60a5fa", "#93c5fd", "#dbeafe"],
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            textfont_size=12,
        )
        layout = {**CHART_LAYOUT, "showlegend": False, "height": 340}
        fig_pie.update_layout(**layout)
        st.plotly_chart(fig_pie, width="stretch")

    with col_bar:
        st.subheader("Amount by Asset")
        fig_bar = go.Figure(go.Bar(
            x=[a["name"] for a in portfolio],
            y=[a["amount"] for a in portfolio],
            text=[f"${a['amount']:,.0f}" for a in portfolio],
            textposition="outside",
            marker_color=ACC,
            marker_line_width=0,
        ))
        fig_bar.update_layout(
            **{**CHART_LAYOUT, "height": 340},
            yaxis_title="Amount ($)",
            xaxis_title="",
            yaxis=dict(showgrid=True, gridcolor=BORDER),
            bargap=0.35,
        )
        st.plotly_chart(fig_bar, width="stretch")

    st.divider()

    # ── Factor sensitivity table ────────────────────────────────────────────────

    st.subheader("Factor Sensitivities (Betas)")
    st.markdown(
        "Each number below is an assumed sensitivity coefficient.\n\n"
        "**Example:**\n"
        "- Gold Inflation = **+3.0** means if Inflation rises by 1.0 percentage point, "
        "Gold is assumed to rise by approximately 3.0%.\n"
        "- Gold Fed Funds = **-2.0** means if Fed Funds rises by 1.0 percentage point, "
        "Gold is assumed to fall by approximately 2.0%.\n\n"
        "**Positive** values mean the asset tends to move in the **same** direction as the factor.  \n"
        "**Negative** values mean the asset tends to move in the **opposite** direction.\n\n"
        "_These sensitivities are used for scenario analysis and represent typical market relationships._"
    )

    beta_rows = []
    for a in portfolio:
        row = {"Asset": f"{a['icon']} {a['name']}"}
        row.update(a["betas"])
        beta_rows.append(row)

    beta_df = pd.DataFrame(beta_rows)

    def color_beta(val):
        try:
            f = float(val)
            if f > 0:  return f"background-color:#dcfce7; color:#166534"
            if f < 0:  return f"background-color:#fee2e2; color:#991b1b"
        except (TypeError, ValueError):
            pass
        return ""

    factor_cols = [c for c in beta_df.columns if c != "Asset"]
    styled_beta = beta_df.style.map(color_beta, subset=factor_cols).format(
        {c: "{:+.1f}" for c in factor_cols}
    )
    st.dataframe(styled_beta, width="stretch", hide_index=True)

    st.divider()

    # ── Remove assets ───────────────────────────────────────────────────────────

    st.subheader("Manage Assets")
    options = {f"#{i+1} — {a['icon']} {a['name']} (${a['amount']:,.0f})": i for i, a in enumerate(portfolio)}
    selected_label = st.selectbox("Select asset to remove", options=list(options.keys()))
    selected_idx = options[selected_label]

    col_rm, col_clr = st.columns([1, 1])
    with col_rm:
        if st.button("🗑️ Remove Selected", width="stretch"):
            # Index-based removal avoids duplicate-name bug
            st.session_state.portfolio = [
                a for i, a in enumerate(st.session_state.portfolio) if i != selected_idx
            ]
            st.rerun()
    with col_clr:
        if st.button("❌ Clear Portfolio", width="stretch"):
            st.session_state.portfolio = []
            st.rerun()

    st.divider()
    st.markdown("**Portfolio ready? Continue to the Scenario Builder.**")
    st.markdown("<a class='nav-btn' href='/Scenario_Builder' target='_self'>Continue to Scenario Builder →</a>", unsafe_allow_html=True)
