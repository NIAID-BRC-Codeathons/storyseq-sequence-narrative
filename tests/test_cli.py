"""Tests for CLI functionality."""

import os
from pathlib import Path
import pytest
from typer.testing import CliRunner
from story_seq.cli import app

runner = CliRunner()


def test_help() -> None:
    """Test that help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "story-seq" in result.stdout.lower()


def test_version() -> None:
    """Test version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_blast_command_exists() -> None:
    """Test that blast command exists."""
    result = runner.invoke(app, ["blast", "--help"])
    assert result.exit_code == 0
    assert "blast" in result.stdout.lower()


def test_blast_not_implemented() -> None:
    """Test that blast command shows not implemented message."""
    result = runner.invoke(app, ["blast"])
    assert result.exit_code == 0
    assert "not yet implemented" in result.stdout.lower()


def test_blast_with_llm_parameters() -> None:
    """Test blast command with LLM parameters."""
    result = runner.invoke(
        app,
        [
            "blast",
            "--query", "test.fasta",
            "--llm-api-url", "https://api.test.com",
            "--llm-model", "gpt-4-turbo",
            "--llm-api-key", "test-key",
        ]
    )
    assert result.exit_code == 0
    assert "test.fasta" in result.stdout
    assert "gpt-4-turbo" in result.stdout


def test_blast_help_shows_llm_options() -> None:
    """Test that blast help shows LLM configuration options."""
    result = runner.invoke(app, ["blast", "--help"])
    assert result.exit_code == 0
    assert "--llm-api-url" in result.stdout
    assert "--llm-model" in result.stdout
    assert "--llm-api-key" in result.stdout


def test_run_agent_command_exists() -> None:
    """Test that run-agent command exists."""
    result = runner.invoke(app, ["run-agent", "--help"])
    assert result.exit_code == 0
    assert "run-agent" in result.stdout.lower()


def test_run_agent_invalid_agent_name() -> None:
    """Test run-agent with invalid agent name."""
    result = runner.invoke(app, ["run-agent", "invalid_agent"])
    assert result.exit_code == 1
    assert "invalid agent name" in result.stdout.lower()


def test_run_agent_valid_agent_names() -> None:
    """Test that valid agent names are accepted."""
    valid_agents = ["configuration", "blast", "data_decoration", "reporter", "validation"]
    for agent in valid_agents:
        result = runner.invoke(app, ["run-agent", agent])
        # Should fail due to missing LLM config, but not due to invalid agent name
        assert "invalid agent name" not in result.stdout.lower()


def test_init_command_exists() -> None:
    """Test that init command exists."""
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "init" in result.stdout.lower()


def test_init_creates_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that init creates a configuration file."""
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("STORY_SEQ_CONFIG", str(config_path))
    
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert config_path.exists()
    assert "configuration file created" in result.stdout.lower()
    
    # Verify default values
    import json
    with open(config_path) as f:
        config = json.load(f)
    
    assert config["llm_api_url"] == "http://lambda5.cels.anl.gov:44497/v1"
    assert config["llm_model"] == "gpt5"
    assert config["llm_api_key"] == "."


def test_init_does_not_overwrite_without_force(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that init doesn't overwrite existing config without --force."""
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("STORY_SEQ_CONFIG", str(config_path))
    
    # Create initial config
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    
    # Try to init again without force
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "already exists" in result.stdout.lower()


def test_init_overwrites_with_force(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that init overwrites existing config with --force."""
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("STORY_SEQ_CONFIG", str(config_path))
    
    # Create initial config with different content
    import json
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump({"llm_model": "old-model"}, f)
    
    # Init with force
    result = runner.invoke(app, ["init", "--force"])
    assert result.exit_code == 0
    
    # Verify it was overwritten with defaults
    with open(config_path) as f:
        config = json.load(f)
    
    assert config["llm_model"] == "gpt5"
