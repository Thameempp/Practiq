Orchestration entry point: `get_orchestrator()` in `service.py`.

```python
from app.orchestration.service import get_orchestrator

coordinator = get_orchestrator()
run = coordinator.prepare(request)  # QuestionRequest
if run.plan is None:
    response = run.decision.response()
else:
    for text in coordinator.stream(run):
        send(text)
    metadata = run.state.snapshot()
```

| Module | Responsibility |
| --- | --- |
| `routing.py` | Intent, document scope, clarification and chapter resolution |
| `router.py` | Map supported actions to explicit task plans |
| `orchestration.py` | Coordinate preparation, execution and structured MCQs |
| `state.py` | Per-request/task statuses, evidence, output and timing |
| `executor.py` | Bounded worker pool, dependency scheduling and deadlines |
| `dispatch.py`, `completion.py` | Start ready tasks and finish/stop tasks |
| `worker.py`, `runtime.py` | Task execution, safe retries and cooperative cancellation |
| `events.py` | Bounded streaming events and public error rendering |
| `tasks.py`, `validation.py` | Plan contracts and dependency validation |
| `*_workflow.py`, `cross_document.py` | Adapters for existing generation/retrieval services |
| `service.py` | Thread-safe process lifetime and shutdown |

`execution.py` supports callers with an existing RoutingDecision. Import the worker executor from `executor.py`.

Independent tasks may run concurrently through `ExecutionPlan(max_concurrency=...)`. PDF summary plans stay sequential. Consolidation depends on every PDF summary succeeding; unrelated PDF summaries continue after a failure.

Task retries default to zero: provider adapters already handle request retries. Opt-in task retries never replay emitted text or retry an SDK call still running after a timeout.

Cancellation is cooperative. A blocking SDK call may finish after its task times out; its result is discarded, and it retains a pool slot until it exits. Request and workflow deadlines do not create replacement worker pools. API disconnects, provider boundaries, retry waits and shutdown observe cancellation.

Available workflows: document QA, cross-document QA, full-PDF/chapter summaries, explicit consolidation, validated MCQs and selective answer verification. `verification_workflow.py` streams progress, canonical citations and a structured verdict; it uses the existing executor deadlines and cancellation. Unimplemented specialist agents remain unsupported. State is request-local; document/clarification persistence remains in the documents package.

Details and defaults: `backend/project/multi-agent-logic.txt`.

SSE also emits `agent` lifecycle metadata (`id`, `name`, `state` as `started`/`finished`). `agent_activity.py` tracks BaseAgent calls and QA generation; the frontend shows the latest active agent beneath PDF and clears activity when streaming settles. These events never enter answer text.
