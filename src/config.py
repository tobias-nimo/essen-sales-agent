# config.py
"""
Configuration module for Essen Sales Agent.
Handles environment variables, model providers, and project paths.
"""

import os
import sys
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# Paths Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# Project root is two levels up from this file (src/config.py -> project root)
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
PROMPTS_DIR = SRC_DIR / "agents" / "prompts"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

logger.debug(f"Project root: {PROJECT_ROOT}")
logger.debug(f"Prompts directory: {PROMPTS_DIR}")
logger.debug(f"Data directory: {DATA_DIR}")

# ═══════════════════════════════════════════════════════════════════════════════
# Model Provider Configuration
# ═══════════════════════════════════════════════════════════════════════════════

llm = None

# Try Groq first
groq_key = os.environ.get("GROQ_API_KEY")
groq_model = os.environ.get("GROQ_LLM")

if groq_key and groq_model:
    logger.info(f"Initializing Groq provider with model: {groq_model}")
    llm = ChatGroq(
        model=groq_model,
        api_key=groq_key
    )
    logger.success("Groq provider initialized successfully")

# Try OpenAI as fallback
if llm is None:
    openai_key = os.environ.get("OPENAI_API_KEY")
    openai_model = os.environ.get("OPENAI_LLM")

    if openai_key and openai_model:
        logger.info(f"Initializing OpenAI provider with model: {openai_model}")
        llm = ChatOpenAI(
            model=openai_model,
            api_key=openai_key
        )
        logger.success("OpenAI provider initialized successfully")

# No provider configured
if llm is None:
    logger.error("No LLM provider configured!")
    logger.error("Please set either:")
    logger.error("  - OPENAI_API_KEY and OPENAI_LLM")
    logger.error("  - GROQ_API_KEY and GROQ_LLM")
    # Don't exit here, let the calling code handle it
