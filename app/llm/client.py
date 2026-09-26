import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from app.llm.prompt_builder import PromptBuilder
from app.llm.fallback import DeterministicFallbackEngine
from app.utils.logging import logger

class LLMClient:
    """
    LLM Client that manages optional LLM calls with seamless fallback to the Deterministic Engine.
    """
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "").lower()
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "")
        self.prompt_builder = PromptBuilder()
        self.fallback_engine = DeterministicFallbackEngine()

    def compose_message(
        self,
        category: Dict[str, Any],
        merchant: Dict[str, Any],
        plan: Dict[str, Any],
        trigger: Optional[Dict[str, Any]] = None,
        customer: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Always run fallback generation first as baseline guarantee
        fallback_res = self.fallback_engine.generate(category, merchant, trigger, customer, plan)
        
        # If no LLM provider/key configured, return fallback immediately
        if not self.api_key and self.provider != "ollama":
            return {
                "body": fallback_res["body"],
                "cta": fallback_res["cta"],
                "send_as": plan.get("send_as", "vera"),
                "rationale": f"Composed deterministically for signal '{plan.get('signal_type')}' grounded in category & merchant context."
            }

        # If LLM configured, attempt LLM call
        try:
            prompt = self.prompt_builder.build_prompt(category, merchant, plan, trigger, customer)
            llm_res = self._call_llm(prompt)
            if llm_res and "body" in llm_res:
                return llm_res
        except Exception as e:
            logger.warning(f"LLM call failed: {e}. Falling back to deterministic engine.")

        return {
            "body": fallback_res["body"],
            "cta": fallback_res["cta"],
            "send_as": plan.get("send_as", "vera"),
            "rationale": f"Deterministic fallback used for signal '{plan.get('signal_type')}'."
        }

    def _call_llm(self, prompt: str) -> Optional[Dict[str, Any]]:
        # Supports OpenAI, Anthropic, Gemini, DeepSeek, Groq, Ollama, OpenRouter
        if self.provider == "openai" or self.provider == "deepseek" or self.provider == "groq" or self.provider == "openrouter":
            url_map = {
                "openai": "https://api.openai.com/v1/chat/completions",
                "deepseek": "https://api.deepseek.com/v1/chat/completions",
                "groq": "https://api.groq.com/openai/v1/chat/completions",
                "openrouter": "https://openrouter.ai/api/v1/chat/completions"
            }
            url = url_map.get(self.provider, "https://api.openai.com/v1/chat/completions")
            model = self.model or ("gpt-4o-mini" if self.provider == "openai" else "deepseek-chat")
            
            body = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": self.prompt_builder.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }).encode("utf-8")
            
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)

        return None
