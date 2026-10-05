import logging

from groq import APIError, APITimeoutError, AsyncGroq

from app.core.config import settings
from app.models.task import Task

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You summarize a user's open tasks. Give a short summary, then the 3 tasks "
    "to do first, with a one-line reason each. Be concise."
)

client: AsyncGroq | None = None

class AIServiceError(Exception):
    pass

class AITimeoutError(AIServiceError):
    pass

def get_client() -> AsyncGroq:
    global client
    if client is None:
        client = AsyncGroq(api_key=settings.GROQ_API_KEY, timeout=20.0, max_retries=1)
    return client

def build_prompt(tasks: list[Task]) -> str:
    lines = []
    for t in tasks:
        due = t.due_date.date().isoformat() if t.due_date else "no due date"
        lines.append(f"- [{t.status.value}] {t.title} (due: {due}): {t.description[:200]}")
    return "\n".join(lines)

async def summarize_tasks(tasks: list[Task]) -> str:
    if not settings.GROQ_API_KEY:
        raise AIServiceError("AI is not configured")
    try:
        response = await get_client().chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role":"system", "content":SYSTEM_PROMPT},
                {"role":"user", "content":build_prompt(tasks)}
            ],
            max_completion_tokens=800
        )
    except APITimeoutError:
        logger.error("Groq request timed out")
        raise AITimeoutError("AI request timed out")
    except APIError:
        logger.exception("Groq request failed")
        raise AIServiceError("AI request failed")
    return (response.content[0].message.content or "").strip()