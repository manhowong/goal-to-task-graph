"""Breaks a goal into a list of concrete tasks, revising vague ones when needed."""

from infrastructure.llm import get_llm, run_llm
from workflow.prompts import DECOMPOSER_PROMPT, DECOMPOSER_PROMPT_GROUNDED, DECOMPOSER_TOOL_NOTE
from workflow.response_schemas import TaskList


def decomposer(state):
    client = get_llm()
    prior_verdicts = state.get("verdicts", [])
    latest = prior_verdicts[-len(state["tasks"]):] if prior_verdicts else []
    flagged = [v for v in latest if v["vague"]]

    if flagged:
        flagged_str = "\n".join(f'- "{v["task"]}": {v["reason"]}' for v in flagged)
        prompt = (
            "Replace only the flagged tasks below with concrete, actionable tasks "
            "that address the stated reason. Keep all other tasks unchanged. "
            "Return the full corrected task list." + DECOMPOSER_TOOL_NOTE + "\n\n"
            f"Current tasks:\n" + "\n".join(f"- {t}" for t in state["tasks"]) + "\n\n"
            f"Flagged:\n{flagged_str}"
        )
    else:
        context = state.get("context", [])
        if context:
            context_str = "\n".join(f"- {c}" for c in context)
            prompt = DECOMPOSER_PROMPT_GROUNDED.format(goal=state["goal"], context=context_str)
        else:
            prompt = DECOMPOSER_PROMPT.format(goal=state["goal"])

    result = run_llm(client, [{"role": "user", "content": prompt}], TaskList)
    retries = state.get("retries", 0) + (1 if flagged else 0)
    return {"tasks": result.tasks, "retries": retries, "verdicts": []} # clear verdicts from previous round
