# agent/long_term_memory.py
from database.db import SessionLocal
from database.models import AgentMemory
from utils.logger import log # type: ignore
from datetime import datetime

# ──────────────────────────────────────────
# RECORD TRANSACTION OUTCOME
# called after every completed/failed sale
# ──────────────────────────────────────────
def record_outcome(
    category: str,
    platform: str,
    asking_price: float,
    final_price: float,
    days_to_sell: int,
    success: bool
):
    """
    Record the outcome of a transaction.
    Updates avg price ratio and days to sell.
    """
    db = SessionLocal()
    try:
        # find existing memory for this category+platform
        memory = db.query(AgentMemory).filter_by(
            category=category,
            platform=platform
        ).first()

        price_ratio = round(final_price / asking_price, 2) if asking_price else 0

        if not memory:
            # first time seeing this category+platform combo
            memory = AgentMemory(
                category        = category,
                platform        = platform,
                avg_days_sold   = float(days_to_sell),
                avg_price_ratio = price_ratio,
                success_count   = 1 if success else 0,
                fail_count      = 0 if success else 1,
                insights        = []
            )
            db.add(memory)
            log("long_term_memory",
                f"New memory created: {category} on {platform}")
        else:
            # update running averages
            total = memory.success_count + memory.fail_count

            if success:
                memory.success_count += 1
                # rolling average for days to sell
                memory.avg_days_sold = round(
                    (memory.avg_days_sold * total + days_to_sell) / (total + 1), 1
                )
                # rolling average for price ratio
                memory.avg_price_ratio = round(
                    (memory.avg_price_ratio * total + price_ratio) / (total + 1), 2
                )
            else:
                memory.fail_count += 1

            memory.updated_at = datetime.now()
            log("long_term_memory",
                f"Memory updated: {category} on {platform} | ratio:{price_ratio}")

        db.commit()

    except Exception as e:
        log("long_term_memory", f"❌ Failed to record outcome: {e}", "ERROR")
        db.rollback()
    finally:
        db.close()

# ──────────────────────────────────────────
# GET INSIGHTS FOR CATEGORY
# ──────────────────────────────────────────
def get_insights(category: str) -> list:
    """
    Get all memory records for a category
    across all platforms.
    """
    db = SessionLocal()
    try:
        records = db.query(AgentMemory).filter_by(
            category=category
        ).all()

        insights = []
        for r in records:
            total = r.success_count + r.fail_count
            success_rate = round(
                r.success_count / total * 100
            ) if total > 0 else 0

            insights.append({
                "platform":        r.platform,
                "avg_days_sold":   r.avg_days_sold,
                "avg_price_ratio": r.avg_price_ratio,
                "success_rate":    success_rate,
                "total_listings":  total,
            })

        # sort by success rate descending
        insights.sort(key=lambda x: x["success_rate"], reverse=True)
        return insights

    except Exception as e:
        log("long_term_memory", f"❌ Failed to get insights: {e}", "ERROR")
        return []
    finally:
        db.close()

# ──────────────────────────────────────────
# GET BEST PLATFORM FOR CATEGORY
# ──────────────────────────────────────────
def get_best_platform(category: str) -> str | None:
    """
    Returns the best performing platform
    for a given category based on past data.
    Returns None if no data yet.
    """
    insights = get_insights(category)
    if not insights:
        log("long_term_memory",
            f"No past data for {category}, using default logic")
        return None

    best = insights[0]  # already sorted by success rate
    log("long_term_memory",
        f"Best platform for {category}: {best['platform']} "
        f"({best['success_rate']}% success rate)")
    return best["platform"]

# ──────────────────────────────────────────
# GET EXPECTED PRICE RATIO
# ──────────────────────────────────────────
def get_expected_price_ratio(category: str, platform: str) -> float:
    """
    Returns expected final/asking price ratio
    for negotiation strategy.
    Default 0.85 if no data.
    """
    db = SessionLocal()
    try:
        memory = db.query(AgentMemory).filter_by(
            category=category,
            platform=platform
        ).first()

        if memory and memory.avg_price_ratio:
            return memory.avg_price_ratio
        return 0.85  # default fallback

    except Exception as e:
        log("long_term_memory", f"❌ Error: {e}", "ERROR")
        return 0.85
    finally:
        db.close()

# ──────────────────────────────────────────
# ADD INSIGHT NOTE
# ──────────────────────────────────────────
def add_insight(category: str, platform: str, note: str):
    """
    Add a text insight/learning for a
    category+platform combination.
    """
    db = SessionLocal()
    try:
        memory = db.query(AgentMemory).filter_by(
            category=category,
            platform=platform
        ).first()

        if memory:
            insights = memory.insights or []
            insights.append({
                "note":      note,
                "timestamp": datetime.now().isoformat()
            })
            # keep only last 20 insights
            memory.insights = insights[-20:]
            db.commit()
            log("long_term_memory", f"Insight added: {note}")

    except Exception as e:
        log("long_term_memory", f"❌ Failed to add insight: {e}", "ERROR")
        db.rollback()
    finally:
        db.close()

# ──────────────────────────────────────────
# SUMMARY FOR DASHBOARD
# ──────────────────────────────────────────
def get_summary() -> dict:
    """
    Get overall agent learning summary
    for dashboard display.
    """
    db = SessionLocal()
    try:
        all_records = db.query(AgentMemory).all()

        total_success = sum(r.success_count for r in all_records)
        total_fail    = sum(r.fail_count for r in all_records)
        total         = total_success + total_fail

        avg_ratio = round(
            sum(r.avg_price_ratio or 0 for r in all_records) /
            len(all_records), 2
        ) if all_records else 0

        return {
            "total_transactions":  total,
            "success_rate":        round(total_success / total * 100) if total else 0,
            "avg_price_ratio":     avg_ratio,
            "categories_learned":  len(set(r.category for r in all_records)),
            "platforms_used":      len(set(r.platform for r in all_records)),
        }

    except Exception as e:
        log("long_term_memory", f"❌ Summary error: {e}", "ERROR")
        return {}
    finally:
        db.close()