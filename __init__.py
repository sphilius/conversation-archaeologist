"""
Claude Conversation Extractor

A comprehensive tool for extracting, analyzing, and exporting Claude.ai conversations.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from claude_extractor.models.conversation import Conversation
from claude_extractor.models.message import Message
from claude_extractor.models.artifact import Artifact
from claude_extractor.models.branch import Branch

__all__ = [
    "Conversation",
    "Message",
    "Artifact",
    "Branch",
    "__version__",
]
