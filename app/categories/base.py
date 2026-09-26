from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseCategoryHandler(ABC):
    slug: str
    tone: str
    vocab_allowed: List[str]
    vocab_taboo: List[str]

    @abstractmethod
    def format_offer_copy(self, offer_title: str, price: Optional[str] = None) -> str:
        """Format an offer in category-appropriate copy."""
        pass

    @abstractmethod
    def generate_fallback_message(
        self,
        merchant_name: str,
        owner_name: Optional[str],
        signal_type: str,
        evidence: Dict[str, Any],
        cta_type: str
    ) -> Dict[str, str]:
        """Generate category-specific fallback body and CTA."""
        pass

    def validate_voice(self, body: str) -> List[str]:
        """Check for taboo words in body."""
        violations = []
        body_lower = body.lower()
        for taboo in self.vocab_taboo:
            if taboo.lower() in body_lower:
                violations.append(f"Taboo word '{taboo}' found in category {self.slug}")
        return violations
