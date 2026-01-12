# src/agents/tools/search_catalog.py

from config import DATA_DIR

import csv
from pathlib import Path
from typing import List, Dict
from langchain.tools import tool

# Path to data files
CATALOG_FILE = DATA_DIR / "catalog.csv"
PRICE_FILE = DATA_DIR / "price_list.csv"

def load_catalog() -> List[Dict[str, str]]:
    """Load catalog from CSV file"""
    products = []
    with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)
    return products

def load_prices() -> Dict[str, Dict[str, str]]:
    """Load prices from CSV file, indexed by product ID"""
    prices = {}
    with open(PRICE_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prices[row['id']] = row
    return prices

@tool
def search_products(query: str) -> str:
    """
    Search for products in the catalog by name or description.
    Returns matching products with their IDs, descriptions, and prices.

    Args:
        query: Search term to find products (e.g., "sarten", "cacerola", "combo")
    """
    catalog = load_catalog()
    prices = load_prices()

    # Simple case-insensitive substring search
    query_lower = query.lower()
    matches = [
        p for p in catalog
        if query_lower in p['description'].lower()
    ]

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
    catalog = load_catalog()
    prices = load_prices()

    # Find product in catalog
    product = next((p for p in catalog if p['id'] == product_id), None)

    if not product:
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

@tool
def get_multiple_products(product_ids: List[str]) -> str:
    """
    Get information for multiple products at once.

    Args:
        product_ids: List of product IDs to retrieve
    """
    results = []
    for pid in product_ids:
        result = get_product_by_id.invoke({"product_id": pid})
        results.append(result)

    return "\n\n---\n\n".join(results)