"""Application configuration for environment variables and runtime file paths."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the root directory and load the .env file
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

# LLM Configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "google/gemini-2.5-flash")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))

# External Service Configurations
PARALLEL_SEARCH_URL = os.getenv("PARALLEL_SEARCH_URL", "https://search.parallel.ai/mcp")
DB_PATH = ROOT_DIR / "workflow.db"