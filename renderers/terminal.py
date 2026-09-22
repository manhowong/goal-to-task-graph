"""Terminal renderer for human-readable output in the CLI."""

from renderers.base import BaseRenderer
from workflow.workflow_result import WorkflowResult


def render_plan(task_graph: dict, thread_id: str) -> str:
    out = [
        "=" * 80,
        f"EXECUTION PLAN | Thread: {thread_id}",
        "Scale: [1 = Low, 5 = High]",
        "=" * 80,
        "",
    ]

    nodes = task_graph.get("nodes", [])

    # For readability, number the tasks by their ranks instead of using node_id directly
    rank_by_id = {node["node_id"]: node.get("rank", index) for index, node in enumerate(nodes, start=1)}

    for index, node in enumerate(nodes, start=1):
        rank = node.get("rank", index)
        dependency_ranks = [
            rank_by_id[dependency_id]
            for dependency_id in node.get("depends_on", [])
            if dependency_id in rank_by_id
        ]
        deps_str = ", ".join(f"Task {dependency_rank}" for dependency_rank in dependency_ranks) or "None"

        out.append(f"[Task {rank}] {node['title']}")
        out.append(f"- Urgency:    {score_to_dots(node['urgency'], 5)}")
        out.append(f"- Importance: {score_to_dots(node['importance'], 5)}")
        out.append(f"- Depends On: {deps_str}")
        out.append("")

    return "\n".join(out)


def score_to_dots(score: int, total: int = 5) -> str:
    """Convert score to dots, e.g. ● ● ● ● ○  (4/5)"""
    score = max(0, min(score, total)) # Ensure score is within [0, total]
    dots = ("● " * score + "○ " * (total - score)).strip()
    return f"{dots}  ({score}/{total})"


class TerminalRenderer(BaseRenderer):
    def display(self, message: str) -> None:
        print(message)

    def render(self, result: WorkflowResult) -> str:
        return render_plan(result.task_graph, result.thread_id)
