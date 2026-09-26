import re
from typing import Dict, Any, List
from app.categories import get_category_handler

class ResponseValidator:
    """
    Validates composed messages against compliance, grounding, CTA structure, and safety rules.
    """
    def validate(
        self,
        body: str,
        cta: str,
        category_slug: str,
        context_facts: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        errors = []

        if not body or len(body.strip()) == 0:
            errors.append("Body is empty.")
            return False, errors

        # 1. URL Check (Meta WhatsApp policy violation check in challenge brief & testing brief §F.4)
        if re.search(r'https?://[^\s]+', body):
            errors.append("Message body contains HTTP/HTTPS URLs (Forbidden by policy harness).")

        # 2. Category Taboo Check
        handler = get_category_handler(category_slug)
        taboo_violations = handler.validate_voice(body)
        if taboo_violations:
            errors.extend(taboo_violations)

        # 3. CTA check
        allowed_ctas = ["binary_yes_no", "open_ended", "multi_choice_slot", "binary_confirm_cancel", "none"]
        if cta not in allowed_ctas:
            errors.append(f"Invalid CTA type '{cta}'. Must be one of {allowed_ctas}")

        # 4. Body length check
        if len(body) > 600:
            errors.append(f"Message body length ({len(body)} chars) exceeds maximum readable threshold.")

        return len(errors) == 0, errors
