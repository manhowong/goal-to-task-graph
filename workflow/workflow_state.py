from typing import TypedDict


class WorkflowState(TypedDict):
    """State object that flows through the agent graph execution."""
    goal: str
    tasks: list[str]
    verdicts: list[dict]
    retries: int
    context: list[str]
    task_graph: dict
