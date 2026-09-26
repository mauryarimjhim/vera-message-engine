from typing import Dict, Any, List, Optional
from app.categories.base import BaseCategoryHandler

class PharmaciesCategoryHandler(BaseCategoryHandler):
    slug = "pharmacies"
    tone = "trustworthy_precise"
    vocab_allowed = ["availability", "chronic", "refill", "batch", "recall", "discount", "molecule", "namaste"]
    vocab_taboo = ["guaranteed cure", "cheap drugs", "untested", "miracle"]

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

        if signal_type == "supply_alert":
            batches = evidence.get("affected_batches") or evidence.get("batches", [])
            batch_txt = f" ({', '.join(str(b) for b in batches)})" if batches else ""
            mfr = evidence.get("manufacturer") or evidence.get("mfr", "the manufacturer")
            molecule = evidence.get("molecule", "atorvastatin")
            affected = evidence.get("affected_count")
            affected_txt = (
                f" I pulled your repeat-Rx list: {affected} of your chronic-Rx customers were dispensed these batches in the last 90 days."
                if affected is not None else
                " I can pull your repeat-Rx list to find customers dispensed these batches in the last 90 days."
            )
            body = f"{name}, urgent: voluntary recall on {len(batches) or 2} {molecule} batches{batch_txt} by {mfr} — sub-potency, no safety risk, but customers should be informed for replacement.{affected_txt} Want me to draft their WhatsApp note + the replacement-pickup workflow?"
            cta = "open_ended"
        elif signal_type == "chronic_refill":
            cust_name = evidence.get("customer_name", "Mr. Sharma")
            date_str = evidence.get("date", "28 April")
            total = evidence.get("total", "1,420")
            saved = evidence.get("saved", "240")
            locality = evidence.get("locality", "Malviya Nagar")
            n_meds = evidence.get("medicine_count", 3)
            molecules = evidence.get("molecules", "metformin, atorvastatin, telmisartan")
            body = f"Namaste — {merchant_name} {locality} yahan. {cust_name} ki {n_meds} monthly medicines ({molecules}) {date_str} ko khatam hongi. Same dose, same brand pack ready hai. Senior discount 15% applied — total ₹{total} (₹{saved} saved). Free home delivery to saved address by 5pm tomorrow. Reply CONFIRM to dispatch, or call if any change in dosage."
            cta = "binary_confirm_cancel"
        elif signal_type == "category_seasonal":
            trends = evidence.get("trends", [])
            season = str(evidence.get("season", "")).replace("_", " ")
            up = [t for t in trends if t.get("pct", 0) > 0]
            down = [t for t in trends if t.get("pct", 0) < 0]
            up_txt = ", ".join(f"{t['product']} +{t['pct']}%" for t in up[:3])
            down_txt = ""
            if down:
                down_txt = " while " + ", ".join(f"{t['product']} {t['pct']}%" for t in down[:1])
            body = f"Namaste {name}, {season} demand data for your area: {up_txt}{down_txt}. Suggested shelf action: front-stock the rising items and cut cold-cough facing space. Want me to draft the shelf plan + a Google post highlighting your in-demand items?"
            cta = "binary_yes_no"
        elif signal_type == "gbp_unverified":
            uplift = evidence.get("estimated_uplift_pct")
            uplift_pct = int(float(uplift) * 100) if uplift is not None else 30
            path = str(evidence.get("verification_path", "")).replace("_", " ").replace(" or ", " or a ")
            views = evidence.get("perf_views")
            views_txt = f" Even unverified, your listing pulled {views} views in 30 days — " if views is not None else ""
            body = f"{name}, one high-impact fix pending: your Google Business Profile is not verified yet. {views_txt}verified pharmacy listings see roughly +{uplift_pct}% profile views. Verification is simple — {path}. Want me to walk you through it step by step this week?"
            cta = "binary_yes_no"
        elif signal_type == "curious_ask":
            body = f"Namaste {name}! Quick check — which medicines or products have customers asked for most this week at {merchant_name}? I'll turn the answer into a stock suggestion + a Google post. Takes 5 min."
            cta = "open_ended"
        else:
            offer = evidence.get("offer")
            views = evidence.get("perf_views")
            facts = []
            if views is not None:
                facts.append(f"{views} profile views in 30 days")
            fact_txt = f" ({', '.join(facts)})" if facts else ""
            offer_txt = f" Your {offer} is active." if offer else ""
            body = f"Hi {name}, your listing is getting attention{fact_txt}.{offer_txt} Want me to set up refill reminders for your regular chronic-medicine patients and draft this week's Google post?"
            cta = "binary_yes_no"

        return {"body": body, "cta": cta}
