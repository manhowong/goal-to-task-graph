"""Abstract rendering interface shared by all output formatters."""

from abc import ABC, abstractmethod

from workflow.workflow_result import WorkflowResult


class BaseRenderer(ABC):
    @abstractmethod
    def render(self, result: WorkflowResult):
        """Convert a completed planning result for an entry point."""
        raise NotImplementedError
