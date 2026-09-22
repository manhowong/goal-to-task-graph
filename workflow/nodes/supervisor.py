"""Controls workflow routing between context retrieval, decomposition, critique, and ranking."""

from workflow.workflow_state import WorkflowState

MAX_RETRIES = 2


def supervisor_router(state: WorkflowState) -> str:
    if not state.get("context"):
        return "retrieve_context"

    tasks = state.get("tasks", [])
    if not tasks:
        return "decomposer"

    verdicts = state.get("verdicts", [])

    if not verdicts:
        return "critic"

    if any(v["vague"] for v in verdicts) and state.get("retries", 0) < MAX_RETRIES:
        return "decomposer"

    return "ranker"
