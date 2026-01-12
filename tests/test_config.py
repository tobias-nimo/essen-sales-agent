# tests/test_config.py
"""
Tests for configuration module.
"""

import os
import pytest
from pathlib import Path


class TestConfigPaths:
    """Tests for configuration paths"""

    def test_project_root_exists(self, project_root):
        """Test that project root exists"""
        assert project_root.exists(), f"Project root not found: {project_root}"

    def test_src_directory_exists(self, project_root):
        """Test that src directory exists"""
        src_dir = project_root / "src"
        assert src_dir.exists(), f"src directory not found: {src_dir}"

    def test_agents_directory_exists(self, project_root):
        """Test that agents directory exists"""
        agents_dir = project_root / "src" / "agents"
        assert agents_dir.exists(), f"agents directory not found: {agents_dir}"

    def test_tools_directory_exists(self, project_root):
        """Test that tools directory exists"""
        tools_dir = project_root / "src" / "agents" / "tools"
        assert tools_dir.exists(), f"tools directory not found: {tools_dir}"

    def test_data_directory_exists(self, data_dir):
        """Test that data directory exists"""
        assert data_dir.exists(), f"data directory not found: {data_dir}"


class TestConfigImport:
    """Tests for config module import"""

    def test_config_imports(self):
        """Test that config module can be imported"""
        try:
            from config import DATA_DIR, PROMPTS_DIR
        except ImportError as e:
            pytest.fail(f"Failed to import config: {e}")

    def test_config_data_dir_is_path(self):
        """Test that DATA_DIR is a Path object"""
        from config import DATA_DIR
        assert isinstance(DATA_DIR, Path), "DATA_DIR should be a Path object"

    def test_config_prompts_dir_is_path(self):
        """Test that PROMPTS_DIR is a Path object"""
        from config import PROMPTS_DIR
        assert isinstance(PROMPTS_DIR, Path), "PROMPTS_DIR should be a Path object"


class TestEnvironmentVariables:
    """Tests for environment variable handling"""

    def test_env_file_exists(self, project_root):
        """Test that .env file exists (optional but recommended)"""
        env_file = project_root / ".env"
        if not env_file.exists():
            pytest.skip(".env file not found - this is optional for testing")

    def test_llm_provider_configured(self):
        """Test that at least one LLM provider is configured"""
        openai_configured = bool(os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_LLM"))
        groq_configured = bool(os.environ.get("GROQ_API_KEY") and os.environ.get("GROQ_LLM"))

        if not (openai_configured or groq_configured):
            pytest.skip("No LLM provider configured - skipping LLM tests")
