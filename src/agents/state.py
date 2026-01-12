# src/agents/state.py

from typing import Dict, Optional, Literal, TypedDict
from dataclasses import dataclass
from langgraph.graph import MessagesState

@dataclass
class CustomerInformation:
    name: str
    email: str
    phone: str

@dataclass
class PaymentPlan:
    bank: Literal[
        "GALICIA", "MACRO", "INDUSTRIAL", "FRANCES", "NACION", "RIO", "HIPOTECARIO", "PROVINCIA", "CREDICOOP",
        "BCO_NEUQUEN", "BCO_CORRIENTES", "BCO_ENTRERIOS", "BCO_SANTACRUZ", "BCO_SANTAFE", "BCO_SANJUAN", "BCO_CHACO"
    ]
    credit_card: Literal["VISA", "AMEX", "MASTERCARD", "CONFI", "TUYA", "CABAL", "NAR"]
    promotion_id: Optional[str] = None
    installments: int = 1
    price_per_installment: float = 0.0

@dataclass
class ProductLine:
    product_id: str
    description: str
    quantity: int
    unit_price: float
    subtotal: float

class SalesQuoteState(MessagesState):
    """State for managing sales quote creation"""
    products: Dict[str, ProductLine]
    payment_method: Optional[Literal["CASH", "WIRE", "CREDIT_CARD"]] = None
    payment_plan: Optional[PaymentPlan] = None
    customer_information: Optional[CustomerInformation] = None
    total_amount: float = 0.0