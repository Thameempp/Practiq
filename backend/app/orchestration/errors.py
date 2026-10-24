class TaskFailure(RuntimeError):
    """A controlled error whose message is safe to show in a workflow response."""


class TaskCancelled(RuntimeError):
    pass


class TaskDeadline(TimeoutError):
    pass


class OrchestrationError(RuntimeError):
    pass
