# config.py

import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# Load envs
load_dotenv()

# Model provider
if os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_LLM"):
	llm = ChatOpenAI(
		model=os.environ.get("OPENAI_LLM"),
		api_key=os.environ.get("OPENAI_API_KEY")
		)
elif os.environ.get("GROQ_API_KEY") and os.environ.get("GROQ_LLM"):
	llm = ChatGroq(
	    model=os.environ.get("GROQ_API_KEY"),
	    api_key=os.environ.get("GROQ_LLM")
	)
else:
	logger.error("❌ Error: OPENAI / GROQ environment variable not set")

# Paths
PROMPTS_DIR = Path("./src/agents/prompts")
DATA_DIR = Path("./data")