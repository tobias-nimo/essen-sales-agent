# promotions_agent.py

from langchain.agents import create_agent

## Prompt
with open("prompts/promotions_agent.md", "r", encoding="utf-8") as f:
    prompt = f.read()

## Init Agent
promotions_agent = create_agent(
    model="gpt-5-nano",
    tools=[], # TODO: add tools
    system_prompt=prompt
)
