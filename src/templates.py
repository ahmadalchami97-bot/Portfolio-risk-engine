"""
Asset templates with pre-calibrated factor betas.

Beta interpretation: % return of asset per 1 unit of factor shock.
  - Rate factors (Fed Funds Rate, US 10Y Yield, Inflation, GDP Growth):
      1 unit = 1 percentage point (pp). e.g. Fed hikes 1pp → +100bps.
  - Market factors (DXY, Oil Price):
      1 unit = 1% change. e.g. DXY +5 → dollar up 5%.
"""

ASSET_TEMPLATES = {
    "Gold": {
        "icon": "🥇",
        "description": "Physical gold / Gold ETF (e.g. GLD)",
        "asset_class": "Commodity",
        "betas": {
            "Fed Funds Rate": -2.0,
            "US 10Y Yield":   -3.0,
            "Inflation":       5.0,
            "GDP Growth":     -1.0,
            "DXY":            -0.8,
            "Oil Price":       0.3,
        },
    },
    "US Equities": {
        "icon": "📈",
        "description": "S&P 500 broad market equity (e.g. SPY)",
        "asset_class": "Equity",
        "betas": {
            "Fed Funds Rate": -3.0,
            "US 10Y Yield":   -2.0,
            "Inflation":      -1.5,
            "GDP Growth":      4.0,
            "DXY":            -0.3,
            "Oil Price":       0.2,
        },
    },
    "US Treasuries": {
        "icon": "🏛️",
        "description": "Long-duration US government bonds (e.g. TLT)",
        "asset_class": "Bond",
        "betas": {
            "Fed Funds Rate": -5.0,
            "US 10Y Yield":   -8.0,
            "Inflation":      -3.0,
            "GDP Growth":     -1.0,
            "DXY":             0.1,
            "Oil Price":      -0.1,
        },
    },
    "Swiss Real Estate": {
        "icon": "🏠",
        "description": "Swiss listed real estate / REIT",
        "asset_class": "Real Estate",
        "betas": {
            "Fed Funds Rate": -1.5,
            "US 10Y Yield":   -3.0,
            "Inflation":       2.0,
            "GDP Growth":      2.0,
            "DXY":            -0.5,
            "Oil Price":       0.0,
        },
    },
}

FACTORS = {
    "Fed Funds Rate": {
        "unit": "pp",
        "label": "Fed Funds Rate",
        "description": "Federal Reserve policy rate change",
        "example": "+1.0 pp = Fed hikes 100bps",
        "min": -3.0,
        "max":  3.0,
        "step": 0.25,
        "baseline": 5.25,
        "baseline_label": "5.25%",
        "icon": "🏦",
    },
    "US 10Y Yield": {
        "unit": "pp",
        "label": "US 10Y Yield",
        "description": "10-Year US Treasury yield change",
        "example": "+0.5 pp = 10Y rises 50bps",
        "min": -3.0,
        "max":  3.0,
        "step": 0.25,
        "baseline": 4.30,
        "baseline_label": "4.30%",
        "icon": "📜",
    },
    "Inflation": {
        "unit": "pp",
        "label": "Inflation (CPI)",
        "description": "Annual CPI inflation change",
        "example": "+1.0 pp = inflation rises from 3% to 4%",
        "min": -3.0,
        "max":  5.0,
        "step": 0.25,
        "baseline": 3.20,
        "baseline_label": "3.2%",
        "icon": "🔥",
    },
    "GDP Growth": {
        "unit": "pp",
        "label": "GDP Growth",
        "description": "Annual GDP growth change",
        "example": "-1.0 pp = growth slows by 1 percentage point",
        "min": -5.0,
        "max":  3.0,
        "step": 0.25,
        "baseline": 2.10,
        "baseline_label": "2.1%",
        "icon": "📊",
    },
    "DXY": {
        "unit": "%",
        "label": "DXY (US Dollar Index)",
        "description": "Percentage change in US Dollar Index",
        "example": "+5.0% = dollar strengthens 5%",
        "min": -20.0,
        "max":  20.0,
        "step":  1.0,
        "baseline": 104.2,
        "baseline_label": "104.2",
        "icon": "💵",
    },
    "Oil Price": {
        "unit": "%",
        "label": "Oil Price (WTI)",
        "description": "Percentage change in WTI crude oil",
        "example": "+20.0% = oil rises 20%",
        "min": -50.0,
        "max":  50.0,
        "step":  5.0,
        "baseline": 78.5,
        "baseline_label": "$78.5/bbl",
        "icon": "🛢️",
    },
}

PREBUILT_SCENARIOS = {
    "— Select a template —": None,
    "🏦 Fed Aggressive Hike Cycle": {
        "description": "Fed raises rates sharply to contain persistent inflation. Bonds and rate-sensitive assets suffer.",
        "shocks": {
            "Fed Funds Rate":  2.00,
            "US 10Y Yield":    1.50,
            "Inflation":      -0.50,
            "GDP Growth":     -1.00,
            "DXY":             5.00,
            "Oil Price":     -10.00,
        },
    },
    "📉 Stagflation Shock": {
        "description": "High inflation combined with weak growth (1970s-style). Most asset classes suffer simultaneously.",
        "shocks": {
            "Fed Funds Rate":  1.00,
            "US 10Y Yield":    2.00,
            "Inflation":       4.00,
            "GDP Growth":     -2.00,
            "DXY":            -5.00,
            "Oil Price":      40.00,
        },
    },
    "🌧️ Recession & Risk-Off": {
        "description": "Economic contraction. Equities fall, Treasuries rally, Fed cuts rates aggressively.",
        "shocks": {
            "Fed Funds Rate": -1.50,
            "US 10Y Yield":   -1.00,
            "Inflation":      -1.00,
            "GDP Growth":     -3.00,
            "DXY":             2.00,
            "Oil Price":     -30.00,
        },
    },
    "🚀 Strong Growth Rally": {
        "description": "Goldilocks economy. Strong growth, moderate inflation. Equities outperform.",
        "shocks": {
            "Fed Funds Rate":  0.25,
            "US 10Y Yield":    0.50,
            "Inflation":       0.50,
            "GDP Growth":      1.50,
            "DXY":            -2.00,
            "Oil Price":      15.00,
        },
    },
    "💵 Dollar Collapse": {
        "description": "Sharp USD depreciation. Commodities and non-USD assets surge.",
        "shocks": {
            "Fed Funds Rate": -1.00,
            "US 10Y Yield":    0.50,
            "Inflation":       2.00,
            "GDP Growth":     -0.50,
            "DXY":           -15.00,
            "Oil Price":      25.00,
        },
    },
}
