import json

from app.chat.tokens import clip_tokens
from app.core.config import settings
from app.services.retrieval.tokens import count_tokens


def retain_turns(turns) -> list[dict]:
    kept, used, seen = [], 2, set()
    for turn in sorted(turns, key=lambda item: item["created_at"], reverse=True):
        if turn["request_id"] in seen:
            continue
        seen.add(turn["request_id"])
        bounded = {**turn, "question": clip_tokens(turn["question"], 800),
                   "answer": clip_tokens(turn["answer"], 2400),
                   "topic": clip_tokens(turn["topic"], 600)}
        cost = count_tokens(json.dumps(bounded, ensure_ascii=False)) + 2
        if not kept and used + cost > settings.CHAT_MEMORY_TOKENS:
            def cost_with_answer(answer):
                return count_tokens(json.dumps({**bounded, "answer": answer}, ensure_ascii=False)) + 2
            bounded["answer"] = clip_tokens(bounded["answer"], settings.CHAT_MEMORY_TOKENS - used,
                                            counter=cost_with_answer)
            cost = count_tokens(json.dumps(bounded, ensure_ascii=False)) + 2
        if used + cost > settings.CHAT_MEMORY_TOKENS or len(kept) >= settings.CHAT_MAX_TURNS:
            break
        kept.append(bounded)
        used += cost
    return list(reversed(kept))
