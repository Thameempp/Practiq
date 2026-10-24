"""Keep disconnect checks responsive even while provider tasks produce no text."""

import anyio
from starlette.concurrency import iterate_in_threadpool, run_in_threadpool

from app.orchestration.orchestration import render_event
from app.api.stream_events import encode_event
from time import monotonic


def response_headers(run):
    return {"cache-control": "no-cache", "x-accel-buffering": "no",
            "x-workflow-id": run.state.request_id}


async def stream_workflow(coordinator, run, connection, *, sse=False):
    events = coordinator.events(run)
    heartbeat = monotonic()
    try:
        if await connection.is_disconnected():
            run.state.cancel.set()
        async for event in iterate_in_threadpool(events):
            if await connection.is_disconnected():
                run.state.cancel.set()
                break
            text = encode_event(event) if sse else render_event(event)
            if text:
                yield text
            elif sse and monotonic() - heartbeat >= 10:
                yield ": keep-alive\n\n"
                heartbeat = monotonic()
        if sse and not run.state.cancel.is_set():
            yield "event: done\ndata: null\n\n"
    finally:
        if run.state.status == "running":
            run.state.cancel.set()
        with anyio.CancelScope(shield=True):
            await run_in_threadpool(events.close)
