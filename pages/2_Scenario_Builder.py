import streamlit as st

from src.templates import FACTORS, PREBUILT_SCENARIOS
from src.scenario_checks import classify_severity, check_consistency
from src.ui import apply_theme, ACC, NEG, POS, NEU, BORDER, LIGHT, sign_color, sign_arrow, kpi_card, nav_button

st.set_page_config(page_title="Scenario Builder", page_icon="⚙️", layout="wide")
apply_theme()

# ── Session state init ─────────────────────────────────────────────────────────

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
if "scenario" not in st.session_state:
    st.session_state.scenario = {f: 0.0 for f in FACTORS}
st.session_state.setdefault("stress_toggle", False)
for _f in FACTORS:
    st.session_state.setdefault(f"slider_{_f}", 0.0)


# ── Callbacks (run BEFORE the script reruns — the Streamlit-safe place to ───────
#    modify widget-keyed session state without raising StreamlitAPIException) ────

def _reset_all():
    """Reset every slider and the stored scenario to zero."""
    for f in FACTORS:
        st.session_state[f"slider_{f}"] = 0.0
    st.session_state.scenario = {f: 0.0 for f in FACTORS}


def _load_template(name: str):
    """Load a pre-built scenario into the sliders, enabling Stress Mode
    automatically if the template needs the expanded ranges."""
    tdata = PREBUILT_SCENARIOS.get(name)
    if not tdata:
        return
    shocks = tdata["shocks"]

    # Does the template exceed normal market ranges? If so, enable Stress Mode.
    needs_stress = (
        abs(shocks.get("DXY", 0.0)) > FACTORS["DXY"]["max"]
        or abs(shocks.get("Oil Price", 0.0)) > FACTORS["Oil Price"]["max"]
    )
    if needs_stress:
        st.session_state["stress_toggle"] = True

    stress = st.session_state.get("stress_toggle", False)
    for f in FACTORS:
        cfg = FACTORS[f]
        is_market = f in ("DXY", "Oil Price")
        if is_market and stress:
            lo, hi = cfg["min_stress"], cfg["max_stress"]
        else:
            lo, hi = cfg["min"], cfg["max"]
        val = float(shocks.get(f, 0.0))
        st.session_state[f"slider_{f}"] = max(lo, min(hi, val))


# ── Header ─────────────────────────────────────────────────────────────────────

st.title("⚙️ Scenario Builder")
st.markdown(
    "Define a macro scenario by moving the sliders below. "
    "Each value is the **change** from today's baseline. "
    "Load a pre-built template to get started quickly."
)
st.divider()

# ── Stress Mode toggle ─────────────────────────────────────────────────────────

col_toggle, col_toggle_info = st.columns([1, 3])
with col_toggle:
    stress_on = st.toggle(
        "🔴 Stress Mode",
        key="stress_toggle",
        help="Stress Mode: Allows extreme but less common macro shocks.",
    )
with col_toggle_info:
    if stress_on:
        st.markdown(
            f"<div style='background:#fff1f2;border-left:3px solid {NEG};"
            f"padding:0.5rem 0.9rem;border-radius:0 6px 6px 0;margin-top:4px;"
            f"font-size:0.9rem;'>"
            f"⚠️ <strong>Stress Mode: Allows extreme but less common macro shocks.</strong><br>"
            f"DXY expanded to ±15% &nbsp;|&nbsp; Oil expanded to ±25%."
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background:{LIGHT};border-left:3px solid {BORDER};"
            f"padding:0.5rem 0.9rem;border-radius:0 6px 6px 0;margin-top:4px;"
            f"font-size:0.9rem;color:{NEU};'>"
            f"Normal mode: DXY ±5% &nbsp;|&nbsp; Oil ±5%. "
            f"Enable <strong>Stress Mode</strong> for extreme but less common macro shocks."
            f"</div>",
            unsafe_allow_html=True,
        )

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
    st.button(
        "Load This Scenario",
        type="primary",
        on_click=_load_template,
        args=(selected,),
    )

st.divider()

# ── Factor sliders ─────────────────────────────────────────────────────────────

st.subheader("Factor Shocks")
st.markdown(
    "Adjust each slider to set a macro shock. "
    "Values represent **changes from today's baseline**."
)

col_a, col_b = st.columns(2)
left_factors  = ["Fed Funds Rate", "US 10Y Yield", "Inflation"]
right_factors = ["DXY", "Oil Price"]


