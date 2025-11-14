"""
Nano-Agents Package

Modular conversation extraction agents following nano-agent architecture.

Each agent has:
- Single responsibility
- Clear I/O contracts
- Quality metrics tracking
- Error recovery
- Reusability

Available Agents:
- URLParser: Extract conversation IDs from URLs
- APIDataFetcher: Fetch conversation data (multi-strategy)
- BranchDetector: Reconstruct conversation tree structure
"""

from nano_agents.url_parser import URLParser, ConversationIdentifier
from nano_agents.api_fetcher import APIDataFetcher, FetchStrategy
from nano_agents.branch_detector import (
    BranchDetector,
    ConversationTree,
    MessageNode
)

__all__ = [
    'URLParser',
    'ConversationIdentifier',
    'APIDataFetcher',
    'FetchStrategy',
    'BranchDetector',
    'ConversationTree',
    'MessageNode',
]

__version__ = '0.1.0'
