# src/agents/tools/coordinator.py

from config import OUTPUT_DIR
from agents.catalog_agent import catalog_agent
from agents.promotions_agent import promotions_agent
from agents.state import ProductLine, PaymentPlan, CustomerInformation
from agents.tools.search_catalog import load_prices

from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path
import json

from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command

# Load price data for budget calculations
_prices = load_prices()

@tool
def lookup_products(products: list[str]) -> str:
    """Search the catalog for available products and their prices."""
    query = f"""
    Search the catalog for these products:
    {'\n'.join(f"- {p}" for p in products)}
    """

    response = catalog_agent.invoke(
        {"messages": [HumanMessage(content=query)]}
        )

    return response['messages'][-1].content

@tool
def get_available_promotions(banks: list[str], installments: list[int], credit_cards: list[str]) -> str:
    """
    Return available sales promotions and discounts
    for the given banks and credit card installment options.
    """
    query = f"""
    Find available promotions that satisfy **all** of the following conditions (logical AND):
    - Bank is one of: {', '.join(banks)}
    - Installments include: {', '.join(map(str, installments))}
    - Credit card is one of: {', '.join(credit_cards)}
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
    runtime: ToolRuntime
) -> Command:
    """
    Add a product to the shopping cart.

    Args:
        product_id: Unique product identifier
        description: Product description
        quantity: Number of units

    NOTE:
        This function overwrites the entry for a given product_id.
        To increase quantity for an existing product, first read the current
        quantity and pass the updated total explicitly.

        Prices are NOT stored in cart - they are calculated at quote generation
        time based on the selected payment method and plan.
    """
    product_line = ProductLine(
        product_id=product_id,
        description=description,
        quantity=quantity
    )

    # Get current state from runtime
    current_products = runtime.state.get("products", {})
    current_products[product_id] = product_line

    return Command(
        update={
            "products": current_products,
            "messages": [ToolMessage(
                content=f"Added {quantity}x {description} to cart.",
                tool_call_id=runtime.tool_call_id
            )]
        }
    )

@tool
def remove_product_from_cart(
    product_id: str,
    runtime: ToolRuntime
) -> Command:
    """
    Remove a product from the shopping cart.

    Args:
        product_id: Unique product identifier to remove
    """
    current_products = runtime.state.get("products", {})

    if product_id not in current_products:
        return Command(
            update={
                "messages": [ToolMessage(
                    content=f"Product {product_id} not found in cart.",
                    tool_call_id=runtime.tool_call_id
                )]
            }
        )

    removed_product = current_products.pop(product_id)

    return Command(
        update={
            "products": current_products,
            "messages": [ToolMessage(
                content=f"Removed {removed_product.description} from cart.",
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
    runtime: ToolRuntime,
    bank: str,
    credit_card: str,
    installments: int,
    promotion_id: Optional[str] = None
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
        promotion_id=promotion_id
    )

    return Command(
        update={
            "payment_plan": payment_plan,
            "messages": [ToolMessage(
                content=f"Payment plan set: {installments} installments with {bank} - {credit_card}",
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

def _parse_price(value: str) -> float:
    """Parse price string to float, handling empty or invalid values."""
    if not value or value == 'N/A':
        return 0.0
    try:
        # Handle both comma and dot decimal separators
        return float(str(value).replace(',', '.'))
    except (ValueError, TypeError):
        return 0.0


def _get_unit_price(product_id: str, payment_method: str, payment_plan: Optional[PaymentPlan]) -> float:
    """
    Calculate the unit price for a product based on payment method and plan.

    Pricing logic:
    - CASH/WIRE: Use cash_price (or base_price if cash_price is 0)
    - CREDIT_CARD + promotion: Use base_price (promotional = base_price / installments)
    - CREDIT_CARD + no promotion: Use installment_n * n (total from standard installments)
    """
    price_info = _prices.get(product_id, {})

    if payment_method in ("CASH", "WIRE"):
        cash_price = _parse_price(price_info.get('cash_price', '0'))
        if cash_price > 0:
            return cash_price
        # Fallback to base_price if cash_price is 0
        return _parse_price(price_info.get('base_price', '0'))

    # CREDIT_CARD payment
    if payment_plan and payment_plan.promotion_id:
        # With promotion: use base_price (installment = base_price / n)
        return _parse_price(price_info.get('base_price', '0'))

    # Without promotion: total = installment_price * num_installments
    if payment_plan:
        installments = payment_plan.installments
        installment_key = f'installments_{installments}'
        installment_price = _parse_price(price_info.get(installment_key, '0'))

        if installment_price > 0:
            return installment_price * installments

    # Fallback to base_price
    return _parse_price(price_info.get('base_price', '0'))


def _calculate_budget(state: dict) -> List[dict]:
    """Calculate budget line items with prices based on payment method."""
    budget = []
    products = state.get("products", {})
    payment_method = state.get("payment_method", "CASH")
    payment_plan = state.get("payment_plan")

    for product_id, product in products.items():
        unit_price = _get_unit_price(product_id, payment_method, payment_plan)
        subtotal = product.quantity * unit_price

        budget.append({
            "id": product.product_id,
            "description": product.description,
            "quantity": product.quantity,
            "unit_price": unit_price,
            "subtotal": subtotal
        })

    return budget


def _calculate_total(budget: List[dict]) -> float:
    """Calculate total amount from budget line items."""
    return sum(item["subtotal"] for item in budget)


@tool
def generate_quote_pdf(runtime: ToolRuntime) -> str:
    """
    Generate a PDF document for the sales quote and return a download link.
    """
    state = runtime.state

    # Validate that all required information is present
    if not state.get("products"):
        return "Cannot generate quote: No products in cart"

    if not state.get("payment_method"):
        return "Cannot generate quote: Payment method not set"

    # Create a quote summary
    customer = state.get("customer_information")
    payment_method = state["payment_method"]
    payment_plan = state.get("payment_plan")

    # Calculate budget and totals
    budget = _calculate_budget(state)
    total_amount = _calculate_total(budget)

    # For credit card with promotion, also calculate installment info
    price_per_installment = None
    if payment_method == "CREDIT_CARD" and payment_plan:
        installments = payment_plan.installments
        if payment_plan.promotion_id:
            # Promotional pricing: total / installments (interest-free)
            price_per_installment = total_amount / installments
        else:
            # Standard installments: sum of monthly payments
            price_per_installment = total_amount / installments

    # Generate quote data
    quote_data = {
        "date": datetime.now().isoformat(),
        "products": budget,
        "payment_method": payment_method,
        "total_amount": total_amount
    }

    # Add customer info if available
    if customer:
        quote_data["customer"] = {
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone
        }

    if payment_plan:
        quote_data["payment_plan"] = {
            "bank": payment_plan.bank,
            "credit_card": payment_plan.credit_card,
            "installments": payment_plan.installments,
            "promotion_id": payment_plan.promotion_id,
            "price_per_installment": price_per_installment
        }

    # In production, this would:
    # 1. Generate a PDF using a library like reportlab or weasyprint
    # 2. Upload to cloud storage (S3, etc.)
    # 3. Return a download URL

    # For now, save as JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quote_{timestamp}.json"
    filepath = OUTPUT_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(quote_data, f, indent=2, ensure_ascii=False)

    return f"Quote generated successfully! File saved to: {filepath}"