from google import genai

from app.config import LLM_API_KEY, LLM_MODEL

_client = genai.Client(api_key=LLM_API_KEY)


def generate_text(prompt: str, system_instruction: str | None = None) -> str:
    """Send a prompt to the LLM and return its text response."""
    config = {"system_instruction": system_instruction} if system_instruction else {}
    response = _client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config=config,
    )
    return response.text or ""