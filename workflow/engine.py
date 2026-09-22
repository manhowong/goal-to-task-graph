"""Builds and executes the LangGraph workflow that plans a goal into ranked tasks."""

import sqlite3
import uuid
from collections.abc import Callable

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from renderers.base import BaseRenderer
from infrastructure.config import DB_PATH
from workflow.workflow_result import WorkflowResult
from workflow.workflow_state import WorkflowState
from workflow.nodes.critic import critic
from workflow.nodes.decomposer import decomposer
from workflow.nodes.ranker import ranker
from workflow.nodes.rag import retrieve_context
from workflow.nodes.supervisor import supervisor_router


def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("decomposer", decomposer)
    graph.add_node("critic", critic)
    graph.add_node("ranker", ranker)

    routes = {
        "retrieve_context": "retrieve_context",
        "decomposer": "decomposer",
        "critic": "critic",
        "ranker": "ranker",
    }
    graph.add_conditional_edges(START, supervisor_router, routes)
    for node in ["retrieve_context", "decomposer", "critic"]:
        graph.add_conditional_edges(node, supervisor_router, routes)

    graph.add_edge("ranker", END)
    return graph


graph = build_graph()
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
app = graph.compile(checkpointer=SqliteSaver(conn))


def generate_task_graph(
    goal: str,
    thread_id: str | None = None,
    renderer: BaseRenderer | None = None,
    on_progress: Callable[[str], None] | None = None,
):
    """Run the workflow without printing and optionally render its result."""
    thread_id = thread_id or str(uuid.uuid4())

    def report(message: str) -> None:
        if on_progress:
            on_progress(message)

    # Takes a goal string and returns the dict .invoke() needs
    session_input = lambda g: {
        "goal": g,
        "tasks": [],
        "verdicts": [],
        "retries": 0,
        "context": [],
        "task_graph": {"nodes": [], "edges": []},
    }

    # config controls how the run relates to persistence and limits
    # thread_id: tells the checkpointer which saved state to resume from.
    # Same thread_id across multiple .invoke() calls → each call picks up
    # wherever plan was left off. Different thread_id → starts with an empty
    # plan, like a fresh conversation.
    # recursion_limit: limits total graph steps for this call, independent of
    # MAX_RETRIES (it protects against the graph looping in some way the code's
    # own logic didn't anticipate.)
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 20}

    agent_steps = 0

    # Stream node updates step-by-step as they execute
    for event in app.stream(session_input(goal), config=config, stream_mode="updates"):
        for node_name, node_output in event.items():
            agent_steps += 1

            if node_name == "retrieve_context":
                report("🔎 Retriving context from knowledge base ...")
                count = len(node_output.get("context", []))
                report(f"Retrieved {count} context chunks.\n")

            elif node_name == "decomposer":
                report("📝 Analysing goal and writing tasks ...")
                count = len(node_output.get("tasks", []))
                report(f"Generated {count} tasks.\n")

            elif node_name == "critic":
                report("🤔 Evaluating tasks ...")
                verdicts = node_output.get("verdicts", [])
                vague_tasks = [v for v in verdicts if v["vague"]]
                vague_count = len(vague_tasks)

                if vague_count == 0:
                    status_msg = "All tasks passed concreteness check (0 vague tasks)."
                else:
                    status_msg = f"{vague_count} vague task(s) flagged for revision."

                report(f"Evaluated {len(verdicts)} tasks: {status_msg}\n")

            elif node_name == "ranker":
                report("🔢 Ranking tasks by dependency, urgency, and importance ...")

    state = app.get_state(config).values
    result = WorkflowResult.from_state(state, thread_id, agent_steps)
    report(f"✅ Execution plan finalised! Total planning steps: {agent_steps}\n")
    return renderer.render(result) if renderer else result
