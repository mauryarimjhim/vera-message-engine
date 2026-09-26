from typing import Dict, Any, List, Optional
from app.categories.base import BaseCategoryHandler

class DentistsCategoryHandler(BaseCategoryHandler):
    slug = "dentists"
    tone = "peer_clinical"
    vocab_allowed = ["fluoride varnish", "caries", "cleaning", "consultation", "root canal", "recall"]
    vocab_taboo = ["cure", "guaranteed", "100% safe", "miracle", "cheap"]

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
        dr_prefix = f"Dr. {owner_name}" if owner_name else merchant_name
        
        if signal_type == "recent_search":
            query = evidence.get("query", "Dental Check Up")
            count = evidence.get("count", 190)
            price = evidence.get("price", "299")
            body = f"{dr_prefix}, {count} people nearby searched for '{query}'. Your ₹{price} check-up offer is live. Should I promote it?"
            cta = "binary_yes_no"
        elif signal_type == "research_digest":
            item = evidence.get("title", "3-month fluoride recall trial")
            source = evidence.get("source", "JIDA Oct 2026, p.14")
            count = evidence.get("trial_n", 2100)
            pct = evidence.get("reduction_pct", 38)
            body = f"{dr_prefix}, JIDA's Oct issue landed. One item relevant to your high-risk adult patients — {count}-patient trial showed 3-month fluoride recall cuts caries recurrence {pct}% better than 6-month. Worth a look (2-min abstract). Want me to pull it + draft a patient-ed WhatsApp you can share? — {source}"
            cta = "open_ended"
        elif signal_type == "recall_due":
            cust_name = evidence.get("customer_name", "Patient")
            months = evidence.get("months", 5)
            price = evidence.get("price", "299")
            slot1 = evidence.get("slot1", "Wed 5 Nov, 6pm")
            slot2 = evidence.get("slot2", "Thu 6 Nov, 5pm")
            body = f"Hi {cust_name}, {merchant_name} here 🦷 It's been {months} months since your last visit — your 6-month cleaning recall is due. Apke liye 2 slots ready hain: {slot1} ya {slot2}. ₹{price} cleaning + complimentary fluoride. Reply 1 for Wed, 2 for Thu, or tell us a time that works."
            cta = "multi_choice_slot"
        elif signal_type == "perf_dip":
            metric = evidence.get("metric", "calls")
            delta = evidence.get("delta_pct", -0.5)
            pct = int(abs(float(delta)) * 100)
            ctr = evidence.get("merchant_ctr")
            peer = evidence.get("peer_ctr")
            ctr_note = ""
            if ctr is not None and peer is not None:
                ctr_note = f"CTR is {ctr:.3f} vs peer median {peer:.3f} — listing clicks aren't converting to calls. "
            body = f"{dr_prefix}, your {metric} dropped {pct}% week-on-week ({ctr_note or 'worth a quick listing check'}). Your active cleaning offer can help recover intent-led calls. Want me to draft a Google post + WhatsApp reply template?"
            cta = "binary_yes_no"
        elif signal_type == "renewal_due":
            days = evidence.get("days_remaining", 12)
            plan = evidence.get("plan", "Pro")
            amount = evidence.get("renewal_amount", "4999")
            body = f"{dr_prefix}, your {plan} plan renews in {days} days (₹{amount}). Before renewal, I can refresh stale Google posts and align your ₹{evidence.get('price', '299')} cleaning offer with current search demand. Want the renewal + growth checklist?"
            cta = "binary_yes_no"
        elif signal_type == "compliance_regulation":
            title = evidence.get("title", "DCI radiograph dose limit update")
            deadline = evidence.get("deadline", "2026-12-15")
            source = evidence.get("source", "DCI circular")
            eff_txt = "" if deadline in title else f" (effective {deadline})"
            body = f"{dr_prefix}, compliance heads-up: {title}{eff_txt}. {source}. I can draft a 1-paragraph staff SOP + patient FAQ snippet for your desk. Want me to send it?"
            cta = "binary_yes_no"
        elif signal_type == "festival":
            festival = evidence.get("festival", "Diwali")
            days = evidence.get("days_until", 30)
            offer = evidence.get("offer", "Dental Cleaning @ ₹299")
            body = f"{dr_prefix}, {festival} is {days} days out — family check-up searches usually spike 10 days before. Your {offer} is active. Should I schedule a pre-festival Google post + WhatsApp blast draft?"
            cta = "binary_yes_no"
        elif signal_type == "winback":
            days = evidence.get("days_since_expiry", 38)
            lapsed = evidence.get("lapsed_customers", 24)
            body = f"{dr_prefix}, your Pro plan lapsed {days} days ago — {lapsed} patients were added to lapsed recall since then. Win-back window is open: I can reactivate your ₹{evidence.get('price', '299')} cleaning offer post on Google. Proceed?"
            cta = "binary_yes_no"
        elif signal_type == "review_theme":
            theme = evidence.get("theme", "wait_time")
            n = evidence.get("occurrences", 3)
            quote = evidence.get("quote", "")
            body = f"{dr_prefix}, {n} recent reviews mention '{theme.replace('_', ' ')}' (e.g. \"{quote[:60]}\"). I can draft a reply template + a small process tweak post for Google. Want me to send both?"
            cta = "binary_yes_no"
        elif signal_type == "cde_opportunity":
            title = evidence.get("title", "IDA webinar")
            credits = evidence.get("credits", 2)
            fee = evidence.get("fee", "free_for_members")
            fee_txt = "free for members" if fee == "free_for_members" else fee
            body = f"{dr_prefix}, quick one: '{title}' is worth {credits} CDE credits and {fee_txt}. I can block the seat and add a reminder to your calendar. Want me to register you?"
            cta = "binary_yes_no"
        elif signal_type == "competitor_opened":
            comp = evidence.get("competitor_name", "a new clinic")
            dist = evidence.get("distance_km", 1)
            their = evidence.get("their_offer", "")
            offer = evidence.get("offer")
            price = evidence.get("price")
            their_txt = f" — they're running {their}" if their else ""
            if offer:
                own_txt = f" Your {offer} is still live, so you're competitive."
            elif price:
                own_txt = f" Your ₹{price} offer is still live, so you're competitive."
            else:
                own_txt = ""
            body = f"{dr_prefix}, {comp} opened {dist} km from your clinic{their_txt}.{own_txt} Want me to refresh your Google post + listing photos this week to defend your local search rank?"
            cta = "binary_yes_no"
        else:
            offer = evidence.get("offer")
            price = evidence.get("price")
            locality = evidence.get("locality")
            views = evidence.get("perf_views")
            facts = []
            if views is not None:
                facts.append(f"{views} profile views in the last 30 days")
            if locality:
                facts.append(f"in {locality}")
            fact_txt = f" — {facts[0]}" if facts else ""
            offer_txt = f" Your {offer} is live." if offer else (f" Your ₹{price} offer is live." if price else "")
            body = f"{dr_prefix}, your listing pulled{fact_txt}{offer_txt} Want me to draft a local check-up promotion to convert those views into appointments?"
            cta = "binary_yes_no"
            
        return {"body": body, "cta": cta}
