"""Flags vague or non-actionable tasks before ranking and finalization."""

from infrastructure.llm import get_llm, run_llm
from workflow.prompts import CRITIC_PROMPT
from workflow.response_schemas import CriticOutput


def critic(state):
    client = get_llm()
    tasks_str = "\n".join(f"- {t}" for t in state["tasks"])
    result = run_llm(
        client,
        [{"role": "user", "content": CRITIC_PROMPT.format(tasks=tasks_str)}],
        CriticOutput,
    )
    return {"verdicts": [v.model_dump() for v in result.verdicts]}
