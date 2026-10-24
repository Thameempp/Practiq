"""Provider adapter shared by generation and the separate answer review."""

from app.core.config import settings
from app.orchestration.runtime import check_active, current_task, request_timeout
from app.services.mcq.errors import MCQGenerationError


def make_generate_text(client):
    def generate_text(system_prompt: str, prompt: str) -> str:
        check_active()
        active_client = client.with_options(
            max_retries=0, timeout=request_timeout()
        ) if current_task.get() else client
        response = active_client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": prompt}],
            model=settings.LLM_MODEL,
            temperature=0,
            timeout=request_timeout(),
            response_format={"type": "json_object"},
        )
        check_active()
        choice = response.choices[0]
        if getattr(choice, "finish_reason", None) == "length":
            raise MCQGenerationError("The quiz response was incomplete. Please try again.")
        content = choice.message.content
        if not isinstance(content, str) or not content.strip():
            raise MCQGenerationError("The quiz service returned an empty response.")
        return content

    return generate_text
