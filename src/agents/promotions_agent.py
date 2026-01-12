# src/agents/promotions_agent.py

from agents.tools.query_promotions import (
    search_promotions,
    get_promotion_by_id,
    list_all_promotions
    )
from config import llm, PROMPTS_DIR

from langchain.agents import create_agent
from pathlib import Path

## Prompt
PROMPT_PATH = PROMPTS_DIR / "promotions_agent.md"
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    prompt = f.read()

## Init Agent
promotions_agent = create_agent(
    model=llm,
    tools=[search_promotions, get_promotion_by_id, list_all_promotions],
    system_prompt=prompt
)
