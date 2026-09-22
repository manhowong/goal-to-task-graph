"""Pydantic schemas used for structured LLM responses in the planning workflow."""

from pydantic import BaseModel, Field


class TaskList(BaseModel):
    tasks: list[str] = Field(description="Concrete, actionable tasks. Short phrases, no explanations.")


class TaskVerdict(BaseModel):
    task: str
    vague: bool
    reason: str


class CriticOutput(BaseModel):
    verdicts: list[TaskVerdict]


class TaskScore(BaseModel):
    task: str
    urgency: int
    importance: int
    depends_on: list[str] = Field(description="Titles of prerequisite tasks")


class RankerOutput(BaseModel):
    scores: list[TaskScore]