"""Configuration management for story-seq."""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, ValidationError


class StorySeqConfig(BaseModel):
    """Configuration for story-seq application."""

    project_name: str = Field(default="story-seq", description="Project name")
    version: str = Field(default="0.1.0", description="Version number")
    
    # BLAST configuration
    blast_db_path: Optional[Path] = Field(
        default=None,
        description="Default path to BLAST database"
    )
    blast_evalue: float = Field(
        default=0.001,
        description="E-value threshold for BLAST"
    )
    
    # LLM configuration
    llm_api_url: Optional[str] = Field(
        default=None,
        description="LLM API endpoint URL"
    )
    llm_model: str = Field(
        default="gpt-4",
        description="LLM model to use for narrative generation"
    )
    llm_api_key: Optional[str] = Field(
        default=None,
        description="API key for LLM service"
    )
    max_tokens: int = Field(
        default=2000,
        description="Maximum tokens for AI responses"
    )
    
    class Config:
        """Pydantic config."""
        
        extra = "forbid"
        validate_assignment = True


def get_config_path() -> Path:
    """
    Get the path to the configuration file.
    
    Uses STORY_SEQ_CONFIG environment variable if set,
    otherwise defaults to ~/.storyseq/config.json
    """
    env_config = os.getenv("STORY_SEQ_CONFIG")
    if env_config:
        return Path(env_config)
    return Path.home() / ".storyseq" / "config.json"


def load_config() -> StorySeqConfig:
    """
    Load configuration from file.
    
    Returns default configuration if file doesn't exist.
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        return StorySeqConfig()
    
    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
        return StorySeqConfig(**config_data)
    except (json.JSONDecodeError, ValidationError) as e:
        # Return default config if file is invalid
        return StorySeqConfig()


def save_config(config: StorySeqConfig) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w") as f:
        json.dump(config.model_dump(exclude={"project_name", "version"}), f, indent=2, default=str)
