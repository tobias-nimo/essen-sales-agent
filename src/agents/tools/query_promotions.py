# src/agents/tools/query_promotions.py
"""
Promotion query tools for the promotions agent.
"""

import json
from typing import List, Optional
from datetime import datetime
from loguru import logger
from langchain.tools import tool

from config import DATA_DIR

# Path to promotions file
PROMOTIONS_FILE = DATA_DIR / "promotions.json"

def load_promotions() -> List[dict]:
    """Load promotions from JSON file"""
    logger.debug(f"Loading promotions from: {PROMOTIONS_FILE}")
    try:
        with open(PROMOTIONS_FILE, 'r', encoding='utf-8') as f:
            promotions = json.load(f)
        logger.debug(f"Loaded {len(promotions)} promotions")
        return promotions
    except FileNotFoundError:
        logger.error(f"Promotions file not found: {PROMOTIONS_FILE}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in promotions file: {e}")
        return []
    except Exception as e:
        logger.exception(f"Error loading promotions: {e}")
        return []

def is_promotion_available(promotion: dict, current_date: datetime = None) -> bool:
    """Check if a promotion is currently available"""
    if current_date is None:
        current_date = datetime.now()

    availability = promotion.get('availability', {})
    avail_type = availability.get('type', 'always')

    if avail_type == 'always':
        return True
    elif avail_type == 'date_range':
        start = datetime.fromisoformat(availability.get('start', ''))
        end = datetime.fromisoformat(availability.get('end', ''))
        return start <= current_date <= end

    return False

# Load promotions in-memory
promotions = load_promotions()

@tool
def search_promotions(
    bank: Optional[str] = None,
    credit_card: Optional[str] = None,
    installments: Optional[int] = None
) -> str:
    """
    Search for available promotions based on bank, credit card, and installment criteria.

    Args:
        bank: Bank name (e.g., "GALICIA", "MACRO")
        credit_card: Credit card brand (e.g., "VISA", "MASTERCARD", "AMEX")
        installments: Number of installments desired (e.g., 3, 6, 9, 12)

    Note:
        Any parameter set to None is ignored and will not be used as a filter.
        Only the provided (non-None) parameters are applied when searching promotions.
    """
    logger.info(f"Searching promotions - bank: {bank}, card: {credit_card}, installments: {installments}")

    matches = []

    for promo in promotions:
        # Check if promotion is currently available
        if not is_promotion_available(promo):
            continue

        # Filter by bank
        if bank and bank.upper() not in [b.upper() for b in promo.get('banks', [])]:
            continue

        # Filter by credit card
        if credit_card:
            cards = [c.upper() for c in promo.get('credit_cards', [])]
            if credit_card.upper() not in cards:
                continue

        # Filter by installments
        if installments and installments not in promo.get('installments', []):
            continue

        matches.append(promo)

    logger.debug(f"Found {len(matches)} matching promotions")

    if not matches:
        filters = []
        if bank:
            filters.append(f"bank: {bank}")
        if credit_card:
            filters.append(f"credit card: {credit_card}")
        if installments:
            filters.append(f"installments: {installments}")

        filter_str = ", ".join(filters) if filters else "the given criteria"
        return f"No promotions found for {filter_str}"

    # Format results
    results = []
    for promo in matches:
        result = f"Promotion: {promo['name']} (ID: {promo['id']})\n"
        result += f"Banks: {', '.join(promo['banks'])}\n"
        result += f"Credit Cards: {', '.join(promo['credit_cards'])}\n"
        result += f"Installments: {', '.join(map(str, promo['installments']))}\n"

        wallets = promo.get('wallets', [])
        if wallets:
            wallet_names = [w['name'] for w in wallets]
            result += f"Digital Wallets: {', '.join(wallet_names)}\n"

        reimbursement = promo.get('reimbursement')
        if reimbursement:
            result += f"Reimbursement: {reimbursement}\n"

        results.append(result)

    return f"Found {len(matches)} promotions:\n\n" + "\n---\n\n".join(results)

@tool
def get_promotion_by_id(promotion_id: str) -> str:
    """
    Get detailed information about a specific promotion by its ID.

    Args:
        promotion_id: The unique promotion identifier (e.g., "001", "002")
    """
    logger.info(f"Getting promotion details for ID: {promotion_id}")

    promo = next((p for p in promotions if p['id'] == promotion_id), None)

    if not promo:
        logger.warning(f"Promotion not found: {promotion_id}")
        return f"Promotion with ID {promotion_id} not found"

    if not is_promotion_available(promo):
        logger.info(f"Promotion {promotion_id} is not currently available")
        return f"Promotion {promotion_id} is not currently available"

    result = f"Promotion: {promo['name']} (ID: {promo['id']})\n"
    result += f"Banks: {', '.join(promo['banks'])}\n"
    result += f"Credit Cards: {', '.join(promo['credit_cards'])}\n"
    result += f"Available Installments: {', '.join(map(str, promo['installments']))}\n"

    availability = promo.get('availability', {})
    result += f"Availability: {availability.get('type', 'always')}\n"

    wallets = promo.get('wallets', [])
    if wallets:
        wallet_info = []
        for w in wallets:
            optional = " (optional)" if w.get('is_optional') else " (required)"
            wallet_info.append(f"{w['name']}{optional}")
        result += f"Digital Wallets: {', '.join(wallet_info)}\n"

    reimbursement = promo.get('reimbursement')
    if reimbursement:
        result += f"Reimbursement: {reimbursement}\n"
    else:
        result += "Reimbursement: None\n"

    return result

@tool
def list_all_promotions() -> str:
    """List all currently available promotions"""
    logger.info("Listing all available promotions")

    available = [p for p in promotions if is_promotion_available(p)]

    logger.debug(f"Found {len(available)} available promotions out of {len(promotions)} total")

    if not available:
        return "No promotions are currently available"

    results = []
    for promo in available:
        results.append(
            f"{promo['name']} (ID: {promo['id']}) - "
            f"Banks: {', '.join(promo['banks'][:2])}{'...' if len(promo['banks']) > 2 else ''}"
        )

    return f"Available Promotions ({len(available)}):\n" + "\n".join(f"- {r}" for r in results)