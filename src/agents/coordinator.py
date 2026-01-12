# src/agents/coordinator.py

from config import llm, PROMPTS_DIR
from agents.state import SalesQuoteState
from agents.tools.coordinator import (
    lookup_products,
    get_available_promotions,
    add_product_to_cart,
    set_payment_method,
    set_payment_plan,
    set_customer_information,
    generate_quote_pdf
)

from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

## Middleware
summarizer = SummarizationMiddleware(
    model=llm,
    trigger=("tokens", 10_000),  # Amount of tokens we allow the conversation to grow to until we start summarizing
    keep=("messages", 3)         # Number of messages to keep after summarizing
)

## Prompt
PROMPT_PATH = PROMPTS_DIR / "coordinator.md"
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    prompt = f.read()

## Init Agent
coordinator = create_agent(
    model=llm,
    system_prompt=prompt,
    state_schema=SalesQuoteState,
    checkpointer=InMemorySaver(),
    tools=[
        lookup_products,
        get_available_promotions,
        add_product_to_cart,
        set_payment_method,
        set_payment_plan,
        set_customer_information,
        generate_quote_pdf
    ],
    middleware=[summarizer]
)