# src/agents/tools/search_catalog.py
"""
Catalog search tools for the product catalog agent.
"""

import csv
from typing import List, Dict
from loguru import logger
from langchain.tools import tool

from config import DATA_DIR

# Path to data files
CATALOG_FILE = DATA_DIR / "catalog.csv"
PRICE_FILE = DATA_DIR / "price_list.csv"

def load_catalog() -> List[Dict[str, str]]:
    """Load catalog from CSV file"""
    logger.debug(f"Loading catalog from: {CATALOG_FILE}")
    products = []
    try:
        with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)
        logger.debug(f"Loaded {len(products)} products from catalog")
    except FileNotFoundError:
        logger.error(f"Catalog file not found: {CATALOG_FILE}")
    except Exception as e:
        logger.exception(f"Error loading catalog: {e}")
    return products

def load_prices() -> Dict[str, Dict[str, str]]:
    """Load prices from CSV file, indexed by product ID"""
    logger.debug(f"Loading prices from: {PRICE_FILE}")
    prices = {}
    try:
        with open(PRICE_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prices[row['id']] = row
        logger.debug(f"Loaded prices for {len(prices)} products")
    except FileNotFoundError:
        logger.error(f"Price file not found: {PRICE_FILE}")
    except Exception as e:
        logger.exception(f"Error loading prices: {e}")
    return prices

# Load catalog in-memory
catalog = load_catalog()
prices = load_prices()

@tool
def search_products(query: str) -> str:
    """
    Search for products in the catalog by name or description.
    Returns matching products with their IDs, descriptions, and prices.

    Args:
        query: Search term to find products (e.g., "sarten", "cacerola", "combo")
    """
    logger.info(f"Searching products with query: '{query}'")

    # Simple case-insensitive substring search
    query_lower = query.lower()
    matches = [
        p for p in catalog
        if query_lower in p['description'].lower()
    ]

    logger.debug(f"Found {len(matches)} matches for query '{query}'")

    if not matches:
        return f"No products found matching '{query}'"

    # Format results
    results = []
    for product in matches[:20]:  # Limit to 20 results
        product_id = product['id']
        description = product['description']

        price_info = prices.get(product_id, {})
        base_price = price_info.get('base_price', 'N/A')
        cash_price = price_info.get('cash_price', 'N/A')

        results.append(
            f"ID: {product_id}\n"
            f"Description: {description}\n"
            f"Base Price: ${base_price}\n"
            f"Cash Price: ${cash_price if cash_price != '0' else 'Same as base'}\n"
        )

    return f"Found {len(matches)} products:\n\n" + "\n---\n".join(results)

@tool
def get_product_by_id(product_id: str) -> str:
    """
    Get detailed information about a specific product by its ID.

    Args:
        product_id: The unique product identifier (e.g., "80010010")
    """
    logger.info(f"Getting product details for ID: {product_id}")

    # Find product in catalog
    product = next((p for p in catalog if p['id'] == product_id), None)

    if not product:
        logger.warning(f"Product not found: {product_id}")
        return f"Product with ID {product_id} not found"

    # Get price information
    price_info = prices.get(product_id, {})

    result = f"Product ID: {product_id}\n"
    result += f"Description: {product['description']}\n"
    result += f"Base Price: ${price_info.get('base_price', 'N/A')}\n"
    result += f"Cash/Wire Price: ${price_info.get('cash_price', 'N/A')}\n"
    result += f"12 Installments: ${price_info.get('installments_12', 'N/A')}/month\n"
    result += f"9 Installments: ${price_info.get('installments_9', 'N/A')}/month\n"
    result += f"6 Installments: ${price_info.get('installments_6', 'N/A')}/month\n"

    return result