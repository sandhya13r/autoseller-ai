# agent/feedback_engine.py
from agent import long_term_memory
from utils.logger import log
from datetime import datetime

# ──────────────────────────────────────────
# PROCESS COMPLETED TRANSACTION
# called after every delivery confirmation
# ──────────────────────────────────────────
def process_outcome(
    item_id: str,
    category: str,
    platform: str,
    asking_price: float,
    final_price: float,
    created_at: datetime,
    delivered_at: datetime,
    success: bool
):
    """
    Process the outcome of a completed transaction.
    Updates long term memory and generates insights.
    """
    log("feedback_engine", f"Processing outcome for item: {item_id}")

    # calculate days to sell
    days = (delivered_at - created_at).days if success else 0

    # record in long term memory
    long_term_memory.record_outcome(
        category      = category,
        platform      = platform,
        asking_price  = asking_price,
        final_price   = final_price,
        days_to_sell  = days,
        success       = success
    )

    # generate insight note
    if success:
        price_ratio = round(final_price / asking_price * 100)
        insight = (
            f"Sold in {days} days at {price_ratio}% "
            f"of asking price on {platform}"
        )
        long_term_memory.add_insight(category, platform, insight)
        log("feedback_engine",
            f"✅ Success recorded: {insight}", "SUCCESS")
    else:
        insight = f"Failed to sell on {platform} after listing"
        long_term_memory.add_insight(category, platform, insight)
        log("feedback_engine",
            f"❌ Failure recorded for {category} on {platform}")

# ──────────────────────────────────────────
# ADJUST PRICING STRATEGY
# ──────────────────────────────────────────
def get_pricing_adjustment(
    category: str,
    platform: str,
    base_price: float
) -> dict:
    """
    Suggest price adjustments based on
    historical performance data.
    """
    insights = long_term_memory.get_insights(category)

    # find this platform's data
    platform_data = next(
        (i for i in insights if i["platform"] == platform),
        None
    )

    if not platform_data:
        log("feedback_engine",
            f"No history for {category}/{platform}, using base price")
        return {
            "adjusted_price":  base_price,
            "adjustment":      0,
            "confidence":      "low",
            "reason":          "No historical data available"
        }

    avg_ratio = platform_data["avg_price_ratio"]
    success_rate = platform_data["success_rate"]

    # if items sell well above asking → we're underpricing
    if avg_ratio > 0.95 and success_rate > 70:
        adjusted = round(base_price * 1.08)
        reason = f"Items sell at {round(avg_ratio*100)}% — you can price higher"
        adjustment = "+8%"

    # if items struggle to sell → we're overpricing
    elif avg_ratio < 0.75 or success_rate < 40:
        adjusted = round(base_price * 0.92)
        reason = f"Success rate {success_rate}% — lower price for faster sale"
        adjustment = "-8%"

    else:
        adjusted = base_price
        reason = "Price is well calibrated based on history"
        adjustment = "0%"

    confidence = (
        "high" if platform_data["total_listings"] >= 5
        else "medium" if platform_data["total_listings"] >= 2
        else "low"
    )

    log("feedback_engine",
        f"Price adjustment for {category}: {adjustment} "
        f"(confidence: {confidence})")

    return {
        "adjusted_price": adjusted,
        "adjustment":     adjustment,
        "confidence":     confidence,
        "reason":         reason
    }

# ──────────────────────────────────────────
# GET NEGOTIATION STRATEGY
# ──────────────────────────────────────────
def get_negotiation_strategy(
    category: str,
    platform: str
) -> dict:
    """
    Suggest negotiation strategy based on
    historical buyer behavior for this category.
    """
    insights = long_term_memory.get_insights(category)

    platform_data = next(
        (i for i in insights if i["platform"] == platform),
        None
    )

    if not platform_data:
        return {
            "style":       "balanced",
            "firmness":    0.7,
            "max_discount": 15,
            "reason":      "Default strategy — no history"
        }

    avg_ratio = platform_data["avg_price_ratio"]

    # buyers in this category tend to negotiate hard
    if avg_ratio < 0.80:
        return {
            "style":        "firm",
            "firmness":     0.85,
            "max_discount": 10,
            "reason":       f"Buyers negotiate hard here — be firm"
        }

    # buyers tend to accept quickly
    elif avg_ratio > 0.92:
        return {
            "style":        "flexible",
            "firmness":     0.6,
            "max_discount": 20,
            "reason":       f"Buyers accept easily — can be flexible"
        }

    else:
        return {
            "style":        "balanced",
            "firmness":     0.75,
            "max_discount": 15,
            "reason":       f"Balanced negotiation works well here"
        }

# ──────────────────────────────────────────
# GET FULL FEEDBACK REPORT
# ──────────────────────────────────────────
def get_report() -> dict:
    """
    Get full feedback report for dashboard.
    Shows what the agent has learned.
    """
    summary = long_term_memory.get_summary()

    report = {
        "summary":   summary,
        "timestamp": datetime.now().isoformat(),
        "message":   _generate_report_message(summary)
    }

    log("feedback_engine", "Report generated for dashboard")
    return report

def _generate_report_message(summary: dict) -> str:
    if not summary or summary.get("total_transactions", 0) == 0:
        return "No transactions recorded yet. Complete a sale to start learning!"

    total    = summary["total_transactions"]
    rate     = summary["success_rate"]
    ratio    = summary["avg_price_ratio"]
    cats     = summary["categories_learned"]

    return (
        f"Learned from {total} transactions across "
        f"{cats} categories. "
        f"Average success rate: {rate}%. "
        f"Sellers typically get {round(ratio*100)}% of asking price."
    )