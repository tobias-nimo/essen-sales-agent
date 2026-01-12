# src/coordinator.py

from agents.state import SalesQuoteState
from agents.tools.coordinator import (
    lookup_products,
    get_available_promotions,
    update_state
    )

from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import before_agent
from langchain.messages import RemoveMessage
from langchain.messages import ToolMessage
from langchain.agents import create_agent
from langchain.agents import AgentState
from langgraph.runtime import Runtime

from typing import Any

## Middleware
summarizer = SummarizationMiddleware(
            model="gpt-4o-mini",
            trigger=("tokens", 5_000), # Amount of tokens we allow the conversation to grow to until we start summarizing
            keep=("messages", 3)       # Number of messages to keep after summarizing
        )


@before_agent
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Remove all the tool messages from the state"""
    messages = state["messages"]

    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
    
    return {"messages": [RemoveMessage(id=m.id) for m in tool_messages]}

## Prompt
with open("prompts/coordinator_agent.md", "r", encoding="utf-8") as f:
    prompt = f.read()

## Init Agent
coordinator = create_agent(
    model="gpt-5-nano",
    system_prompt=prompt,
    state_schema=SalesQuoteState,
    checkpointer=InMemorySaver(),
    tools=[lookup_products, get_available_promotions, update_state],
    middleware=[trim_messages, summarizer]
)