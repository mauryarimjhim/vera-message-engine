from typing import Dict, Any, List, Optional
from app.categories.base import BaseCategoryHandler

class RestaurantsCategoryHandler(BaseCategoryHandler):
    slug = "restaurants"
    tone = "fast_commercial"
    vocab_allowed = ["orders", "covers", "delivery radius", "BOGO", "thali", "IPL", "menu", "dishes"]
    vocab_taboo = ["cheap", "unhygienic", "stale", "guaranteed"]

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

        if signal_type == "ipl_match":
            match = evidence.get("match", "DC vs MI")
            time_str = evidence.get("time", "7:30pm")
            venue = evidence.get("venue", "Arun Jaitley Stadium")
            offer = evidence.get("offer", "BOGO pizza")
            body = f"Quick heads-up {name} — {match} at {venue} tonight, {time_str}. Important: Saturday IPL matches usually shift -12% restaurant covers (people watch at home). Skip the match-night promo today; instead push your {offer} (already active) as a delivery-only Saturday special. Want me to draft the Swiggy banner + an Insta story? Live in 10 min."
            cta = "binary_yes_no"
        elif signal_type == "recent_search":
            item = evidence.get("query", "Pizza BOGO")
            count = evidence.get("count", 210)
            offer = evidence.get("offer", "BOGO pizza")
            body = f"{name}, {count} people nearby are searching for '{item}'. Your {offer} is active. Should I push a delivery campaign?"
            cta = "binary_yes_no"
        elif signal_type == "review_theme":
            theme = evidence.get("theme", "delivery_late")
            n = evidence.get("occurrences", 4)
            quote = evidence.get("quote", "")
            body = f"{name}, {n} reviews in 30d flag '{theme.replace('_', ' ')}' (e.g. \"{quote[:55]}\"). I can draft empathetic public replies + a 'delivery ETA' line for Swiggy/Zomato. Want both?"
            cta = "binary_yes_no"
        elif signal_type == "perf_dip":
            metric = evidence.get("metric", "orders")
            delta = evidence.get("delta_pct", -0.3)
            pct = int(abs(float(delta)) * 100)
            offer = evidence.get("offer", "active combo")
            body = f"{name}, {metric} down {pct}% WoW — before spending on ads, let's push your {offer} on Google + delivery apps for this weekend. Draft ready in 10 min. Launch?"
            cta = "binary_yes_no"
        elif signal_type == "corporate_thali":
            locality = evidence.get("locality", "Indiranagar")
            body = f"{name}, here's a starter version — you can edit:\n\nCorporate Bulk Package for offices in {locality}:\n- 10 thalis @ ₹125 each (₹25 off retail) + free delivery\n- 25 thalis @ ₹115 each + 2 free filter coffees\n\n3 offices nearby are in your delivery radius. Want me to draft a 3-line WhatsApp to send their facilities managers?"
            cta = "open_ended"
        elif signal_type == "planning_intent":
            topic = str(evidence.get("intent_topic", "")).replace("_", " ")
            body = f"{name}, following up on your {topic} idea — here's a simple starter plan: fixed batch slots, intro pricing for the first sign-ups, and one launch post to announce it. Want me to draft the full plan + the announcement for your approval?"
            cta = "open_ended"
        elif signal_type == "milestone":
            metric = str(evidence.get("metric", "review_count")).replace("_", " ")
            now = evidence.get("value_now", 145)
            target = evidence.get("milestone_value", 150)
            gap = (target or 0) - (now or 0)
            body = f"{name}, you're at {now} {metric} — just {gap} away from {target}. That's a natural moment for a thank-you post + a small nudge to recent happy customers for a rating. Want me to draft both? Takes 2 min."
            cta = "binary_yes_no"
        else:
            offer = evidence.get("offer")
            views = evidence.get("perf_views")
            facts = []
            if views is not None:
                facts.append(f"{views} profile views in 30 days")
            fact_txt = f" ({', '.join(facts)})" if facts else ""
            offer_txt = f" Your {offer} is active." if offer else ""
            body = f"Hi {name}, peak weekend dining demand is approaching and your listing is getting traffic{fact_txt}.{offer_txt} Should I launch a weekend push on Google & social?"
            cta = "binary_yes_no"

        return {"body": body, "cta": cta}
