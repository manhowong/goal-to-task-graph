"""Prompt templates and reusable instructions for task decomposition, critique, and ranking."""

DECOMPOSER_TOOL_NOTE = (
    " If deciding on a concrete task depends on a real-world fact you're not confident "
    "about (current regulations, requirements, availability), call web_search first."
)

DECOMPOSER_PROMPT = (
    "Break the following goal into a short list of concrete, actionable tasks. "
    "Each task should be a short phrase, not a sentence. No explanations."
    + DECOMPOSER_TOOL_NOTE + "\n\nGoal: {goal}"
)

DECOMPOSER_PROMPT_GROUNDED = (
    "Break the following goal into a short list of concrete, actionable tasks. "
    "Each task should be a short phrase, not a sentence. No explanations. "
    "Use the reference checklist items below where relevant."
    + DECOMPOSER_TOOL_NOTE + "\n\nGoal: {goal}\n\nReference checklist items:\n{context}"
)

CRITIC_PROMPT = (
    "For each task below, decide if it is vague (no concrete action, or no clear "
    "completion condition) or concrete. Give a one-sentence reason only if vague; "
    "otherwise return an empty string for reason. If judging a task's concreteness "
    "depends on a real-world fact you're unsure of, call web_search before deciding.\n\n"
    "Tasks:\n{tasks}"
)

RANKER_PROMPT = (
    "Score each task below on a 1-5 scale using this rubric:\n"
    "- urgency: 1 = no time pressure, 5 = immediate or blocking\n"
    "- importance: 1 = minor impact on the goal, 5 = critical to the goal\n"
    "Return each score using the task title. Also list the titles of any tasks from "
    "the same list that must finish first. "
    "Use an empty list if there are none.\n"
    "Return only the scores, no explanations.\n\nTasks:\n{tasks}"
)
