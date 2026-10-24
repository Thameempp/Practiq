"""Shared accounting for complete prompts, history and stored memory."""

from app.services.retrieval.tokens import count_tokens

MESSAGE_OVERHEAD = 16


def message_tokens(messages) -> int:
    return sum(count_tokens(message["content"]) + MESSAGE_OVERHEAD for message in messages)


def clip_tokens(text: str, limit: int, *, counter=count_tokens) -> str:
    if limit <= 0:
        return ""
    if counter(text) <= limit:
        return text
    low, high = 0, len(text)
    while low < high:
        middle = (low + high + 1) // 2
        if counter(text[:middle]) <= limit:
            low = middle
        else:
            high = middle - 1
    return text[:low]


def turn_messages(turn) -> list[dict]:
    return [{"role": "user", "content": turn["question"]},
            {"role": "assistant", "content": turn["answer"]}]
