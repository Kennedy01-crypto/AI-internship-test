import json
import os
import re
from typing import Any

import google.generativeai as genai


class GeminiProcessor:
    SYSTEM_PROMPT = """
You are an assistant that converts diaspora client requests into structured JSON.
Always return valid JSON only, with no markdown.

Required output shape:
{
  "intent": "registration|banking|compliance|legal_support|unknown",
  "risk_score": 0.0,
  "employee_category": "finance|operations|legal",
  "steps": ["step 1", "step 2"],
  "messages": {
    "whatsapp": "short message",
    "email": "longer professional message",
    "sms": "very short message"
  }
}

Rules:
1) risk_score must be a float between 0.0 and 1.0 inclusive.
2) If uncertain, use intent = "unknown" and employee_category = "operations".
3) Never output text outside the JSON object.
"""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def process(self, user_input: str) -> dict[str, Any]:
        prompt = f"{self.SYSTEM_PROMPT}\n\nUser input:\n{user_input}"
        response = self.model.generate_content(prompt)
        raw_text = response.text.strip() if hasattr(response, "text") and response.text else "{}"
        parsed = self._safe_parse_json(raw_text)
        return self._normalize_output(parsed)

    @staticmethod
    def _safe_parse_json(text: str) -> dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        return {}

    @staticmethod
    def _normalize_output(payload: dict[str, Any]) -> dict[str, Any]:
        valid_intents = {"registration", "banking", "compliance", "legal_support", "unknown"}
        valid_categories = {"finance", "operations", "legal"}

        intent = str(payload.get("intent", "unknown")).lower()
        if intent not in valid_intents:
            intent = "unknown"

        employee_category = str(payload.get("employee_category", "operations")).lower()
        if employee_category not in valid_categories:
            employee_category = "operations"

        risk_raw = payload.get("risk_score", 0.0)
        try:
            risk_score = float(risk_raw)
        except (TypeError, ValueError):
            risk_score = 0.0
        risk_score = max(0.0, min(1.0, risk_score))

        messages = payload.get("messages", {}) or {}
        if not isinstance(messages, dict):
            messages = {}

        steps = payload.get("steps", [])
        if not isinstance(steps, list):
            steps = []

        return {
            "intent": intent,
            "risk_score": risk_score,
            "employee_category": employee_category,
            "steps": [str(step) for step in steps],
            "messages": {
                "whatsapp": str(messages.get("whatsapp", "")),
                "email": str(messages.get("email", "")),
                "sms": str(messages.get("sms", "")),
            },
        }
