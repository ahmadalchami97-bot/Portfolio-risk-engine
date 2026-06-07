"""
Scenario severity classification and macro consistency checks.

classify_severity() → 'Mild' | 'Moderate' | 'Severe / Stress' | None
check_consistency()  → list of warning strings (never blocks a scenario)
"""

# Per-factor thresholds: (mild_max, moderate_max).
# Anything above moderate_max is classified as Severe.
_THRESHOLDS: dict[str, tuple[float, float]] = {
    "Fed Funds Rate": (0.50, 1.50),   # pp
    "US 10Y Yield":   (0.50, 1.50),   # pp
    "Inflation":      (0.50, 1.50),   # pp
    "GDP Growth":     (0.50, 1.50),   # pp
    "DXY":            (1.50, 4.00),   # %
    "Oil Price":      (3.00, 10.00),  # %
}

_LEVEL_LABEL = {0: None, 1: "Mild", 2: "Moderate", 3: "Severe / Stress"}


def classify_severity(scenario: dict) -> str | None:
    """
    Return the overall severity label for a scenario.
    Based on the worst-classified single factor.
    """
    max_level = 0
    for factor, shock in scenario.items():
        if abs(shock) < 0.001:
            continue
        mild_max, mod_max = _THRESHOLDS.get(factor, (0.5, 1.5))
        abs_shock = abs(shock)
        if abs_shock > mod_max:
            level = 3
        elif abs_shock > mild_max:
            level = 2
        else:
            level = 1
        if level > max_level:
            max_level = level
    return _LEVEL_LABEL[max_level]


def check_consistency(scenario: dict) -> list[str]:
    """
    Check for historically unusual macro combinations.
    Returns a list of warning strings.  Never blocks the scenario.
    """
    fed  = scenario.get("Fed Funds Rate", 0.0)
    y10  = scenario.get("US 10Y Yield",   0.0)
    inf_ = scenario.get("Inflation",      0.0)
    gdp  = scenario.get("GDP Growth",     0.0)
    dxy  = scenario.get("DXY",            0.0)
    oil  = scenario.get("Oil Price",      0.0)

    warnings: list[str] = []

    # 1. Fed cutting while long rates rise sharply
    if fed <= -0.50 and y10 >= 1.00:
        warnings.append(
            "**Fed cutting while long rates rise sharply.** "
            "Markets appear to be demanding a fiscal or inflation premium despite easing — "
            "historically rare outside sovereign-stress episodes (e.g. UK Gilt crisis 2022)."
        )

    # 2. Fed hiking while long rates fall significantly
    if fed >= 1.00 and y10 <= -0.50:
        warnings.append(
            "**Fed hiking while the 10Y yield falls.** "
            "This implies aggressive curve inversion — a historically strong recession signal. "
            "The simultaneous occurrence of sharp hikes and falling long yields is unusual."
        )

    # 3. Strong GDP growth with sharply falling inflation
    if gdp >= 0.50 and inf_ <= -0.75:
        warnings.append(
            "**Strong GDP growth alongside sharply falling inflation.** "
            "Growth typically generates some price pressure. "
            "This 'immaculate disinflation' combination is historically very rare."
        )

    # 4. Oil rising significantly with no inflation response
    if oil >= 5.00 and abs(inf_) < 0.25:
        warnings.append(
            "**Oil rising significantly with no inflation impact modeled.** "
            "Energy is a major CPI component. "
            "A move of this size with zero inflation response is historically unusual — "
            "consider whether an inflation shock should also be applied."
        )

    # 5. Dollar and oil both rising sharply
    if dxy >= 3.00 and oil >= 5.00:
        warnings.append(
            "**Dollar and oil both rising sharply.** "
            "Since oil is priced in USD, a stronger dollar typically suppresses oil prices. "
            "Both appreciating simultaneously is historically uncommon."
        )

    # 6. Fed cutting while inflation surging
    if fed <= -0.75 and inf_ >= 1.50:
        warnings.append(
            "**Fed cutting rates while inflation surges.** "
            "This mirrors the 1970s policy error. "
            "Under modern central bank mandates, this combination is extremely unusual."
        )

    # 7. Severe recession with surging oil but low inflation
    if gdp <= -2.00 and oil >= 10.00 and inf_ < 1.00:
        warnings.append(
            "**Severe recession with a large oil shock but low modeled inflation.** "
            "Historical oil shocks (1973, 1979) produced both recession and high inflation. "
            "Consider whether inflation should be shocked upward to reflect this."
        )

    # 8. GDP falling sharply while Fed hiking aggressively
    if gdp <= -1.50 and fed >= 1.50:
        warnings.append(
            "**Aggressive rate hikes alongside a sharp GDP contraction.** "
            "Central banks typically pause or reverse hiking cycles during recessions. "
            "This combination implies a severe stagflationary policy bind."
        )

    return warnings
