import streamlit as st

from src.templates import FACTORS, PREBUILT_SCENARIOS

st.set_page_config(page_title="Scenario Builder", page_icon="⚙️", layout="wide")

# ── Session state init ─────────────────────────────────────────────────────────

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

if "scenario" not in st.session_state:
    st.session_state.scenario = {f: 0.0 for f in FACTORS}

# ── Header ─────────────────────────────────────────────────────────────────────

st.title("⚙️ Scenario Builder")
st.markdown(
    "Define a macro scenario by adjusting the sliders below. "
    "Each slider represents a **change** from the current baseline value. "
    "Or load a pre-built scenario template to get started quickly."
)
st.divider()

# ── Pre-built scenario loader ──────────────────────────────────────────────────

st.subheader("Load a Pre-Built Scenario")

selected_template = st.selectbox(
    "Scenario Template",
    options=list(PREBUILT_SCENARIOS.keys()),
    index=0,
    help="Load a pre-configured macro scenario. You can then fine-tune it with the sliders.",
)

if selected_template != "— Select a template —":
    template_data = PREBUILT_SCENARIOS[selected_template]
    st.info(f"**{selected_template}** — {template_data['description']}")

    if st.button("Load This Scenario", type="primary"):
        st.session_state.scenario = dict(template_data["shocks"])
        st.success(f"Scenario loaded: {selected_template}")
        st.rerun()

st.divider()

# ── Manual sliders ─────────────────────────────────────────────────────────────

st.subheader("Manual Factor Shocks")
st.markdown(
    "Adjust each factor independently. "
    "Values represent the **change** from today's baseline."
)

col_a, col_b = st.columns(2)

factor_list = list(FACTORS.keys())
left_factors = factor_list[: len(factor_list) // 2 + len(factor_list) % 2]
right_factors = factor_list[len(factor_list) // 2 + len(factor_list) % 2 :]

def render_factor_slider(factor: str, container):
    cfg = FACTORS[factor]
    current_val = st.session_state.scenario.get(factor, 0.0)

    with container:
        st.markdown(
            f"**{cfg['icon']} {cfg['label']}**  \n"
            f"<span style='color:grey;font-size:0.85em'>"
            f"Baseline: {cfg['baseline_label']} | Unit: {cfg['unit']} | {cfg['example']}"
            f"</span>",
            unsafe_allow_html=True,
        )
        new_val = st.slider(
            label=factor,
            min_value=float(cfg["min"]),
            max_value=float(cfg["max"]),
            value=float(current_val),
            step=float(cfg["step"]),
            label_visibility="collapsed",
            key=f"slider_{factor}",
        )
        st.session_state.scenario[factor] = new_val

        # Colour-coded indicator
        if abs(new_val) < 0.01:
            st.markdown(
                "<span style='color:grey'>Shock: **0** (no change)</span>",
                unsafe_allow_html=True,
            )
        elif new_val > 0:
            unit = cfg["unit"]
            st.markdown(
                f"<span style='color:#d62728'>Shock: **+{new_val} {unit}** ▲</span>",
                unsafe_allow_html=True,
            )
        else:
            unit = cfg["unit"]
            st.markdown(
                f"<span style='color:#1f77b4'>Shock: **{new_val} {unit}** ▼</span>",
                unsafe_allow_html=True,
            )
        st.markdown("")

for factor in left_factors:
    render_factor_slider(factor, col_a)

for factor in right_factors:
    render_factor_slider(factor, col_b)

st.divider()

# ── Scenario summary ───────────────────────────────────────────────────────────

st.subheader("Active Scenario Summary")

active = {f: v for f, v in st.session_state.scenario.items() if abs(v) > 0}

if not active:
    st.warning("All factors are set to zero — no macro shock is active.")
else:
    summary_cols = st.columns(len(active))
    for i, (factor, shock) in enumerate(active.items()):
        cfg = FACTORS[factor]
        sign = "+" if shock >= 0 else ""
        color = "#d62728" if shock > 0 else "#1f77b4"
        with summary_cols[i]:
            st.metric(
                label=f"{cfg['icon']} {cfg['label']}",
                value=f"{sign}{shock} {cfg['unit']}",
                delta=f"Baseline: {cfg['baseline_label']}",
            )

st.divider()

# ── Reset and navigation ───────────────────────────────────────────────────────

col_reset, col_next = st.columns([1, 2])

with col_reset:
    if st.button("🔄 Reset All Shocks to Zero", use_container_width=True):
        st.session_state.scenario = {f: 0.0 for f in FACTORS}
        st.rerun()

with col_next:
    if not st.session_state.portfolio:
        st.warning("Your portfolio is empty. Go back and add assets first.")
        st.page_link("pages/1_Portfolio_Builder.py", label="← Back to Portfolio Builder")
    else:
        st.markdown("**Portfolio and scenario ready? View the results.**")
        st.page_link("pages/3_Results_Dashboard.py", label="Continue to Results Dashboard →")
