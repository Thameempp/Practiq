import json


def encode_event(event):
    if event.kind in {"text", "progress", "agent", "sources", "citation", "verification"}:
        return f"event: {event.kind}\ndata: {json.dumps(event.data)}\n\n"
    if event.kind == "task_finished" and event.data.error:
        return f"event: error\ndata: {json.dumps(event.data.error)}\n\n"
    return None
