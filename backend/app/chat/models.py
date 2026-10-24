from dataclasses import dataclass, field
from time import time


@dataclass(frozen=True)
class ChatContext:
    knowledge_base_id: str
    conversation_id: str
    document_ids: tuple[str, ...]
    scope_key: str
    turns: tuple[dict, ...]
    query: str
    topic: str
    created_at: float = field(default_factory=time)
    knowledge_base_wide: bool = False
