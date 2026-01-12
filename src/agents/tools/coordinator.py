# src/agents/tools/coordinator.py

from agents.catalog_agent import catalog_agent
from agents.promotions_agent import promotions_agent
from agents.state import ProductLine, PaymentPlan, CustomerInformation

from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path
import json

from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import tool, ToolRuntime
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

@tool
def add_product_to_cart(
    product_id: str,
    description: str,
    quantity: int,
    unit_price: float,
    runtime: ToolRuntime
) -> Command:
    """
    Add a product to the shopping cart.

    Args:
        product_id: Unique product identifier
        description: Product description
        quantity: Number of units
        unit_price: Price per unit
    """
    subtotal = quantity * unit_price

    product_line = ProductLine(
        product_id=product_id,
        description=description,
        quantity=quantity,
        unit_price=unit_price,
        subtotal=subtotal
    )

    # Get current state from runtime
    current_products = runtime.state.get("products", {})
    current_products[product_id] = product_line

    # Recalculate total
    total = sum(p.subtotal for p in current_products.values())

    return Command(
        update={
            "products": current_products,
            "total_amount": total,
            "messages": [ToolMessage(
                content=f"Added {quantity}x {description} to cart. Subtotal: ${subtotal:.2f}",
                tool_call_id=runtime.tool_call_id
            )]
        }
    )

@tool
def set_payment_method(
    payment_method: str,
    runtime: ToolRuntime
) -> Command:
    """
    Set the payment method for the sales quote.

    Args:
        payment_method: One of "CASH", "WIRE", or "CREDIT_CARD"
    """
    if payment_method not in ["CASH", "WIRE", "CREDIT_CARD"]:
        return Command(
            update={
                "messages": [ToolMessage(
                    content=f"Invalid payment method: {payment_method}. Must be CASH, WIRE, or CREDIT_CARD",
                    tool_call_id=runtime.tool_call_id
                )]
            }
        )

    return Command(
        update={
            "payment_method": payment_method,
            "messages": [ToolMessage(
                content=f"Payment method set to {payment_method}",
                tool_call_id=runtime.tool_call_id
            )]
        }
    )

@tool
def set_payment_plan(
    bank: str,
    credit_card: str,
    installments: int,
    price_per_installment: float,
    promotion_id: Optional[str] = None,
    runtime: ToolRuntime = None
) -> Command:
    """
    Set the payment plan for credit card purchases.

    Args:
        bank: Bank name
        credit_card: Credit card brand
        installments: Number of installments
        price_per_installment: Monthly payment amount
        promotion_id: Optional promotion ID if applicable
    """
    payment_plan = PaymentPlan(
        bank=bank,
        credit_card=credit_card,
        installments=installments,
        price_per_installment=price_per_installment,
        promotion_id=promotion_id
    )

    return Command(
        update={
            "payment_plan": payment_plan,
            "messages": [ToolMessage(
                content=f"Payment plan set: {installments} installments of ${price_per_installment:.2f} with {bank} {credit_card}",
                tool_call_id=runtime.tool_call_id
            )]
        }
    )

@tool
def set_customer_information(
    name: str,
    email: str,
    phone: str,
    runtime: ToolRuntime
) -> Command:
    """
    Set customer information for the sales quote.

    Args:
        name: Customer's full name
        email: Customer's email address
        phone: Customer's phone number
    """
    customer_info = CustomerInformation(
        name=name,
        email=email,
        phone=phone
    )

    return Command(
        update={
            "customer_information": customer_info,
            "messages": [ToolMessage(
                content=f"Customer information set for {name}",
                tool_call_id=runtime.tool_call_id
            )]
        }
    )

@tool
def generate_quote_pdf(runtime: ToolRuntime) -> str:
    """
    Generate a PDF document for the sales quote and return a download link.
    This is a placeholder - in production, this would generate an actual PDF file.
    """
    state = runtime.state

    # Validate that all required information is present
    if not state.get("products"):
        return "Cannot generate quote: No products in cart"

    if not state.get("customer_information"):
        return "Cannot generate quote: Customer information is missing"

    if not state.get("payment_method"):
        return "Cannot generate quote: Payment method not set"

    # Create a quote summary
    products = state["products"]
    customer = state["customer_information"]
    payment_method = state["payment_method"]
    payment_plan = state.get("payment_plan")
    total = state.get("total_amount", 0)

    # Generate quote data
    quote_data = {
        "date": datetime.now().isoformat(),
        "customer": {
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone
        },
        "products": [
            {
                "id": p.product_id,
                "description": p.description,
                "quantity": p.quantity,
                "unit_price": p.unit_price,
                "subtotal": p.subtotal
            }
            for p in products.values()
        ],
        "payment_method": payment_method,
        "total_amount": total
    }

    if payment_plan:
        quote_data["payment_plan"] = {
            "bank": payment_plan.bank,
            "credit_card": payment_plan.credit_card,
            "installments": payment_plan.installments,
            "price_per_installment": payment_plan.price_per_installment,
            "promotion_id": payment_plan.promotion_id
        }

    # In production, this would:
    # 1. Generate a PDF using a library like reportlab or weasyprint
    # 2. Upload to cloud storage (S3, etc.)
    # 3. Return a download URL

    # For now, save as JSON
    output_dir = Path(__file__).parent.parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quote_{timestamp}.json"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(quote_data, f, indent=2, ensure_ascii=False)

    return f"Quote generated successfully! File saved to: {filepath}\n\nIn production, this would be a PDF download link."