def render_slider(factor: str, container):
    cfg       = FACTORS[factor]
    is_market = factor in ("DXY", "Oil Price")

    if is_market and stress_on:
        lo, hi, step = cfg["min_stress"], cfg["max_stress"], cfg["step"]
    else:
        lo, hi, step = cfg["min"], cfg["max"], cfg["step"]

    key = f"slider_{factor}"
    # Clamp the stored value into the current range BEFORE the widget is
    # instantiated (safe) — handles switching out of Stress Mode.
    st.session_state[key] = float(max(lo, min(hi, st.session_state.get(key, 0.0))))

    range_label = f"±{hi}{cfg['unit']}" if is_market else f"{lo} to +{hi} {cfg['unit']}"

    with container:
        st.markdown(
            f"**{cfg['icon']} {cfg['label']}**  \n"
            f"<span style='color:{NEU};font-size:0.82em;'>"
            f"Baseline: **{cfg['baseline_label']}** &nbsp;|&nbsp; "
            f"Range: **{range_label}** &nbsp;|&nbsp; {cfg['example']}"
            f"</span>",
            unsafe_allow_html=True,
        )

        new_val = st.slider(
            label=factor,
            min_value=float(lo),
            max_value=float(hi),
            step=float(step),
            label_visibility="collapsed",
            key=key,
        )

        # Colour rule (consistent everywhere): + green ▲, − red ▼, 0 grey
        color = sign_color(new_val)
        arrow = sign_arrow(new_val)
        if abs(new_val) < 0.001:
            badge = f"<span style='color:{NEU};font-size:0.85em;'>{arrow} No shock</span>"
        else:
            sign = "+" if new_val > 0 else ""
            badge = (
                f"<span style='background:{color};color:white;"
                f"padding:1px 8px;border-radius:4px;font-size:0.82em;font-weight:600;'>"
                f"{arrow} {sign}{new_val} {cfg['unit']}</span>"
            )
        st.markdown(badge + "&nbsp;", unsafe_allow_html=True)
        st.markdown("")


for f in left_factors:
    render_slider(f, col_a)
for f in right_factors:
    render_slider(f, col_b)

# Rebuild the scenario dict from the sliders (single source of truth; also
# prunes any factors no longer in the model).
st.session_state.scenario = {f: st.session_state[f"slider_{f}"] for f in FACTORS}

st.divider()

# ── Active scenario summary ────────────────────────────────────────────────────

st.subheader("Active Scenario")

active = {f: v for f, v in st.session_state.scenario.items() if abs(v) > 0.001}

if not active:
    st.warning("All factors are at zero — no macro shock is active.")
else:
    shock_cols = st.columns(min(len(active), 5))
    for i, (factor, shock) in enumerate(active.items()):
        cfg   = FACTORS[factor]
        sign  = "+" if shock > 0 else ""
        arrow = sign_arrow(shock)
        with shock_cols[i % 5]:
            st.markdown(
                kpi_card(
                    label=f"{cfg['icon']} {cfg['label']}",
                    value=f"{arrow} {sign}{shock} {cfg['unit']}",
                    color=sign_color(shock),
                    sublabel=f"Base: {cfg['baseline_label']}",
                ),
                unsafe_allow_html=True,
            )

    # ── Severity badge ─────────────────────────────────────────────────────────
    severity = classify_severity(st.session_state.scenario)
    if severity:
        SEVERITY_STYLE = {
            "Mild": ("#dcfce7", "#166534", "#16a34a", "🟢",
                     "Shocks are within typical quarter-to-quarter variation."),
            "Moderate": ("#fef9c3", "#854d0e", "#ca8a04", "🟡",
                         "At least one factor exceeds normal cyclical variation."),
            "Severe / Stress": ("#fee2e2", "#991b1b", "#dc2626", "🔴",
                                 "At least one factor reflects a significant macro stress event."),
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
                f"font-size:0.9rem;line-height:1.6;'>⚠️ {w}</div>",
                unsafe_allow_html=True,
            )

st.divider()

# ── Reset / navigation ─────────────────────────────────────────────────────────

col_reset, col_next = st.columns([1, 2])

with col_reset:
    st.button("🔄 Reset All to Zero", width="stretch", on_click=_reset_all)

with col_next:
    if not st.session_state.portfolio:
        st.warning("No portfolio yet — go back and add assets first.")
        nav_button("← Back to Portfolio Builder", "/Portfolio_Builder")
    else:
        st.markdown("**Portfolio and scenario ready?**")
        nav_button("Continue to Results Dashboard →", "/Results_Dashboard")
