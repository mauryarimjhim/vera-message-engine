import re
from typing import Dict, Any, List

class IntentEngine:
    """
    Classifies merchant and customer responses into actionable intents.
    Priority order:
    1. AUTO_REPLY
    2. HOSTILE
    3. YES
    4. NO
    5. LATER
    6. OFF_TOPIC
    7. QUESTION
    8. OBJECTION
    """
    AUTO_REPLY_PATTERNS = [
        r"thank you for contacting",
        r"our team will respond",
        r"we will get back to you",
        r"automated assistant",
        r"auto-reply",
        r"jaankari ke liye",
        r"sujhaav.*team tak",
        r"bahut-bahut shukriya",
        r"currently unavailable",
        r"out of office"
    ]

    HOSTILE_PATTERNS = [
        r"stop messaging", r"useless spam", r"harass", r"get lost", r"abuse",
        r"don't disturb", r"spam"
    ]

    YES_PATTERNS = [
        r"ok\s+lets\s+do\t*it", r"let'?s do it", r"\byes\b", r"\bdo it\b", r"\blaunch\b",
        r"\bokay\b", r"\bok\b", r"\bsure\b", r"\bconfirm\b", r"\bproceed\b", r"\bsend\b",
        r"\bgo ahead\b", r"\byeah\b", r"\bha\b", r"\bhaa\b", r"\bchalega\b", r"\bready\b"
    ]

    NO_PATTERNS = [
        r"\bnot interested\b", r"\bdon'?t\b", r"\bno\b", r"\bstop\b", r"\bcancel\b",
        r"\bnever\b", r"\bna\b", r"\bnahi\b", r"\bno thanks\b"
    ]

    LATER_PATTERNS = [
        r"\blater\b", r"\btomorrow\b", r"\bnot now\b", r"\bbusy\b", r"\bnext week\b",
        r"\bbaad mein\b", r"\bbaad me\b"
    ]

    OFF_TOPIC_PATTERNS = [
        r"\bgst\b", r"\btax\b", r"\baccounting\b"
    ]

    def classify_intent(self, message: str, conversation_turns: List[Dict[str, Any]] = None) -> str:
        if not message:
            return "UNKNOWN"

        msg_clean = message.strip().lower()

        # Check for duplicate consecutive messages (auto-reply heuristic)
        if conversation_turns and len(conversation_turns) >= 2:
            merchant_msgs = [t["message"].strip().lower() for t in conversation_turns if t.get("from_role") == "merchant"]
            if len(merchant_msgs) >= 2 and merchant_msgs[-1] == merchant_msgs[-2]:
                return "AUTO_REPLY"

        # 1. AUTO_REPLY
        for pat in self.AUTO_REPLY_PATTERNS:
            if re.search(pat, msg_clean):
                return "AUTO_REPLY"

        # 2. HOSTILE
        for pat in self.HOSTILE_PATTERNS:
            if re.search(pat, msg_clean):
                return "HOSTILE"

        # 3. YES (Evaluate BEFORE question mark check so "Ok lets do it. Whats next?" is YES)
        for pat in self.YES_PATTERNS:
            if re.search(pat, msg_clean):
                return "YES"

        # 4. NO
        for pat in self.NO_PATTERNS:
            if re.search(pat, msg_clean):
                return "NO"

        # 5. LATER
        for pat in self.LATER_PATTERNS:
            if re.search(pat, msg_clean):
                return "LATER"

        # 6. OFF_TOPIC
        for pat in self.OFF_TOPIC_PATTERNS:
            if re.search(pat, msg_clean):
                return "OFF_TOPIC"

        # 7. QUESTION
        if "?" in message or any(w in msg_clean for w in ["what", "how", "when", "where", "why", "cost", "price"]):
            return "QUESTION"

        # 8. NEW_INTENT
        if any(p in msg_clean for p in ["instead", "promote my", "switch to", "rather promote", "can you promote"]):
            return "NEW_INTENT"

        # 9. OBJECTION
        if any(w in msg_clean for w in ["expensive", "staff", "busy", "difficult", "why should"]):
            return "OBJECTION"

        return "UNKNOWN"
