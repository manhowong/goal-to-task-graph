"""Command-line entry point for running the planning workflow from the terminal."""

import sys
import uuid

from renderers.terminal import TerminalRenderer
from workflow.engine import generate_task_graph


if __name__ == "__main__":
    goal = sys.argv[1] if len(sys.argv) > 1 else "plan a weekend camping trip"
    thread_id = sys.argv[2] if len(sys.argv) > 2 else str(uuid.uuid4())
    terminal = TerminalRenderer()
    terminal.display("=" * 80)
    terminal.display(f"PLANNING STARTED | Thread: {thread_id}")
    terminal.display("=" * 80 + "\n")
    rendered = generate_task_graph(
        goal,
        thread_id,
        renderer=terminal,
        on_progress=terminal.display,
    )
    terminal.display(rendered)
