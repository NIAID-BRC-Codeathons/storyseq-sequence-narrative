"""Tests for CLI functionality."""

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
