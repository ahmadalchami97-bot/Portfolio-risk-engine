"""
Core computation engine.

Factor model: Return(%) = Σ [ beta_k × shock_k ]

beta_k  = % return of asset per 1 unit of shock
shock_k = factor shock in natural units (pp for rates, % for DXY/Oil)
"""

import pandas as pd
import numpy as np


def compute_results(portfolio: list, scenario: dict) -> tuple:
    """
    Compute scenario analysis results.

    Args:
        portfolio: list of dicts {name, amount, betas}
        scenario:  dict of {factor_name: shock_value}

    Returns:
        results_df:              per-asset DataFrame
        portfolio_summary:       dict of portfolio-level totals
        factor_contributions:    dict {factor: portfolio-level % contribution}
    """
    if not portfolio:
        return None, None, None

    total_invested = sum(a["amount"] for a in portfolio)
    if total_invested <= 0:
        return None, None, None

    rows = []
    for asset in portfolio:
        weight = asset["amount"] / total_invested
        betas = asset["betas"]

        # Per-factor return contribution (in %)
        factor_returns = {}
        for factor, shock in scenario.items():
            beta = betas.get(factor, 0.0)
            factor_returns[factor] = beta * shock  # result in %

        total_return_pct = sum(factor_returns.values())
        pnl = asset["amount"] * (total_return_pct / 100)
        ending_value = asset["amount"] + pnl

        rows.append(
            {
                "Asset": asset["name"],
                "Asset Class": asset.get("asset_class", "—"),
                "Invested ($)": asset["amount"],
                "Weight (%)": round(weight * 100, 2),
                "Return (%)": round(total_return_pct, 3),
                "P&L ($)": round(pnl, 2),
                "Ending Value ($)": round(ending_value, 2),
                **{f"_factor_{f}": v for f, v in factor_returns.items()},
            }
        )

    results_df = pd.DataFrame(rows)

    # Portfolio totals
    total_pnl = results_df["P&L ($)"].sum()
    total_return_pct = (total_pnl / total_invested) * 100
    ending_value = total_invested + total_pnl

    portfolio_summary = {
        "total_invested": total_invested,
        "total_pnl": total_pnl,
        "total_return_pct": total_return_pct,
        "ending_value": ending_value,
    }

    # Portfolio-level factor contributions (% contribution to portfolio return)
    factor_contributions = {}
    for factor in scenario:
        col = f"_factor_{factor}"
        if col in results_df.columns:
            # Weighted average factor contribution across assets
            weighted = (
                results_df[col] * results_df["Invested ($)"]
            ).sum() / total_invested
            factor_contributions[factor] = round(weighted, 4)

    return results_df, portfolio_summary, factor_contributions


def get_asset_factor_contributions(results_df: pd.DataFrame, scenario: dict) -> pd.DataFrame:
    """
    Return a tidy DataFrame of per-asset, per-factor return contributions (%).
    Useful for stacked bar charts.
    """
    factor_cols = [f"_factor_{f}" for f in scenario]
    available = [c for c in factor_cols if c in results_df.columns]

    long_rows = []
    for _, row in results_df.iterrows():
        for col in available:
            factor = col.replace("_factor_", "")
            long_rows.append(
                {
                    "Asset": row["Asset"],
                    "Factor": factor,
                    "Contribution (%)": round(row[col], 4),
                }
            )
    return pd.DataFrame(long_rows)
