# tests/test_data.py
"""
Tests for data file integrity and loading.
"""

import csv
import json
import pytest
from pathlib import Path


class TestDataFiles:
    """Tests for data file existence and structure"""

    def test_catalog_file_exists(self, data_dir):
        """Test that catalog.csv exists"""
        catalog_file = data_dir / "catalog.csv"
        assert catalog_file.exists(), f"Catalog file not found: {catalog_file}"

    def test_price_list_file_exists(self, data_dir):
        """Test that price_list.csv exists"""
        price_file = data_dir / "price_list.csv"
        assert price_file.exists(), f"Price list file not found: {price_file}"

    def test_promotions_file_exists(self, data_dir):
        """Test that promotions.json exists"""
        promotions_file = data_dir / "promotions.json"
        assert promotions_file.exists(), f"Promotions file not found: {promotions_file}"


class TestCatalogData:
    """Tests for catalog.csv structure and content"""

    def test_catalog_has_required_columns(self, data_dir):
        """Test that catalog has id and description columns"""
        catalog_file = data_dir / "catalog.csv"
        with open(catalog_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

        assert 'id' in fieldnames, "Catalog missing 'id' column"
        assert 'description' in fieldnames, "Catalog missing 'description' column"

    def test_catalog_has_products(self, data_dir):
        """Test that catalog has at least one product"""
        catalog_file = data_dir / "catalog.csv"
        with open(catalog_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            products = list(reader)

        assert len(products) > 0, "Catalog is empty"

    def test_catalog_products_have_ids(self, data_dir):
        """Test that all products have non-empty IDs"""
        catalog_file = data_dir / "catalog.csv"
        with open(catalog_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row['id'].strip(), f"Product found with empty ID: {row}"

    def test_catalog_ids_are_unique(self, data_dir):
        """Test that all product IDs are unique"""
        catalog_file = data_dir / "catalog.csv"
        with open(catalog_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            ids = [row['id'] for row in reader]

        duplicates = [id for id in ids if ids.count(id) > 1]
        assert len(duplicates) == 0, f"Duplicate product IDs found: {set(duplicates)}"


class TestPriceListData:
    """Tests for price_list.csv structure and content"""

    def test_price_list_has_required_columns(self, data_dir):
        """Test that price list has required columns"""
        price_file = data_dir / "price_list.csv"
        with open(price_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

        required_columns = ['id', 'base_price', 'cash_price', 'installments_12', 'installments_9', 'installments_6']
        for col in required_columns:
            assert col in fieldnames, f"Price list missing '{col}' column"

    def test_price_list_has_prices(self, data_dir):
        """Test that price list has at least one entry"""
        price_file = data_dir / "price_list.csv"
        with open(price_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            prices = list(reader)

        assert len(prices) > 0, "Price list is empty"

    def test_prices_are_numeric(self, data_dir):
        """Test that price values are numeric"""
        price_file = data_dir / "price_list.csv"
        numeric_fields = ['base_price', 'cash_price', 'installments_12', 'installments_9', 'installments_6']

        with open(price_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                for field in numeric_fields:
                    value = row.get(field, '0')
                    if value:  # Allow empty values
                        try:
                            float(value)
                        except ValueError:
                            pytest.fail(f"Non-numeric value '{value}' found in {field} for product {row['id']}")


class TestPromotionsData:
    """Tests for promotions.json structure and content"""

    def test_promotions_is_valid_json(self, data_dir):
        """Test that promotions.json is valid JSON"""
        promotions_file = data_dir / "promotions.json"
        try:
            with open(promotions_file, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in promotions file: {e}")

    def test_promotions_is_list(self, data_dir):
        """Test that promotions.json contains a list"""
        promotions_file = data_dir / "promotions.json"
        with open(promotions_file, 'r', encoding='utf-8') as f:
            promotions = json.load(f)

        assert isinstance(promotions, list), "Promotions should be a list"

    def test_promotions_have_required_fields(self, data_dir):
        """Test that promotions have required fields"""
        promotions_file = data_dir / "promotions.json"
        with open(promotions_file, 'r', encoding='utf-8') as f:
            promotions = json.load(f)

        required_fields = ['id', 'name', 'banks', 'credit_cards', 'installments', 'availability']
        for promo in promotions:
            for field in required_fields:
                assert field in promo, f"Promotion {promo.get('id', 'unknown')} missing '{field}' field"

    def test_promotions_banks_is_list(self, data_dir):
        """Test that banks field is a list"""
        promotions_file = data_dir / "promotions.json"
        with open(promotions_file, 'r', encoding='utf-8') as f:
            promotions = json.load(f)

        for promo in promotions:
            assert isinstance(promo['banks'], list), f"Promotion {promo['id']} banks should be a list"

    def test_promotions_credit_cards_is_list(self, data_dir):
        """Test that credit_cards field is a list"""
        promotions_file = data_dir / "promotions.json"
        with open(promotions_file, 'r', encoding='utf-8') as f:
            promotions = json.load(f)

        for promo in promotions:
            assert isinstance(promo['credit_cards'], list), f"Promotion {promo['id']} credit_cards should be a list"

    def test_promotions_installments_is_list(self, data_dir):
        """Test that installments field is a list"""
        promotions_file = data_dir / "promotions.json"
        with open(promotions_file, 'r', encoding='utf-8') as f:
            promotions = json.load(f)

        for promo in promotions:
            assert isinstance(promo['installments'], list), f"Promotion {promo['id']} installments should be a list"


class TestPromptsFiles:
    """Tests for prompt files"""

    def test_prompts_directory_exists(self, prompts_dir):
        """Test that prompts directory exists"""
        assert prompts_dir.exists(), f"Prompts directory not found: {prompts_dir}"

    def test_coordinator_prompt_exists(self, prompts_dir):
        """Test that coordinator prompt file exists"""
        prompt_file = prompts_dir / "coordinator.md"
        assert prompt_file.exists(), f"Coordinator prompt not found: {prompt_file}"

    def test_catalog_agent_prompt_exists(self, prompts_dir):
        """Test that catalog agent prompt file exists"""
        prompt_file = prompts_dir / "catalog_agent.md"
        assert prompt_file.exists(), f"Catalog agent prompt not found: {prompt_file}"

    def test_promotions_agent_prompt_exists(self, prompts_dir):
        """Test that promotions agent prompt file exists"""
        prompt_file = prompts_dir / "promotions_agent.md"
        assert prompt_file.exists(), f"Promotions agent prompt not found: {prompt_file}"

    def test_prompt_files_not_empty(self, prompts_dir):
        """Test that prompt files are not empty"""
        prompt_files = [
            "coordinator.md",
            "catalog_agent.md",
            "promotions_agent.md"
        ]
        for filename in prompt_files:
            prompt_file = prompts_dir / filename
            if prompt_file.exists():
                content = prompt_file.read_text(encoding='utf-8')
                assert len(content.strip()) > 0, f"Prompt file {filename} is empty"
