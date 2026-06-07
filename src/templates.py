"""
Asset templates with pre-calibrated factor betas.

Beta interpretation: % return of asset per 1 unit of factor shock.
  - Rate factors (Fed Funds Rate, US 10Y Yield, Inflation):
      1 unit = 1 percentage point (pp). e.g. Fed hikes 1pp → +100bps.
  - Market factors (DXY, Oil Price):
      1 unit = 1% change. e.g. DXY +5 → dollar up 5%.

IMPORTANT: All betas are assumption-based, not statistically estimated.
They reflect directional consensus from financial economics literature
and standard institutional practice. See page 5 (Assumptions) for full
rationale and limitations.
"""

ASSET_TEMPLATES = {
    "Gold": {
        "icon": "🥇",
        "description": "Physical gold / Gold ETF (e.g. GLD)",
        "asset_class": "Commodity",
        "betas": {
            "Fed Funds Rate": -2.0,
            "US 10Y Yield":   -3.0,
            "Inflation":       3.0,   # reduced from 5.0 — empirical CPI sensitivity is moderate
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
            "US 10Y Yield":   -8.0,   # compressed vs true duration (~16y) to avoid double-counting
            "Inflation":      -3.0,
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
            "DXY":            -0.5,   # CHF/USD exposure: USD strengthens → CHF assets worth less in USD
            "Oil Price":       0.0,
        },
    },
}

# ── Detailed beta rationale (used by Assumptions page) ────────────────────────
# Each entry: (sign_correct, magnitude_note, economic_rationale)

