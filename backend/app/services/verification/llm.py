from app.chat.budget import validate_messages
from app.core.config import settings
from app.orchestration.runtime import check_active, request_timeout
from app.services.verification.models import VerificationError


def make_generate_text(client):
    def generate(system: str, prompt: str) -> str:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        validate_messages(messages)
        check_active()
        response = client.with_options(max_retries=0, timeout=request_timeout()).chat.completions.create(
            messages=messages, model=settings.LLM_MODEL, temperature=0,
            response_format={"type": "json_object"},
            max_completion_tokens=settings.CHAT_OUTPUT_TOKENS, timeout=request_timeout())
        check_active()
        choice = response.choices[0]
        if getattr(choice, "finish_reason", None) == "length" or not choice.message.content:
            raise VerificationError("The verification response was incomplete. The answer could not be confirmed.")
        return choice.message.content
    return generate
