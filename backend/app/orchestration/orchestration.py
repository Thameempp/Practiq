"""The application coordinator: resolve scope, build a plan, execute, expose state."""

import logging
from dataclasses import dataclass

from app.orchestration.executor import TaskExecutor
from app.orchestration.events import render_event
from app.orchestration.errors import OrchestrationError
from app.orchestration.validation import validate_plan
from app.orchestration.mcq_workflow import resolve_quiz
from app.orchestration.router import build_plan
from app.orchestration.routing import route_request
from app.orchestration.state import WorkflowState
from app.chat.context import attach_history
from app.chat.persistence import remember_exchange

logger = logging.getLogger(__name__)


@dataclass
class WorkflowRun:
    decision: object
    plan: object
    state: WorkflowState


class Orchestrator:
    def __init__(self, *, executor=None, resolver=route_request, planner=build_plan):
        self.executor = executor or TaskExecutor()
        self.resolver, self.planner = resolver, planner


    def prepare(self, request):
        try:
            return self.from_decision(attach_history(self.resolver(request), request))
        except Exception as error:
            raise OrchestrationError("The workflow could not be prepared. Please try again.") from error


    def from_decision(self, decision, **options):
        plan = self.planner(decision, **options)
        if plan is not None:
            validate_plan(plan)
        state = WorkflowState(decision.action)
        if plan is None:
            state.status = "waiting_input" if decision.action != "unsupported_task" else "unsupported"
        return WorkflowRun(decision, plan, state)


    def events(self, run):
        if run.plan is None:
            return
        try:
            yield from self.executor.events(run.plan, run.state)
            remember_exchange(run)
        finally:
            logger.info("Workflow finished: %s", run.state.snapshot())


    def stream(self, run):
        events = self.events(run)
        try:
            for event in events:
                text = render_event(event)
                if text:
                    yield text
        finally:
            events.close()


    def quiz(self, request):
        run = self.from_decision(
            resolve_quiz(request), count=request.count, exclude_questions=request.exclude_questions,
        )
        list(self.events(run))
        if run.state.status != "succeeded":
            raise OrchestrationError(next(task.error for task in run.state.tasks.values() if task.error))
        return run.state.tasks["mcq"].result