BETA_RATIONALE = {
    "Gold": {
        "Fed Funds Rate": (
            "✅ Correct",
            "Moderate — ~2% loss per 100bps hike is conservative",
            "Higher real rates raise the opportunity cost of holding non-yielding gold. "
            "Well-documented in World Gold Council research.",
        ),
        "US 10Y Yield": (
            "✅ Correct",
            "Moderate — some studies find -4% to -6%; we use -3%",
            "Gold prices track real 10Y yields closely (gold vs. TIPS spread). "
            "Negative relationship is among the most robust in commodity research.",
        ),
        "Inflation": (
            "✅ Correct",
            "Conservative — gold's inflation hedge is empirically unreliable in short windows",
            "Gold is widely cited as an inflation hedge, but empirical evidence is mixed. "
            "It performed well in the 1970s and 2020–2022 but near-zero sensitivity in 2010s. "
            "Beta of +3.0 reflects a moderate assumption.",
        ),
        "DXY": (
            "✅ Correct",
            "Reasonable — literature range is -0.5 to -1.2 per 1% USD move",
            "Gold is priced in USD; a stronger dollar mechanically lowers gold's USD price. "
            "One of the most consistent relationships in commodity markets.",
        ),
        "Oil Price": (
            "✅ Correct",
            "Small — commodity co-movement only",
            "Weak positive correlation via the joint inflation/commodity complex. "
            "Not a structural relationship.",
        ),
    },
    "US Equities": {
        "Fed Funds Rate": (
            "✅ Correct",
            "Moderate — empirical range is -2% to -5% per 100bps",
            "Tighter monetary policy raises discount rates and reduces earnings growth expectations. "
            "Broadly supported across multiple market cycles.",
        ),
        "US 10Y Yield": (
            "⚠️ Regime-dependent",
            "Moderate — sign depends on whether yields rise from growth or inflation",
            "In a growth-driven yield rise, equities and yields can be positively correlated. "
            "In an inflation/Fed-driven rise (e.g. 2022), both fall. "
            "The assumed -2.0 applies to a rate-headwind regime.",
        ),
        "Inflation": (
            "✅ Correct",
            "Moderate — varies by type of inflation",
            "Demand-pull inflation can be equity-positive; cost-push inflation and "
            "Fed reaction risk are equity-negative. Net assumption: moderately negative.",
        ),
        "DXY": (
            "✅ Correct",
            "Small — S&P 500 has ~40% international revenue",
            "A stronger dollar reduces the USD value of foreign earnings. "
            "Small magnitude reflects partial hedging and sector diversification.",
        ),
        "Oil Price": (
            "✅ Correct",
            "Near-neutral — energy sector gains roughly offset consumer drag",
            "S&P 500 is diversified; oil rises benefit energy names but hurt consumer "
            "discretionary and industrials. Net effect is near zero.",
        ),
    },
    "US Treasuries": {
        "Fed Funds Rate": (
            "✅ Correct",
            "Moderate — less than full duration; short end transmission is imperfect",
            "Fed hikes transmit to the long end via rate expectations, but with dampening. "
            "Long bonds are more driven by 10Y yield directly.",
        ),
        "US 10Y Yield": (
            "✅ Correct",
            "Compressed vs true duration (~16y for TLT) to avoid double-counting",
            "Modified duration of TLT is ~16–17 years, implying ~-16% per 100bps. "
            "We use -8.0 to avoid double-counting with the Fed Funds Rate beta. "
            "This is the most significant model simplification in the template.",
        ),
        "Inflation": (
            "✅ Correct",
            "Moderate — inflation erodes real value of fixed coupons and pushes yields up",
            "Fixed nominal coupon payments are worth less in real terms. "
            "Inflation also triggers Fed action which raises nominal yields further.",
        ),
        "DXY": (
            "✅ Correct",
            "Near-zero — minor safe-haven correlation",
            "Treasuries are a global safe haven; dollar strength often accompanies Treasury demand. "
            "Very small positive. Directionally plausible.",
        ),
        "Oil Price": (
            "✅ Correct",
            "Near-zero — indirect via inflation channel",
            "Higher oil → higher inflation → higher yields → bond price decline. "
            "Marginal effect.",
        ),
    },
    "Swiss Real Estate": {
        "Fed Funds Rate": (
            "✅ Correct",
            "Smaller than US assets — Swiss RE is partly insulated from Fed policy",
            "Global rate correlation exists, but Switzerland's SNB operates independently. "
            "Swiss mortgage market and valuations are less directly tied to the Fed.",
        ),
        "US 10Y Yield": (
            "✅ Correct",
            "Moderate — listed RE trades like a long-duration bond",
            "Swiss REITs are valued on discounted cash flows; higher yields compress valuations. "
            "Standard real estate duration sensitivity.",
        ),
        "Inflation": (
            "✅ Correct",
            "Moderate — Swiss RE leases often indexed to CPI",
            "Swiss commercial and residential leases frequently include CPI escalators. "
            "Real asset with good inflation pass-through.",
        ),
        "DXY": (
            "✅ Correct",
            "Small negative — currency translation for USD-based investor",
            "Swiss RE is priced in CHF. When USD strengthens (DXY↑), CHF weakens, "
            "so USD-based returns fall. Sign is correct from a USD investor's perspective.",
        ),
        "Oil Price": (
            "✅ Correct",
            "Zero — no direct channel identified",
            "Swiss real estate has no significant direct exposure to oil price movements. "
            "Any indirect effect via inflation is captured by the Inflation beta.",
        ),
    },
}

