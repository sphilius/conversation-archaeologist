"""
Configuration management for Claude Conversation Extractor.

Handles loading configuration from files, environment variables,
and provides sensible defaults.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field


class MarkdownConfig(BaseModel):
    """Markdown export configuration."""
    include_statistics: bool = Field(True, description="Include statistics section")
    include_mermaid: bool = Field(True, description="Include Mermaid diagrams")
    include_tool_analysis: bool = Field(True, description="Include tool usage analysis")
    include_artifacts: bool = Field(True, description="Include artifact content")


class JSONConfig(BaseModel):
    """JSON export configuration."""
    pretty_print: bool = Field(True, description="Pretty print JSON output")
    include_metadata: bool = Field(True, description="Include extraction metadata")
    indent: int = Field(2, description="JSON indentation level")


class AuthConfig(BaseModel):
    """Authentication configuration."""
    method: str = Field("stored", description="Auth method: stored, browser, cookie")
    save_credentials: bool = Field(False, description="Save credentials to keyring")


class PerformanceConfig(BaseModel):
    """Performance and resource configuration."""
    timeout: int = Field(60, description="Request timeout in seconds")
    max_concurrent: int = Field(3, description="Max concurrent extractions")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    rate_limit_delay: float = Field(1.0, description="Delay between requests (seconds)")


class Config(BaseModel):
    """Main configuration class."""
    
    # General settings
    output_dir: Path = Field(
        default_factory=lambda: Path.home() / "claude-exports",
        description="Default output directory"
    )
    format: str = Field("both", description="Default export format: json, markdown, both")
    include_artifacts: bool = Field(True, description="Include artifacts by default")
    include_thinking: bool = Field(True, description="Include thinking content by default")
    extract_branches: str = Field("all", description="Branch extraction: all, active, none")
    
    # Sub-configurations
    auth: AuthConfig = Field(default_factory=AuthConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    markdown: MarkdownConfig = Field(default_factory=MarkdownConfig)
    json: JSONConfig = Field(default_factory=JSONConfig)
    
    # Logging
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[Path] = Field(None, description="Log file path")
    
    class Config:
        use_enum_values = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.dict(exclude_none=True)

    def save(self, path: Path) -> None:
        """Save configuration to YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Load configuration from dictionary."""
        return cls(**data)

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load configuration from YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)


def get_config_path() -> Path:
    """Get the default configuration file path."""
    return Path.home() / ".claude-extractor" / "config.yaml"


def load_config(path: Optional[Path] = None) -> Config:
    """
    Load configuration from file or create default.
    
    Args:
        path: Optional path to config file. If None, uses default location.
    
    Returns:
        Config object
    """
    if path is None:
        path = get_config_path()
    
    if path.exists():
        try:
            return Config.from_file(path)
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
            print("Using default configuration")
            return Config()
    else:
        # Create default config
        config = Config()
        
        # Try to save default config
        try:
            config.save(path)
            print(f"Created default configuration at {path}")
        except Exception as e:
            print(f"Warning: Could not save default config: {e}")
        
        return config


def ensure_config_exists() -> Config:
    """Ensure configuration exists, create if needed."""
    return load_config()
