"""Assigns urgency, importance, and dependency metadata to each task."""

from infrastructure.config import MAX_TOKENS, MODEL_NAME
from infrastructure.llm import get_llm
from workflow.prompts import RANKER_PROMPT
from workflow.response_schemas import RankerOutput, TaskScore


def compute_depths(task_graph: dict) -> dict[str, int]:
    """Compute dependency depth for each node in an explicit task graph."""
    by_id = {node["node_id"]: node for node in task_graph.get("nodes", [])}
    depths: dict[str, int] = {}

    def depth_of(node_id: str, visiting: set[str]) -> int:
        if node_id in depths:
            return depths[node_id]
        if node_id not in by_id or node_id in visiting:
            return 0 # unknown reference or cycle: treat as no unresolved prerequisite
        visiting.add(node_id)
        prereqs = [p for p in by_id[node_id].get("depends_on", []) if p != node_id]
        d = 1 + max((depth_of(p, visiting) for p in prereqs), default=-1)
        visiting.discard(node_id)
        depths[node_id] = d
        return d

    for node_id in by_id:
        depth_of(node_id, set())
    return depths


def build_task_graph(tasks: list[str]) -> dict:
    """Create graph nodes from the finalized task list before ranking."""
    if len(tasks) != len(set(tasks)):
        raise ValueError("Finalized task titles must be unique before ranking")

    return {
        "nodes": [
            {
                "node_id": f"task-{index:03d}",
                "title": title,
                "urgency": None,
                "importance": None,
                "depends_on": [],
            }
            for index, title in enumerate(tasks, start=1)
        ],
        "edges": [],
    }


def apply_scores(task_graph: dict, scores: list[TaskScore]) -> dict:
    """Match title-based model scores to graph nodes and add dependency edges."""
    scores_by_title = {score.task: score for score in scores}
    nodes_by_title = {node["title"]: node for node in task_graph["nodes"]}

    for node in task_graph["nodes"]:
        score = scores_by_title[node["title"]]
        node["urgency"] = score.urgency
        node["importance"] = score.importance
        node["depends_on"] = [
            nodes_by_title[dependency]["node_id"]
            for dependency in score.depends_on
            if dependency in nodes_by_title
        ]
        task_graph["edges"].extend(
            {"source": dependency, "target": node["node_id"], "type": "dependency"}
            for dependency in node["depends_on"]
        )

    return task_graph


def rank_task_graph(task_graph: dict) -> dict:
    """Order graph nodes and add rank, depth, and sequence relationships."""
    depths = compute_depths(task_graph)
    nodes = sorted(
        task_graph["nodes"],
        key=lambda node: (depths[node["node_id"]], -node["urgency"], -node["importance"]),
    )
    task_graph["nodes"] = nodes

    for rank, node in enumerate(nodes, start=1):
        node["rank"] = rank
        node["depth"] = depths[node["node_id"]]

    task_graph["edges"].extend(
        {
            "source": nodes[index]["node_id"],
            "target": nodes[index + 1]["node_id"],
            "type": "sequence",
        }
        for index in range(len(nodes) - 1)
    )
    return task_graph


def ranker(state):
    client = get_llm()
    task_graph = build_task_graph(state["tasks"])
    tasks_str = "\n".join(f'- {node["title"]}' for node in task_graph["nodes"])
    completion = client.chat.completions.parse(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": RANKER_PROMPT.format(tasks=tasks_str)}],
        max_tokens=MAX_TOKENS,
        response_format=RankerOutput,
        temperature=0,
    )
    result = completion.choices[0].message.parsed
    task_graph = apply_scores(task_graph, result.scores)
    return {"task_graph": rank_task_graph(task_graph)}