FACTORS = {
    "Fed Funds Rate": {
        "unit": "pp",
        "label": "Fed Funds Rate",
        "description": "Federal Reserve policy rate change",
        "example": "+1.0 pp = Fed hikes 100bps",
        "min": -2.0,
        "max":  2.0,
        "step": 0.25,
        "baseline": 4.50,
        "baseline_label": "4.50%",
        "icon": "🏦",
    },
    "US 10Y Yield": {
        "unit": "pp",
        "label": "US 10Y Yield",
        "description": "10-Year US Treasury yield change",
        "example": "+0.5 pp = 10Y rises 50bps",
        "min": -2.0,
        "max":  2.0,
        "step": 0.25,
        "baseline": 4.45,
        "baseline_label": "4.45%",
        "icon": "📜",
    },
    "Inflation": {
        "unit": "pp",
        "label": "Inflation (CPI)",
        "description": "Annual CPI inflation change",
        "example": "+1.0 pp = inflation rises from 3% to 4%",
        "min": -2.0,
        "max":  2.0,
        "step": 0.25,
        "baseline": 2.80,
        "baseline_label": "2.8%",
        "icon": "🔥",
    },
    "DXY": {
        "unit": "%",
        "label": "DXY (US Dollar Index)",
        "description": "Percentage change in US Dollar Index",
        "example": "+5.0% = dollar strengthens 5%",
        "min": -5.0,          # normal mode
        "max":  5.0,
        "min_stress": -15.0,  # stress testing mode
        "max_stress":  15.0,
        "step":  0.5,
        "baseline": 99.0,
        "baseline_label": "99.0",
        "icon": "💵",
    },
    "Oil Price": {
        "unit": "%",
        "label": "Oil Price (WTI)",
        "description": "Percentage change in WTI crude oil",
        "example": "+15.0% = oil rises 15%",
        "min": -5.0,          # normal mode
        "max":  5.0,
        "min_stress": -25.0,  # stress testing mode
        "max_stress":  25.0,
        "step":  1.0,
        "baseline": 65.0,
        "baseline_label": "$65.0/bbl",
        "icon": "🛢️",
    },
}

PREBUILT_SCENARIOS = {
    "— Select a template —": None,
    "🏦 Fed Hiking Cycle": {
        "description": "The Fed raises rates to cool the economy. Yields rise, the dollar strengthens, and rate-sensitive assets come under pressure.",
        "shocks": {
            "Fed Funds Rate":  1.00,
            "US 10Y Yield":    0.50,
            "Inflation":       0.25,
            "DXY":             2.00,
            "Oil Price":       0.00,
        },
    },
    "📉 Fed Cutting Cycle": {
        "description": "The Fed eases policy to support growth. Yields fall, the dollar weakens, and rate-sensitive assets benefit.",
        "shocks": {
            "Fed Funds Rate": -1.00,
            "US 10Y Yield":   -0.50,
            "Inflation":      -0.25,
            "DXY":            -2.00,
            "Oil Price":       0.00,
        },
    },
    "💪 Strong Dollar": {
        "description": "A broad US dollar rally. Non-USD and dollar-priced commodity assets face translation headwinds.",
        "shocks": {
            "Fed Funds Rate":  0.00,
            "US 10Y Yield":    0.25,
            "Inflation":       0.00,
            "DXY":             5.00,
            "Oil Price":      -2.00,
        },
    },
    "🪙 Weak Dollar": {
        "description": "A broad US dollar decline. Commodities and non-USD assets are supported.",
        "shocks": {
            "Fed Funds Rate":  0.00,
            "US 10Y Yield":   -0.25,
            "Inflation":       0.00,
            "DXY":            -5.00,
            "Oil Price":       2.00,
        },
    },
    "🛢️ Oil Shock": {
        "description": "A sharp spike in crude oil prices feeds into inflation. Requires Stress Mode for the full oil move.",
        "shocks": {
            "Fed Funds Rate":  0.00,
            "US 10Y Yield":    0.25,
            "Inflation":       1.00,
            "DXY":            -1.00,
            "Oil Price":      15.00,
        },
    },
    "🌧️ Risk-Off Flight To Safety": {
        "description": "Markets sell off and capital flows to safe havens. Yields fall, the dollar firms, and oil declines on growth fears.",
        "shocks": {
            "Fed Funds Rate": -0.50,
            "US 10Y Yield":   -0.75,
            "Inflation":      -0.50,
            "DXY":             2.00,
            "Oil Price":      -3.00,
        },
    },
}
