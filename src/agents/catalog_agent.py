# src/agents/catalog_agent.py

from agents.tools.search_catalog import search_products, get_product_by_id
from config import llm, PROMPTS_DIR

from langchain.agents import create_agent
from pathlib import Path

## Prompt
PROMPT_PATH = PROMPTS_DIR / "catalog_agent.md"
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    prompt = f.read()

## Init Agent
catalog_agent = create_agent(
    model=llm,
    tools=[search_products, get_product_by_id],
    system_prompt=prompt
)