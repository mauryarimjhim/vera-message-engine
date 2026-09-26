from typing import Dict, Any, List, Optional
from app.categories.base import BaseCategoryHandler

class GymsCategoryHandler(BaseCategoryHandler):
    slug = "gyms"
    tone = "coaching_motivational"
    vocab_allowed = ["memberships", "trials", "retention", "attendance", "ad spend", "conversion", "classes"]
    vocab_taboo = ["guaranteed loss", "miracle body", "steroids", "cheap"]

    def format_offer_copy(self, offer_title: str, price: Optional[str] = None) -> str:
        if price:
            return f"{offer_title} @ ₹{price}"
        return offer_title

    def generate_fallback_message(
        self,
        merchant_name: str,
        owner_name: Optional[str],
        signal_type: str,
        evidence: Dict[str, Any],
        cta_type: str
    ) -> Dict[str, str]:
        name = owner_name or merchant_name

        if signal_type == "seasonal_dip":
            metric = evidence.get("metric", "views")
            delta = evidence.get("delta_pct", -0.3)
            pct = int(abs(float(delta)) * 100)
            views = evidence.get("perf_views")
            views_txt = f" ({views} views in 30 days)" if views is not None else ""
            body = f"{name}, your {metric} are down {pct}% this week{views_txt} — but this is the normal April-June post-resolution lull, so hold off on ad spend and save it for Sept-Oct when conversion picks up. Better move now: retention. Want me to draft a 'summer attendance challenge' for your current members?"
            cta = "binary_yes_no"
        elif signal_type == "customer_lapsed":
            cust_name = evidence.get("customer_name", "there")
            weeks = evidence.get("weeks", 8)
            days = evidence.get("days_since_last_visit")
            since_txt = f"{days} days (about {weeks} weeks)" if days is not None else f"about {weeks} weeks"
            focus = str(evidence.get("previous_focus", "")).replace("_", "-")
            focus_txt = f" toward your {focus} goal" if focus else ""
            body = f"Hi {cust_name} 👋 {name} from {merchant_name} here. It's been {since_txt} — happens to most members at some point, no judgment. We can pick you back up{focus_txt}. Want me to hold a free session slot for you this week? Reply YES — no commitment, no auto-charge."
            cta = "binary_yes_no"
        elif signal_type == "trial_followup":
            cust_name = evidence.get("customer_name", "there")
            slot = evidence.get("slot1", "")
            slot_txt = f" — {slot} works?" if slot else " — what time works for you?"
            body = f"Hi {cust_name}, {name} from {merchant_name}. You tried us out recently — how did it feel? Let's lock your next session while the momentum is there{slot_txt}"
            cta = "binary_yes_no"
        elif signal_type == "perf_spike":
            metric = evidence.get("metric", "calls")
            delta = evidence.get("delta_pct", 0.15)
            pct = int(float(delta) * 100)
            driver = str(evidence.get("likely_driver", "")).replace("_", " ")
            driver_txt = f" — likely driven by your {driver}" if driver else ""
            offer = evidence.get("offer")
            offer_txt = f" Your {offer} offer is live, so we can strike while interest is hot." if offer else ""
            body = f"{name}, good news: {metric} are up {pct}% week-on-week{driver_txt}.{offer_txt} Want me to boost this with a follow-up post targeting the same audience?"
            cta = "binary_yes_no"
        elif signal_type == "planning_intent":
            topic = str(evidence.get("intent_topic", "")).replace("_", " ")
            offer = evidence.get("offer")
            offer_txt = f" You already run {offer} — we can bundle around it." if offer else ""
            body = f"{name}, following up on your {topic} idea — here's a simple starter: 4-week batch, fixed morning/evening slots, intro price for first 10 sign-ups.{offer_txt} Want me to draft the full plan + a launch post you can approve?"
            cta = "open_ended"
        else:
            offer = evidence.get("offer")
            views = evidence.get("perf_views")
            facts = []
            if views is not None:
                facts.append(f"{views} profile views in 30 days")
            fact_txt = f" ({', '.join(facts)})" if facts else ""
            offer_txt = f" Your {offer} is live." if offer else ""
            body = f"Hi {name}, your listing is getting traction{fact_txt}.{offer_txt} Want me to promote your trial offer to nearby fitness seekers this week?"
            cta = "binary_yes_no"

        return {"body": body, "cta": cta}
