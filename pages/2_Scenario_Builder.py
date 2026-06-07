import streamlit as st

from src.templates import FACTORS, PREBUILT_SCENARIOS
from src.scenario_checks import classify_severity, check_consistency
from src.ui import apply_theme, ACC, NEG, POS, BORDER, LIGHT

st.set_page_config(page_title="Scenario Builder", page_icon="⚙️", layout="wide")
apply_theme()

# ── Session state ──────────────────────────────────────────────────────────────

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
if "scenario" not in st.session_state:
    st.session_state.scenario = {f: 0.0 for f in FACTORS}
if "stress_mode" not in st.session_state:
    st.session_state.stress_mode = False

# ── Header ─────────────────────────────────────────────────────────────────────

st.title("⚙️ Scenario Builder")
st.markdown(
    "Define a macro scenario by moving the sliders below. "
    "Each value is the **change** from today's baseline. "
    "Load a pre-built template to get started quickly."
)
st.divider()

# ── Stress Testing Mode toggle ─────────────────────────────────────────────────

col_toggle, col_toggle_info = st.columns([1, 3])
with col_toggle:
    stress_on = st.toggle(
        "🔴 Stress Testing Mode",
        value=st.session_state.stress_mode,
        help=(
            "Expands DXY range to ±15% and Oil range to ±25% "
            "for crisis or tail-risk scenarios. "
            "Turn off to return to realistic day-to-day ranges."
        ),
    )
with col_toggle_info:
    if stress_on:
        st.markdown(
            f"<div style='background:#fff1f2;border-left:3px solid {NEG};"
            f"padding:0.5rem 0.9rem;border-radius:0 6px 6px 0;margin-top:4px;"
            f"font-size:0.9rem;'>"
            f"⚠️ <strong>Stress Testing Mode active.</strong> "
            f"DXY expanded to ±15% &nbsp;|&nbsp; Oil expanded to ±25%. "
            f"Use for tail-risk and crisis scenarios only."
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background:{LIGHT};border-left:3px solid {BORDER};"
            f"padding:0.5rem 0.9rem;border-radius:0 6px 6px 0;margin-top:4px;"
            f"font-size:0.9rem;color:#64748b;'>"
            f"Normal mode: DXY ±5% &nbsp;|&nbsp; Oil ±5%. "
            f"Enable Stress Testing Mode for larger market shocks."
            f"</div>",
            unsafe_allow_html=True,
        )

# Clamp out-of-range values when switching from stress → normal
if not stress_on and st.session_state.stress_mode:
    for factor in ("DXY", "Oil Price"):
        cfg = FACTORS[factor]
        clamped = max(cfg["min"], min(cfg["max"], st.session_state.scenario.get(factor, 0.0)))
        if clamped != st.session_state.scenario.get(factor, 0.0):
            st.session_state.scenario[factor] = clamped
            st.session_state[f"slider_{factor}"] = clamped

st.session_state.stress_mode = stress_on

st.divider()

# ── Pre-built scenario templates ───────────────────────────────────────────────

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
            # Clamp to current allowed range
            cfg = FACTORS[factor]
            lo = cfg.get("min_stress" if stress_on else "min", cfg["min"])
            hi = cfg.get("max_stress" if stress_on else "max", cfg["max"])
            clamped = float(max(lo, min(hi, shock)))
            st.session_state.scenario[factor] = clamped
            st.session_state[f"slider_{factor}"] = clamped
        st.success(f"Loaded: {selected}")
        st.rerun()

st.divider()

# ── Factor sliders ─────────────────────────────────────────────────────────────

st.subheader("Factor Shocks")
st.markdown(
    "Adjust each slider to set a macro shock. "
    "Values represent **changes from today's baseline**."
)

col_a, col_b = st.columns(2)
left_factors  = ["Fed Funds Rate", "US 10Y Yield", "Inflation"]
right_factors = ["GDP Growth", "DXY", "Oil Price"]


