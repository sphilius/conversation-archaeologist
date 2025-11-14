"""
API Data Fetcher Nano-Agent

Multi-strategy conversation data fetcher with automatic fallback.

Strategy Priority:
1. Official API (not yet available, future-proofed)
2. Web scraping (Phase 2 implementation)
3. Manual export (Phase 1 implementation)

For Phase 1, this agent primarily guides users through manual export
while setting up architecture for automated fetching in Phase 2.

Quality Metrics:
- Data completeness: Target 98%+
- Cost efficiency: <$0.02 per conversation
- Success rate: 95%+ across all strategies

Example Usage:
    >>> fetcher = APIDataFetcher(auth_token="your_token")
    >>> data = await fetcher.fetch("conversation-id-123")
"""

import asyncio
from typing import Optional, Any
from enum import Enum
from pathlib import Path
import json


class FetchStrategy(Enum):
    """Available fetch strategies"""
    API = "api"
    SCRAPING = "scraping"
    MANUAL = "manual"


class APINotAvailableError(Exception):
    """Raised when API endpoint doesn't exist yet"""
    pass


class APIDataFetcher:
    """
    Multi-strategy conversation data fetcher with automatic fallback.
    
    Phase 1: Manual export guidance
    Phase 2: Add Playwright scraping
    Phase 3: Add official API when available
    
    Quality Metrics:
    - Data completeness: Target 98%+
    - Cost efficiency: <$0.02 per conversation
    - Success rate: 95%+ across all strategies
    """
    
    def __init__(self, auth_token: Optional[str] = None) -> None:
        """
        Initialize fetcher with authentication.
        
        Args:
            auth_token: Claude session token (optional for Phase 1)
        """
        self.auth_token = auth_token
        self.strategy_attempts: dict[FetchStrategy, int] = {
            s: 0 for s in FetchStrategy
        }
        self.strategy_successes: dict[FetchStrategy, int] = {
            s: 0 for s in FetchStrategy
        }
        self.total_cost = 0.0
    
    async def fetch(
        self,
        conv_id: str,
        max_retries: int = 2
    ) -> dict[str, Any]:
        """
        Fetch conversation data using optimal strategy.
        
        Phase 1: Prompts for manual export
        Phase 2: Will add automated scraping
        Phase 3: Will add official API
        
        Args:
            conv_id: Conversation ID to fetch
            max_retries: Maximum retry attempts (for future use)
            
        Returns:
            Complete conversation JSON with metadata
            
        Raises:
            FileNotFoundError: If manual export file doesn't exist
        """
        # Phase 1: Use manual export
        return self._prompt_manual_export(conv_id)
    
    async def fetch_from_file(self, filepath: Path) -> dict[str, Any]:
        """
        Load conversation from manually exported file.
        
        Args:
            filepath: Path to JSON file from manual export
            
        Returns:
            Conversation data dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
            
        Examples:
            >>> fetcher = APIDataFetcher()
            >>> data = await fetcher.fetch_from_file(Path("conversation.json"))
        """
        self.strategy_attempts[FetchStrategy.MANUAL] += 1
        
        if not filepath.exists():
            raise FileNotFoundError(
                f"Manual export file not found: {filepath}\n"
                f"Please export conversation from Claude.ai first"
            )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate basic structure
            self._validate_conversation_data(data)
            
            self.strategy_successes[FetchStrategy.MANUAL] += 1
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in export file: {filepath}\n"
                f"Error: {str(e)}"
            ) from e
    
    def _validate_conversation_data(self, data: dict[str, Any]) -> None:
        """
        Validate conversation data structure.
        
        Args:
            data: Conversation data dictionary
            
        Raises:
            ValueError: If data structure is invalid
        """
        if 'messages' not in data:
            raise ValueError(
                "Invalid conversation data: missing 'messages' field"
            )
        
        if not isinstance(data['messages'], list):
            raise ValueError(
                "Invalid conversation data: 'messages' must be a list"
            )
        
        if len(data['messages']) == 0:
            raise ValueError(
                "Invalid conversation data: 'messages' list is empty"
            )
    
    def _prompt_manual_export(self, conv_id: str) -> dict[str, Any]:
        """
        Guide user through manual export process.
        
        Args:
            conv_id: Conversation ID to export
            
        Returns:
            Instruction dictionary for manual export
        """
        self.strategy_attempts[FetchStrategy.MANUAL] += 1
        
        export_instructions = {
            "status": "manual_export_required",
            "conv_id": conv_id,
            "instructions": [
                "1. Open conversation in Claude.ai:",
                f"   https://claude.ai/chat/{conv_id}",
                "",
                "2. Click the '...' menu in top right corner",
                "",
                "3. Select 'Export conversation'",
                "",
                "4. Save JSON file to: /mnt/user-data/uploads/",
                "",
                "5. Run this command to process the export:",
                f"   python scripts/extract.py --from-file conversation.json"
            ],
            "alternative_method": [
                "If export option is not available:",
                "1. Copy conversation URL",
                "2. Wait for Phase 2 (automated scraping)",
                "3. Or manually copy/paste conversation text"
            ],
            "next_steps": [
                "After exporting, use: fetch_from_file(Path('conversation.json'))"
            ]
        }
        
        return export_instructions
    
    async def _fetch_via_api(self, conv_id: str) -> dict[str, Any]:
        """
        Fetch via official Claude API.
        
        NOTE: Not yet available as of November 2025.
        This is future-proofing for when Anthropic adds conversation history API.
        
        Args:
            conv_id: Conversation ID
            
        Returns:
            Conversation data from API
            
        Raises:
            APINotAvailableError: API endpoint doesn't exist yet
        """
        self.strategy_attempts[FetchStrategy.API] += 1
        
        # Future implementation will use httpx to call Anthropic API
        # For now, raise error to trigger fallback
        raise APINotAvailableError(
            "Official conversation API not yet available. "
            "Using manual export for Phase 1."
        )
    
    async def _fetch_via_scraping(self, conv_id: str) -> dict[str, Any]:
        """
        Fetch via web scraping (Phase 2 implementation).
        
        Will use Playwright to:
        1. Launch browser with authentication
        2. Navigate to conversation URL
        3. Extract conversation DOM
        4. Parse into structured data
        
        Cost: ~$0.02 per conversation (compute time)
        
        Args:
            conv_id: Conversation ID
            
        Returns:
            Scraped conversation data
            
        Raises:
            NotImplementedError: Not yet implemented in Phase 1
        """
        self.strategy_attempts[FetchStrategy.SCRAPING] += 1
        
        # Phase 2 implementation will use Playwright
        raise NotImplementedError(
            "Web scraping not yet implemented. "
            "This will be added in Phase 2. "
            "Please use manual export for now."
        )
    
    def get_metrics(self) -> dict[str, Any]:
        """
        Get quality metrics for DSPy-style optimization.
        
        Returns:
            Dictionary with success rates and cost tracking
            
        Examples:
            >>> fetcher = APIDataFetcher()
            >>> # ... perform fetches ...
            >>> metrics = fetcher.get_metrics()
            >>> print(metrics['overall_success_rate'])
        """
        total_attempts = sum(self.strategy_attempts.values())
        total_successes = sum(self.strategy_successes.values())
        
        return {
            "overall_success_rate": (
                total_successes / total_attempts if total_attempts > 0 else 0
            ),
            "strategy_breakdown": {
                str(s.value): {
                    "attempts": self.strategy_attempts[s],
                    "successes": self.strategy_successes[s],
                    "success_rate": (
                        self.strategy_successes[s] / self.strategy_attempts[s]
                        if self.strategy_attempts[s] > 0 else 0
                    )
                }
                for s in FetchStrategy
            },
            "total_cost_usd": self.total_cost,
            "avg_cost_per_conversation": (
                self.total_cost / total_successes if total_successes > 0 else 0
            ),
            "phase": "1 (manual export only)"
        }


if __name__ == "__main__":
    # Quick test
    async def test_fetcher():
        fetcher = APIDataFetcher()
        
        # Test manual export prompt
        result = fetcher._prompt_manual_export("test-conv-id")
        print("Manual export instructions:")
        for instruction in result["instructions"]:
            print(f"  {instruction}")
        
        print("\nMetrics:", fetcher.get_metrics())
    
    asyncio.run(test_fetcher())
