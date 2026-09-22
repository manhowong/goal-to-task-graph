"""JSON renderer for returning machine-readable workflow output."""

from renderers.base import BaseRenderer
from workflow.workflow_result import WorkflowResult


class JsonRenderer(BaseRenderer):
    """Render workflow output as JSON-serializable Python data."""

    def render(self, result: WorkflowResult) -> dict:
        return result.to_dict()