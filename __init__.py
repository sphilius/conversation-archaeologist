"""
Conversation Archaeologist

A nano-agent based tool for extracting, analyzing, and exporting Claude.ai conversations.

Phase 1: MVP - Extract single conversations with JSON output
"""

__version__ = "0.1.0"
__author__ = "Conversation Archaeologist Team"

# Import nano-agents for easy access
from nano_agents.url_parser import URLParser, ConversationIdentifier
from nano_agents.api_fetcher import APIDataFetcher, FetchStrategy
from nano_agents.branch_detector import BranchDetector, ConversationTree, MessageNode

__all__ = [
    "URLParser",
    "ConversationIdentifier",
    "APIDataFetcher",
    "FetchStrategy",
    "BranchDetector",
    "ConversationTree",
    "MessageNode",
    "__version__",
]
