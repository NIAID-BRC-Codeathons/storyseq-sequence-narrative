"""Tests for configuration management."""

import json
import os
from pathlib import Path
import pytest
from story_seq.config import StorySeqConfig, get_config_path, load_config, save_config


def test_default_config() -> None:
    """Test creating a default configuration."""
    config = StorySeqConfig()
    assert config.project_name == "story-seq"
    assert config.llm_model == "gpt-4"
    assert config.llm_api_url is None
    assert config.llm_api_key is None


def test_config_with_values() -> None:
    """Test creating a configuration with custom values."""
    config = StorySeqConfig(
        llm_api_url="https://api.example.com",
        llm_model="gpt-4-turbo",
        llm_api_key="test-key-123",
    )
    assert config.llm_api_url == "https://api.example.com"
    assert config.llm_model == "gpt-4-turbo"
    assert config.llm_api_key == "test-key-123"


def test_get_config_path_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test getting default config path."""
    monkeypatch.delenv("STORY_SEQ_CONFIG", raising=False)
    path = get_config_path()
    assert path == Path.home() / ".storyseq" / "config.json"


def test_get_config_path_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test getting config path from environment variable."""
    custom_path = "/custom/path/config.json"
    monkeypatch.setenv("STORY_SEQ_CONFIG", custom_path)
    path = get_config_path()
    assert path == Path(custom_path)


def test_load_config_nonexistent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading config when file doesn't exist."""
    config_path = tmp_path / "nonexistent.json"
    monkeypatch.setenv("STORY_SEQ_CONFIG", str(config_path))
    
    config = load_config()
    assert isinstance(config, StorySeqConfig)
    assert config.llm_model == "gpt-4"  # default value


def test_save_and_load_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test saving and loading configuration."""
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("STORY_SEQ_CONFIG", str(config_path))
    
    # Create and save config
    original_config = StorySeqConfig(
        llm_api_url="https://api.test.com",
        llm_model="gpt-4-turbo",
        llm_api_key="secret-key",
    )
    save_config(original_config)
    
    # Load config
    loaded_config = load_config()
    assert loaded_config.llm_api_url == "https://api.test.com"
    assert loaded_config.llm_model == "gpt-4-turbo"
    assert loaded_config.llm_api_key == "secret-key"


def test_load_invalid_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading config with invalid JSON."""
    config_path = tmp_path / "invalid.json"
    monkeypatch.setenv("STORY_SEQ_CONFIG", str(config_path))
    
    # Write invalid JSON
    config_path.write_text("{ invalid json }")
    
    # Should return default config
    config = load_config()
    assert isinstance(config, StorySeqConfig)
    assert config.llm_model == "gpt-4"
