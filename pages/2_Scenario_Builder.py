import streamlit as st

from src.templates import FACTORS, PREBUILT_SCENARIOS
from src.ui import apply_theme, ACC, NEG, BORDER

st.set_page_config(page_title="Scenario Builder", page_icon="⚙️", layout="wide")
apply_theme()

# ── Session state ──────────────────────────────────────────────────────────────

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
if "scenario" not in st.session_state:
    st.session_state.scenario = {f: 0.0 for f in FACTORS}

# ── Header ─────────────────────────────────────────────────────────────────────

st.title("⚙️ Scenario Builder")
st.markdown(
    "Define a macro scenario by moving the sliders below. "
    "Each value represents the **change** from today's baseline. "
    "Load a pre-built template to get started quickly."
)
st.divider()

# ── Pre-built templates ────────────────────────────────────────────────────────

st.subheader("Pre-Built Scenario Templates")

selected = st.selectbox(
    "Load a scenario template",
    options=list(PREBUILT_SCENARIOS.keys()),
    index=0,
)

if selected != "— Select a template —":
    tdata = PREBUILT_SCENARIOS[selected]
    st.info(f"**{selected}** — {tdata['description']}")

    if st.button("Load This Scenario", type="primary"):
        for factor, shock in tdata["shocks"].items():
            # Update both the scenario dict and the slider widget key so
            # the sliders visually reflect the loaded values on rerun.
            st.session_state.scenario[factor] = float(shock)
            st.session_state[f"slider_{factor}"] = float(shock)
        st.success(f"Loaded: {selected}")
        st.rerun()

st.divider()

# ── Manual sliders ─────────────────────────────────────────────────────────────

st.subheader("Factor Shocks")
st.markdown(
    "Move each slider to apply a shock. "
    "Values are **changes** from the baseline shown below each slider."
)

col_a, col_b = st.columns(2)
factor_list = list(FACTORS.keys())
left_factors  = factor_list[:3]   # Fed Funds, US10Y, Inflation
right_factors = factor_list[3:]   # GDP, DXY, Oil


def render_slider(factor: str, container):
    cfg = FACTORS[factor]
    current = float(st.session_state.scenario.get(factor, 0.0))

    with container:
        st.markdown(
            f"**{cfg['icon']} {cfg['label']}**  \n"
            f"<span style='color:{BORDER[1:]};font-size:0.82em;'>"  # reuse hex but as text
            f"Baseline today: **{cfg['baseline_label']}** &nbsp;|&nbsp; "
            f"Unit: **{cfg['unit']}** &nbsp;|&nbsp; {cfg['example']}"
            f"</span>",
            unsafe_allow_html=True,
        )

        new_val = st.slider(
            label=factor,
            min_value=float(cfg["min"]),
            max_value=float(cfg["max"]),
            value=current,
            step=float(cfg["step"]),
            label_visibility="collapsed",
            key=f"slider_{factor}",
        )
        # Keep scenario dict in sync with the slider widget
        st.session_state.scenario[factor] = new_val

        if abs(new_val) < 0.001:
            badge = f"<span style='color:#94a3b8'>No shock applied</span>"
        elif new_val > 0:
            badge = (
                f"<span style='background:{NEG};color:white;"
                f"padding:2px 8px;border-radius:4px;font-size:0.82em;'>"
                f"▲ +{new_val} {cfg['unit']}</span>"
            )
        else:
            badge = (
                f"<span style='background:#2563eb;color:white;"
                f"padding:2px 8px;border-radius:4px;font-size:0.82em;'>"
                f"▼ {new_val} {cfg['unit']}</span>"
            )
        st.markdown(badge + "&nbsp;", unsafe_allow_html=True)
        st.markdown("")


for f in left_factors:
    render_slider(f, col_a)
for f in right_factors:
    render_slider(f, col_b)

st.divider()

# ── Active scenario summary ────────────────────────────────────────────────────

st.subheader("Active Scenario")

active = {f: v for f, v in st.session_state.scenario.items() if abs(v) > 0.001}

if not active:
    st.warning("All factors are at zero — no macro shock is active.")
else:
    cols = st.columns(min(len(active), 6))
    for i, (factor, shock) in enumerate(active.items()):
        cfg = FACTORS[factor]
        sign = "+" if shock >= 0 else ""
        with cols[i % 6]:
            st.metric(
                label=f"{cfg['icon']} {cfg['label']}",
                value=f"{sign}{shock} {cfg['unit']}",
                delta=f"Base: {cfg['baseline_label']}",
                delta_color="off",
            )

st.divider()

# ── Reset / navigation ─────────────────────────────────────────────────────────

col_reset, col_next = st.columns([1, 2])

with col_reset:
    if st.button("🔄 Reset All to Zero", use_container_width=True):
        for f in FACTORS:
            st.session_state.scenario[f] = 0.0
            st.session_state[f"slider_{f}"] = 0.0
        st.rerun()

with col_next:
    if not st.session_state.portfolio:
        st.warning("No portfolio yet — go back and add assets first.")
        st.page_link("pages/1_Portfolio_Builder.py", label="← Back to Portfolio Builder")
    else:
        st.markdown("**Portfolio and scenario ready?**")
        st.page_link("pages/3_Results_Dashboard.py", label="Continue to Results Dashboard →")
