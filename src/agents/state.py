# src/state.py

from typing import Dict, Optional, Literal
from dataclasses import dataclass

from langgraph.graph import AgentState

@dataclass
class CustomerInformation:
    name: str
    email: str
    phone: str 

@dataclass
class PaymentPlan:
    bank: Literal[
        "GALICIA", "MACRO", "INDUSTRIAL", "FRANCES", "NACION", "RIO", "HIPOTECARIO", "PROVINCIA", "CREDICOOP"
        "BCO_NEUQUEN", "BCO_CORRIENTES", "BCO_ENTRERIOS", "BCO_SANTACRUZ", "BCO_SANTAFE", "BCO_SANJUAN", "BCO_CHACO"
        ]
    credit_card: Literal["VISA", "AMEX", "MASTERCARD", "CONFI", "TUYA", "CABAL", "NAR"]
    is_promotion: bool = False
    installments: Optional[int] = None
    price: int

@dataclass
class ProductLine:
    product_id: str
    quantity: int

class SalesQuoteState(AgentState):
    products: Dict[str, ProductLine]
    payment_method: Literal["CASH", "WIRE", "CREDIT_CARD"]
    payment_plan: Optional[PaymentPlan] = None
    customer_information: Optional[CustomerInformation] = None

# TODO: review the SalesQuoteState schema and adapt if necessary