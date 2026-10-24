import logging

from app.chat.store import append_turn
from app.chat.prompts import NOT_FOUND_MESSAGE
from app.services.verification.storage import save_target

logger = logging.getLogger(__name__)


def remember_exchange(run):
    chat = run.decision.chat
    if chat is None or run.state.status != "succeeded" or run.state.cancel.is_set():
        return
    tasks = list(run.state.tasks.values())
    answer = "".join(task.text for task in tasks).strip()
    if not answer:
        return
    try:
        save_target(run, answer)
    except Exception as error:
        logger.warning("Verification target could not be saved (%s)", type(error).__name__)
    if not any(task.evidence for task in tasks) or answer == NOT_FOUND_MESSAGE:
        return
    if run.decision.verification:
        answer = next((task.result.get("corrected_answer") for task in tasks
                       if isinstance(task.result, dict) and task.result.get("corrected_answer")), answer)
    turn = {"request_id": run.state.request_id, "created_at": chat.created_at,
            "document_ids": list(chat.document_ids), "scope_key": chat.scope_key,
            "knowledge_base_wide": chat.knowledge_base_wide,
            "question": run.decision.verification.question if run.decision.verification else run.decision.question,
            "answer": answer, "topic": chat.topic}
    try:
        append_turn(chat.knowledge_base_id, chat.conversation_id, turn)
    except Exception as error:
        logger.warning("Conversation memory could not be saved (%s)", type(error).__name__)
