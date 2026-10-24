import json

from app.chat.budget import input_limit, PromptBudgetError
from app.chat.tokens import clip_tokens, message_tokens


def bounded_target(target):
    answer = clip_tokens(target.answer, 4000)
    return target.model_copy(update={"answer": answer,
                                    "truncated": target.truncated or answer != target.answer})


def build_prompt(system: str, target, *, claims=(), sources=()) -> tuple[str, dict]:
    payload = {"question": target.question, "ANSWER": target.answer,
               "objection": target.objection, "artifact": target.artifact,
               "truncated": target.truncated,
               "topic_scope": {key: target.scope[key] for key in ("title", "topic_path")
                               if key in target.scope} if target.scope else None,
               "claims": [claim.model_dump() for claim in claims], "PDF_passages": []}


    def size():
        prompt = json.dumps(payload, ensure_ascii=False)
        return message_tokens([{"content": system}, {"content": prompt}])

    if size() > input_limit():
        raise PromptBudgetError("The verification request exceeds the chat token budget. Narrow the answer or objection.")
    visible = {}
    for source in sources:
        passage = {"source_id": source.id, "document_id": source.document_id,
                   "filename": source.filename, "page": source.page,
                   "text": clip_tokens(source.quote, 1200)}
        payload["PDF_passages"].append(passage)
        if size() > input_limit():
            payload["PDF_passages"].pop()
        else:
            visible[source.id] = passage
    return json.dumps(payload, ensure_ascii=False), visible
