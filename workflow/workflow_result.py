from dataclasses import asdict, dataclass
from typing import Any

from workflow.workflow_state import WorkflowState


@dataclass(frozen=True)
class WorkflowResult:
    """Completed workflow output shared by all application entry points."""

    goal: str
    thread_id: str
    task_graph: dict
    tasks: list[str]
    verdicts: list[dict]
    context: list[str]
    retries: int
    agent_steps: int

    @classmethod
    def from_state(cls, state: WorkflowState, thread_id: str, agent_steps: int):
        return cls(
            goal=state["goal"],
            thread_id=thread_id,
            task_graph=state.get("task_graph", {"nodes": [], "edges": []}),
            tasks=state.get("tasks", []),
            verdicts=state.get("verdicts", []),
            context=state.get("context", []),
            retries=state.get("retries", 0),
            agent_steps=agent_steps,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)