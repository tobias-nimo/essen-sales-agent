# tests/test_tools.py
"""
Tests for agent tools functionality.
"""

import pytest
from datetime import datetime


class TestSearchCatalogTools:
    """Tests for catalog search tools"""

    def test_load_catalog_returns_list(self):
        """Test that load_catalog returns a list"""
        from agents.tools.search_catalog import load_catalog
        catalog = load_catalog()
        assert isinstance(catalog, list), "load_catalog should return a list"

    def test_load_prices_returns_dict(self):
        """Test that load_prices returns a dict"""
        from agents.tools.search_catalog import load_prices
        prices = load_prices()
        assert isinstance(prices, dict), "load_prices should return a dict"

    def test_catalog_not_empty(self):
        """Test that catalog is not empty"""
        from agents.tools.search_catalog import load_catalog
        catalog = load_catalog()
        assert len(catalog) > 0, "Catalog should not be empty"

    def test_prices_not_empty(self):
        """Test that prices are not empty"""
        from agents.tools.search_catalog import load_prices
        prices = load_prices()
        assert len(prices) > 0, "Prices should not be empty"

    def test_search_products_returns_string(self):
        """Test that search_products returns a string"""
        from agents.tools.search_catalog import search_products
        result = search_products.invoke({"query": "sarten"})
        assert isinstance(result, str), "search_products should return a string"

    def test_search_products_no_results(self):
        """Test search_products with a query that returns no results"""
        from agents.tools.search_catalog import search_products
        result = search_products.invoke({"query": "xyz_nonexistent_product_12345"})
        assert "No products found" in result, "Should indicate no products found"

    def test_get_product_by_id_not_found(self):
        """Test get_product_by_id with non-existent ID"""
        from agents.tools.search_catalog import get_product_by_id
        result = get_product_by_id.invoke({"product_id": "NONEXISTENT123"})
        assert "not found" in result.lower(), "Should indicate product not found"


class TestQueryPromotionsTools:
    """Tests for promotions query tools"""

    def test_load_promotions_returns_list(self):
        """Test that load_promotions returns a list"""
        from agents.tools.query_promotions import load_promotions
        promotions = load_promotions()
        assert isinstance(promotions, list), "load_promotions should return a list"

    def test_promotions_not_empty(self):
        """Test that promotions are not empty"""
        from agents.tools.query_promotions import load_promotions
        promotions = load_promotions()
        assert len(promotions) > 0, "Promotions should not be empty"

    def test_is_promotion_available_always(self, sample_promotion):
        """Test is_promotion_available with 'always' availability"""
        from agents.tools.query_promotions import is_promotion_available
        assert is_promotion_available(sample_promotion), "Promotion with 'always' availability should be available"

    def test_is_promotion_available_date_range_active(self):
        """Test is_promotion_available with active date range"""
        from agents.tools.query_promotions import is_promotion_available
        promo = {
            "availability": {
                "type": "date_range",
                "start": "2020-01-01",
                "end": "2030-12-31"
            }
        }
        assert is_promotion_available(promo), "Promotion within date range should be available"

    def test_is_promotion_available_date_range_expired(self):
        """Test is_promotion_available with expired date range"""
        from agents.tools.query_promotions import is_promotion_available
        promo = {
            "availability": {
                "type": "date_range",
                "start": "2020-01-01",
                "end": "2020-12-31"
            }
        }
        assert not is_promotion_available(promo), "Expired promotion should not be available"

    def test_search_promotions_returns_string(self):
        """Test that search_promotions returns a string"""
        from agents.tools.query_promotions import search_promotions
        result = search_promotions.invoke({})
        assert isinstance(result, str), "search_promotions should return a string"

    def test_list_all_promotions_returns_string(self):
        """Test that list_all_promotions returns a string"""
        from agents.tools.query_promotions import list_all_promotions
        result = list_all_promotions.invoke({})
        assert isinstance(result, str), "list_all_promotions should return a string"

    def test_get_promotion_by_id_not_found(self):
        """Test get_promotion_by_id with non-existent ID"""
        from agents.tools.query_promotions import get_promotion_by_id
        result = get_promotion_by_id.invoke({"promotion_id": "NONEXISTENT123"})
        assert "not found" in result.lower(), "Should indicate promotion not found"


class TestStateSchema:
    """Tests for state schema definitions"""

    def test_customer_information_dataclass(self):
        """Test CustomerInformation dataclass"""
        from agents.state import CustomerInformation
        customer = CustomerInformation(
            name="Test User",
            email="test@example.com",
            phone="1234567890"
        )
        assert customer.name == "Test User"
        assert customer.email == "test@example.com"
        assert customer.phone == "1234567890"

    def test_payment_plan_dataclass(self):
        """Test PaymentPlan dataclass"""
        from agents.state import PaymentPlan
        plan = PaymentPlan(
            bank="GALICIA",
            credit_card="VISA",
            installments=12,
            price_per_installment=10000.0
        )
        assert plan.bank == "GALICIA"
        assert plan.credit_card == "VISA"
        assert plan.installments == 12
        assert plan.price_per_installment == 10000.0

    def test_product_line_dataclass(self):
        """Test ProductLine dataclass"""
        from agents.state import ProductLine
        product = ProductLine(
            product_id="TEST001",
            description="Test Product",
            quantity=2,
            unit_price=50000.0,
            subtotal=100000.0
        )
        assert product.product_id == "TEST001"
        assert product.description == "Test Product"
        assert product.quantity == 2
        assert product.unit_price == 50000.0
        assert product.subtotal == 100000.0
