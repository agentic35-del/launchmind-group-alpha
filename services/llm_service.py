import json
import re
from openai import OpenAI

from config import Settings


class LLMService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.model = Settings.OPENAI_MODEL

    def _clean_json_text(self, text: str) -> str:
        text = text.strip()

        # Remove markdown code fences if present
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        # Extract the first JSON object if extra text exists
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]

        # Remove trailing commas before } or ]
        text = re.sub(r",\s*([}\]])", r"\1", text)

        return text.strip()

    def json_response(self, system_prompt: str, user_prompt: str) -> dict:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw_text = response.output_text.strip()
        cleaned_text = self._clean_json_text(raw_text)

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM did not return valid JSON.\n\n"
                f"RAW OUTPUT:\n{raw_text}\n\n"
                f"CLEANED OUTPUT:\n{cleaned_text}"
            ) from exc