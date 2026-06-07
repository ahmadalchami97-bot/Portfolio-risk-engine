"""
Rule-based narrative generator.

Produces plain-English summaries of scenario results for
non-technical users (e.g. investment committees, clients).
"""

from src.templates import FACTORS


def _fmt_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def _fmt_usd(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}${abs(value):,.0f}"


def _magnitude_label(abs_val: float) -> str:
    if abs_val < 0.5:
        return "marginal"
    if abs_val < 2.0:
        return "moderate"
    if abs_val < 5.0:
        return "significant"
    return "severe"


def generate_narrative(
    portfolio_summary: dict,
    factor_contributions: dict,
    results_df,
    scenario: dict,
) -> str:
    """
    Generate a plain-English paragraph explaining the scenario outcome.

    Returns a markdown string.
    """
    total_return = portfolio_summary["total_return_pct"]
    total_pnl = portfolio_summary["total_pnl"]
    total_invested = portfolio_summary["total_invested"]

    direction = "gain" if total_pnl >= 0 else "loss"
    direction_verb = "gained" if total_pnl >= 0 else "lost"
    magnitude = _magnitude_label(abs(total_return))

    # Sort factors by absolute contribution
    sorted_factors = sorted(
        factor_contributions.items(), key=lambda x: abs(x[1]), reverse=True
    )
    active_factors = [(f, v) for f, v in sorted_factors if abs(v) >= 0.05]

    # Sort assets by P&L
    best_asset = results_df.loc[results_df["Return (%)"].idxmax()]
    worst_asset = results_df.loc[results_df["Return (%)"].idxmin()]

    # --- Build narrative sections ---

    # Opening sentence
    opening = (
        f"Under this macro scenario, the portfolio {direction_verb} "
        f"**{_fmt_pct(total_return)}** ({_fmt_usd(total_pnl)}), "
        f"representing a **{magnitude} {direction}** on the invested capital of "
        f"${total_invested:,.0f}."
    )

    # Factor drivers
    if not active_factors:
        driver_text = "No macro factors produced a material impact under this scenario."
    else:
        top = active_factors[0]
        factor_label = FACTORS.get(top[0], {}).get("label", top[0])
        driver_dir = "positive" if top[1] >= 0 else "negative"
        driver_text = (
            f"The dominant driver was **{factor_label}**, which contributed "
            f"**{_fmt_pct(top[1])}** to the portfolio return ({driver_dir} impact)."
        )

        if len(active_factors) >= 2:
            second = active_factors[1]
            second_label = FACTORS.get(second[0], {}).get("label", second[0])
            second_dir = "reinforcing" if (top[1] * second[1]) > 0 else "partially offsetting"
            driver_text += (
                f" **{second_label}** was a {second_dir} factor, "
                f"contributing **{_fmt_pct(second[1])}**."
            )

    # Asset winners and losers
    asset_text = ""
    if len(results_df) > 1:
        if best_asset["Return (%)"] > 0.01:
            asset_text += (
                f"**{best_asset['Asset']}** was the strongest performer, "
                f"returning {_fmt_pct(best_asset['Return (%)'])} "
                f"({_fmt_usd(best_asset['P&L ($)'])}). "
            )
        if worst_asset["Return (%)"] < -0.01:
            asset_text += (
                f"**{worst_asset['Asset']}** was the hardest hit, "
                f"returning {_fmt_pct(worst_asset['Return (%)'])} "
                f"({_fmt_usd(worst_asset['P&L ($)'])})."
            )

    # Macro context
    active_shocks = {f: v for f, v in scenario.items() if abs(v) > 0}
    context_parts = []
    for factor, shock in active_shocks.items():
        unit = FACTORS.get(factor, {}).get("unit", "")
        label = FACTORS.get(factor, {}).get("label", factor)
        sign = "+" if shock >= 0 else ""
        if unit == "pp":
            context_parts.append(f"{label} {sign}{shock:.2f} pp")
        else:
            context_parts.append(f"{label} {sign}{shock:.1f}%")

    context_text = ""
    if context_parts:
        context_text = (
            "The scenario assumed the following macro shocks: "
            + ", ".join(context_parts) + "."
        )

    # Hedge effectiveness note
    hedge_text = ""
    if len(results_df) > 1:
        positive_assets = results_df[results_df["Return (%)"] > 0]
        negative_assets = results_df[results_df["Return (%)"] < 0]
        if not positive_assets.empty and not negative_assets.empty:
            hedge_text = (
                f"The portfolio showed **partial diversification**: "
                f"{len(positive_assets)} asset(s) posted gains while "
                f"{len(negative_assets)} asset(s) declined, "
                f"which cushioned the overall impact."
            )
        elif negative_assets.empty:
            hedge_text = "All assets posted positive returns under this scenario, reflecting broad macro tailwinds."
        else:
            hedge_text = (
                "All assets declined under this scenario, "
                "suggesting the portfolio has concentrated exposure to these macro factors."
            )

    sections = [opening, driver_text]
    if asset_text:
        sections.append(asset_text)
    if hedge_text:
        sections.append(hedge_text)
    if context_text:
        sections.append(context_text)

    return "\n\n".join(sections)