def render_slider(factor: str, container):
    cfg       = FACTORS[factor]
    is_market = factor in ("DXY", "Oil Price")

    # Dynamic range based on stress mode
    if is_market and stress_on:
        lo   = cfg["min_stress"]
        hi   = cfg["max_stress"]
        step = cfg["step"] * 2          # coarser step in stress mode
    else:
        lo   = cfg["min"]
        hi   = cfg["max"]
        step = cfg["step"]

    current = float(st.session_state.scenario.get(factor, 0.0))
    # Safety clamp in case session state holds a value outside current range
    current = max(lo, min(hi, current))

    range_label = f"±{hi}{cfg['unit']}" if is_market else f"{lo} to +{hi} {cfg['unit']}"

    with container:
        st.markdown(
            f"**{cfg['icon']} {cfg['label']}**  \n"
            f"<span style='color:#94a3b8;font-size:0.82em;'>"
            f"Baseline: **{cfg['baseline_label']}** &nbsp;|&nbsp; "
            f"Range: **{range_label}** &nbsp;|&nbsp; {cfg['example']}"
            f"</span>",
            unsafe_allow_html=True,
        )

        new_val = st.slider(
            label=factor,
            min_value=float(lo),
            max_value=float(hi),
            value=current,
            step=float(step),
            label_visibility="collapsed",
            key=f"slider_{factor}",
        )
        st.session_state.scenario[factor] = new_val

        if abs(new_val) < 0.001:
            badge = "<span style='color:#94a3b8;font-size:0.85em;'>No shock</span>"
        elif new_val > 0:
            badge = (
                f"<span style='background:{NEG};color:white;"
                f"padding:1px 8px;border-radius:4px;font-size:0.82em;font-weight:600;'>"
                f"▲ +{new_val} {cfg['unit']}</span>"
            )
        else:
            badge = (
                f"<span style='background:#2563eb;color:white;"
                f"padding:1px 8px;border-radius:4px;font-size:0.82em;font-weight:600;'>"
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
    shock_cols = st.columns(min(len(active), 6))
    for i, (factor, shock) in enumerate(active.items()):
        cfg  = FACTORS[factor]
        sign = "+" if shock >= 0 else ""
        with shock_cols[i % 6]:
            st.metric(
                label=f"{cfg['icon']} {cfg['label']}",
                value=f"{sign}{shock} {cfg['unit']}",
                delta=f"Base: {cfg['baseline_label']}",
                delta_color="off",
            )

    # ── Severity badge ─────────────────────────────────────────────────────────

    severity = classify_severity(st.session_state.scenario)
    if severity:
        SEVERITY_STYLE = {
            "Mild": (
                "#dcfce7", "#166534", "#16a34a",
                "🟢", "Shocks are within typical quarter-to-quarter variation.",
            ),
            "Moderate": (
                "#fef9c3", "#854d0e", "#ca8a04",
                "🟡", "At least one factor exceeds normal cyclical variation.",
            ),
            "Severe / Stress": (
                "#fee2e2", "#991b1b", "#dc2626",
                "🔴", "At least one factor reflects a significant macro stress event.",
            ),
        }
        bg, text_col, border_col, dot, desc = SEVERITY_STYLE[severity]
        st.markdown(
            f"<div style='background:{bg};border-left:4px solid {border_col};"
            f"border-radius:0 8px 8px 0;padding:0.6rem 1rem;margin-top:0.75rem;"
            f"display:inline-block;min-width:320px;'>"
            f"<span style='font-size:1rem;font-weight:700;color:{text_col};'>"
            f"{dot} Scenario Severity: {severity}</span><br>"
            f"<span style='font-size:0.85rem;color:{text_col};'>{desc}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Consistency warnings ───────────────────────────────────────────────────

    warnings = check_consistency(st.session_state.scenario)
    if warnings:
        st.markdown("")
        st.markdown(
            "<span style='font-size:0.95rem;font-weight:700;color:#92400e;'>"
            "⚠️ Scenario Consistency Warnings</span>",
            unsafe_allow_html=True,
        )
        st.caption(
            "The scenario is accepted as-is. These warnings flag combinations "
            "that are historically unusual and worth reviewing before presenting results."
        )
        for w in warnings:
            st.markdown(
                f"<div style='background:#fffbeb;border:1px solid #fcd34d;"
                f"border-radius:8px;padding:0.65rem 1rem;margin-bottom:0.5rem;"
                f"font-size:0.9rem;line-height:1.6;'>"
                f"⚠️ {w}"
                f"</div>",
                unsafe_allow_html=True,
            )

st.divider()

# ── Reset / navigation ─────────────────────────────────────────────────────────

col_reset, col_next = st.columns([1, 2])

with col_reset:
    if st.button("🔄 Reset All to Zero", width="stretch"):
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
