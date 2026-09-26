from typing import Dict, Any, List, Optional
from app.categories.base import BaseCategoryHandler

class SalonsCategoryHandler(BaseCategoryHandler):
    slug = "salons"
    tone = "visual_practical"
    vocab_allowed = ["bookings", "haircut", "styling", "beauty", "bridal", "skin-prep", "reviews"]
    vocab_taboo = ["cheap", "unprofessional", "miracle", "guaranteed"]

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
        greeting = owner_name or merchant_name

        if signal_type == "recent_search":
            service = evidence.get("query", "Haircut & Styling")
            count = evidence.get("count", 150)
            price = evidence.get("price", "199")
            body = f"Hi {greeting}! {count} people nearby are looking for '{service}'. Your ₹{price} active offer is ready. Should I push it to local searchers?"
            cta = "binary_yes_no"
        elif signal_type == "bridal_followup":
            cust_name = evidence.get("customer_name", "Kavya")
            days = evidence.get("days_to_wedding", 196)
            price = evidence.get("price", "2,499")
            body = f"Hi {cust_name} 💍 {greeting} from {merchant_name} here. {days} days to your wedding — perfect window to start the 30-day skin-prep program before serious bridal bookings roll in. ₹{price} covers 4 sessions + a take-home kit. Want me to block your preferred Saturday 4pm slot for the first session next week?"
            cta = "binary_yes_no"
        elif signal_type == "curious_ask":
            body = f"Hi {greeting}! Quick check — what service has been most asked-for this week at {merchant_name}? I'll turn the answer into a Google post + a WhatsApp reply draft. Takes 5 min."
            cta = "open_ended"
        elif signal_type == "festival":
            festival = evidence.get("festival", "Diwali")
            days = evidence.get("days_until", 30)
            offer = evidence.get("offer")
            price = evidence.get("price")
            if offer:
                offer_txt = f" Your {offer} is live."
            elif price:
                offer_txt = f" Your ₹{price} offer is live."
            else:
                offer_txt = ""
            body = f"Hi {greeting}! {festival} is {days} days out — bridal and party-styling bookings usually spike 2-3 weeks before.{offer_txt} Want me to schedule a festive Google post + WhatsApp blast to your repeat customers now, so you lock slots early?"
            cta = "binary_yes_no"
        elif signal_type == "winback":
            days = evidence.get("days_since_expiry", 38)
            lapsed = evidence.get("lapsed_customers", 24)
            dip = evidence.get("perf_dip_pct")
            dip_txt = f" and views dipped {int(abs(float(dip)) * 100)}%" if dip is not None else ""
            body = f"Hi {greeting}, your plan lapsed {days} days ago{dip_txt} — {lapsed} customers moved to lapsed since then. The win-back window is open: I can reactivate your offers and send a 'we miss you' WhatsApp draft to those {lapsed} customers. Proceed?"
            cta = "binary_yes_no"
        elif signal_type == "dormant_with_vera":
            days = evidence.get("days_since_last_merchant_message", 38)
            topic = str(evidence.get("last_topic", "")).replace("_", " ")
            views = evidence.get("perf_views")
            views_txt = f" Your listing pulled {views} views in the last 30 days." if views is not None else ""
            body = f"Hi {greeting}, it's been {days} days since we last spoke about {topic}.{views_txt} Want me to pick up where we left off and draft this week's promotion?"
            cta = "binary_yes_no"
        else:
            offer = evidence.get("offer")
            price = evidence.get("price")
            views = evidence.get("perf_views")
            locality = evidence.get("locality")
            facts = []
            if views is not None:
                facts.append(f"{views} profile views in 30 days")
            if locality:
                facts.append(f"customers in {locality}")
            fact_txt = f" ({', '.join(facts)})" if facts else ""
            if offer:
                offer_txt = f" and your {offer} is live"
            elif price:
                offer_txt = f" and your ₹{price} offer is live"
            else:
                offer_txt = ""
            body = f"Hi {greeting}! Your listing is getting attention{fact_txt}{offer_txt}. Want me to draft a weekend beauty package promotion to convert those views into bookings?"
            cta = "binary_yes_no"

        return {"body": body, "cta": cta}
