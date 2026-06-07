import streamlit as st
import plotly.express as px
import pandas as pd

from src.templates import ASSET_TEMPLATES

st.set_page_config(page_title="Portfolio Builder", page_icon="🏗️", layout="wide")

# ── Session state init ─────────────────────────────────────────────────────────

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

# ── Page header ────────────────────────────────────────────────────────────────

st.title("🏗️ Portfolio Builder")
st.markdown(
    "Add assets to your portfolio using the pre-built templates below. "
    "Enter the amount you have invested in each asset."
)
st.divider()

# ── Add asset form ─────────────────────────────────────────────────────────────

st.subheader("Add an Asset")

with st.form("add_asset_form", clear_on_submit=True):
    col_template, col_name, col_amount = st.columns([2, 2, 2])

    with col_template:
        template_choice = st.selectbox(
            "Asset Template",
            options=list(ASSET_TEMPLATES.keys()),
            help="Select a pre-built asset type. Each template has calibrated factor sensitivities.",
        )

    with col_name:
        custom_name = st.text_input(
            "Display Name (optional)",
            placeholder=f"e.g. My {template_choice} position",
            help="Leave blank to use the template name.",
        )

    with col_amount:
        amount = st.number_input(
            "Amount Invested ($)",
            min_value=1_000,
            max_value=100_000_000,
            value=100_000,
            step=10_000,
            format="%d",
            help="Enter the total dollar value of this position.",
        )

    # Show template info
    template_data = ASSET_TEMPLATES[template_choice]
    st.markdown(
        f"**{template_data['icon']} {template_choice}** — {template_data['description']}  \n"
        f"Asset class: `{template_data['asset_class']}`"
    )

    submitted = st.form_submit_button("➕ Add to Portfolio", use_container_width=True, type="primary")

    if submitted:
        display_name = custom_name.strip() if custom_name.strip() else template_choice
        new_asset = {
            "name": display_name,
            "template": template_choice,
            "asset_class": template_data["asset_class"],
            "amount": amount,
            "betas": template_data["betas"],
            "icon": template_data["icon"],
        }
        st.session_state.portfolio.append(new_asset)
        st.success(f"Added **{display_name}** — ${amount:,.0f}")

st.divider()

# ── Portfolio table ────────────────────────────────────────────────────────────

st.subheader("Current Portfolio")

if not st.session_state.portfolio:
    st.info("Your portfolio is empty. Add assets above to get started.")
else:
    total_invested = sum(a["amount"] for a in st.session_state.portfolio)

    # Build display DataFrame
    rows = []
    for i, asset in enumerate(st.session_state.portfolio):
        weight = asset["amount"] / total_invested * 100
        rows.append(
            {
                "#": i + 1,
                "Asset": f"{asset['icon']} {asset['name']}",
                "Template": asset["template"],
                "Asset Class": asset["asset_class"],
                "Amount ($)": asset["amount"],
                "Weight (%)": round(weight, 1),
            }
        )

    display_df = pd.DataFrame(rows)

    # Totals row
    totals = pd.DataFrame(
        [
            {
                "#": "",
                "Asset": "**TOTAL**",
                "Template": "",
                "Asset Class": "",
                "Amount ($)": total_invested,
                "Weight (%)": 100.0,
            }
        ]
    )
    display_df = pd.concat([display_df, totals], ignore_index=True)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount ($)": st.column_config.NumberColumn(format="$%d"),
            "Weight (%)": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

    # Weight warning
    if abs(sum(a["amount"] for a in st.session_state.portfolio) - total_invested) < 0.01:
        st.metric("Total Portfolio Value", f"${total_invested:,.0f}")

    st.divider()

    # ── Weight visualisation ────────────────────────────────────────────────────

    col_chart, col_betas = st.columns([1, 1])

    with col_chart:
        st.subheader("Weight Allocation")
        chart_data = [
            {"Asset": a["name"], "Amount": a["amount"]}
            for a in st.session_state.portfolio
        ]
        fig = px.pie(
            chart_data,
            values="Amount",
            names="Asset",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(
            showlegend=True,
            margin=dict(t=20, b=20, l=20, r=20),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_betas:
        st.subheader("Factor Sensitivities (Betas)")
        st.markdown(
            "Each row shows how sensitive an asset is to a 1-unit macro shock. "
            "Negative = asset falls when factor rises."
        )

        beta_rows = []
        for asset in st.session_state.portfolio:
            row = {"Asset": asset["name"]}
            row.update(asset["betas"])
            beta_rows.append(row)

        beta_df = pd.DataFrame(beta_rows)
        st.dataframe(
            beta_df,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # ── Remove assets ───────────────────────────────────────────────────────────

    st.subheader("Remove an Asset")
    asset_names = [a["name"] for a in st.session_state.portfolio]
    to_remove = st.selectbox("Select asset to remove", options=asset_names)

    col_remove, col_clear = st.columns([1, 1])
    with col_remove:
        if st.button("🗑️ Remove Selected Asset", use_container_width=True):
            st.session_state.portfolio = [
                a for a in st.session_state.portfolio if a["name"] != to_remove
            ]
            st.rerun()

    with col_clear:
        if st.button("❌ Clear Entire Portfolio", use_container_width=True):
            st.session_state.portfolio = []
            st.rerun()

    st.divider()

    # ── Navigation ──────────────────────────────────────────────────────────────

    st.markdown("**Ready to define your macro scenario?**")
    st.page_link("pages/2_Scenario_Builder.py", label="Continue to Scenario Builder →")
