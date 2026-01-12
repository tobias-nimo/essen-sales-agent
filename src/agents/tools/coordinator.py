# src/tools/coordinator.py

from agents.catalog_agent import catalog_agent
from agents.promotions_agent import promotions_agent

from typing import Optional

from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import ToolRuntime
from langgraph.types import Command

@tool
def lookup_products(products: list[str]) -> str:
    """Search the catalog for available products and their prices."""
    query = f"""
    Search the catalog for these products:
    {chr(10).join(f"- {p}" for p in products)}
    """

    response = catalog_agent.invoke(
        {"messages": [HumanMessage(content=query)]}
        )
    
    return response['messages'][-1].content

@tool
def get_available_promotions(banks: list[str], installments: list[int]) -> str:
    """
    Return available sales promotions and discounts
    for the given banks and credit card installment options.
    """
    query = f"""
    Find available promotions for:
    - Banks: {', '.join(banks)}
    - Installments: {', '.join(map(str, installments))}
    """

    response = promotions_agent.invoke(
        {"messages": [HumanMessage(content=query)]}
        )
    
    return response['messages'][-1].content

# TODO: update update_state tool based on the new SalesQuoteState schema

@tool
def update_state(
    products: Optional[list] = None,
    payment_method: Optional[str] = None,
    promotion: Optional[str] = None,
    customer_name: Optional[str] = None,
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None,
    runtime: ToolRuntime) -> str:
    """Update state values for the sales quote"""
    
    # Build the update dictionary with only provided values
    update_dict = {}
    
    if products is not None:
        update_dict["products"] = products
    
    if payment_method is not None:
        update_dict["payment_method"] = payment_method
    
    if payment_plan is not None:
        update_dict["payment_plan"] = payment_plan
    
    # Handle customer information
    if any([customer_name, customer_email, customer_phone]):
        customer_info = {}
        if customer_name:
            customer_info["name"] = customer_name
        if customer_email:
            customer_info["email"] = customer_email
        if customer_phone:
            customer_info["phone"] = customer_phone
        update_dict["customer_information"] = customer_info
    
    return Command(
        update={
            **update_dict,
            "messages": [ToolMessage(
                content="Successfully updated state",
                tool_call_id=runtime.tool_call_id
            )]
        }
    )

# TODO: add tool to generate a link to download the sales quote document in a nicely-formatted PDF file