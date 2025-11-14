"""
URL Parser Nano-Agent

Extracts conversation identifiers from Claude.ai URLs.

Quality Metrics Tracked:
- Parse success rate
- Validation accuracy  
- Execution time

Example Usage:
    >>> parser = URLParser()
    >>> result = parser.parse("https://claude.ai/chat/abc-123-def")
    >>> print(result.conv_id)
    'abc-123-def'
"""

from dataclasses import dataclass
from typing import Optional
import re
from urllib.parse import urlparse
import time


@dataclass
class ConversationIdentifier:
    """
    Value object for conversation metadata.
    
    Attributes:
        conv_id: Unique conversation identifier (UUID format)
        org_id: Organization ID (if available)
        project_id: Project ID (for project conversations)
        is_project_conv: Whether this is a project conversation
        platform: Source platform (always 'claude.ai' for now)
    """
    conv_id: str
    org_id: Optional[str] = None
    project_id: Optional[str] = None
    is_project_conv: bool = False
    platform: str = "claude.ai"


class URLParser:
    """
    Parses Claude.ai conversation URLs and extracts identifiers.
    
    Supports two URL formats:
    1. Standard: https://claude.ai/chat/{uuid}
    2. Project: https://claude.ai/project/{project_id}/chat/{uuid}
    
    Quality Metrics:
    - Target parse success rate: 99.5%
    - Target validation accuracy: 100%
    - Target execution time: <100ms per URL
    """
    
    # UUID pattern: 8-4-4-4-12 format with lowercase hex
    UUID_PATTERN = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
    
    # URL patterns
    CONV_URL_PATTERN = re.compile(
        rf'claude\.ai/chat/({UUID_PATTERN})',
        re.IGNORECASE
    )
    PROJECT_URL_PATTERN = re.compile(
        rf'claude\.ai/project/([a-zA-Z0-9_-]+)/chat/({UUID_PATTERN})',
        re.IGNORECASE
    )
    
    def __init__(self) -> None:
        """Initialize parser with quality tracking."""
        self.success_count = 0
        self.failure_count = 0
        self.execution_times: list[float] = []
    
    def parse(self, url: str) -> ConversationIdentifier:
        """
        Parse Claude.ai conversation URL.
        
        Args:
            url: Full or partial Claude conversation URL
            
        Returns:
            ConversationIdentifier with extracted metadata
            
        Raises:
            ValueError: If URL format is invalid
            
        Examples:
            >>> parser = URLParser()
            >>> result = parser.parse("https://claude.ai/chat/abc-123")
            >>> result.conv_id
            'abc-123'
            
            >>> result = parser.parse("claude.ai/project/my-proj/chat/def-456")
            >>> result.is_project_conv
            True
            >>> result.project_id
            'my-proj'
        """
        start_time = time.time()
        
        try:
            # Normalize URL - add scheme if missing
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            
            # Validate URL structure
            parsed = urlparse(url)
            if parsed.netloc != 'claude.ai':
                raise ValueError(
                    f"Invalid domain: {parsed.netloc}. Expected 'claude.ai'"
                )
            
            # Try project conversation pattern first
            project_match = self.PROJECT_URL_PATTERN.search(url)
            if project_match:
                result = ConversationIdentifier(
                    conv_id=project_match.group(2).lower(),
                    project_id=project_match.group(1),
                    org_id=None,  # Will be extracted from API response if needed
                    is_project_conv=True
                )
            else:
                # Try standard conversation pattern
                conv_match = self.CONV_URL_PATTERN.search(url)
                if not conv_match:
                    raise ValueError(
                        f"Invalid Claude conversation URL format: {url}\n"
                        f"Expected format: https://claude.ai/chat/{{uuid}} or "
                        f"https://claude.ai/project/{{id}}/chat/{{uuid}}"
                    )
                
                result = ConversationIdentifier(
                    conv_id=conv_match.group(1).lower(),
                    project_id=None,
                    org_id=None,
                    is_project_conv=False
                )
            
            # Validate UUID format
            self._validate_uuid(result.conv_id)
            
            # Track success metrics
            self.success_count += 1
            elapsed = time.time() - start_time
            self.execution_times.append(elapsed)
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            elapsed = time.time() - start_time
            self.execution_times.append(elapsed)
            
            # Re-raise with more context
            if isinstance(e, ValueError):
                raise
            else:
                raise ValueError(f"URL parsing failed: {str(e)}") from e
    
    def _validate_uuid(self, uuid: str) -> None:
        """
        Validate UUID format.
        
        Args:
            uuid: UUID string to validate
            
        Raises:
            ValueError: If UUID format is invalid
        """
        if not re.match(rf'^{self.UUID_PATTERN}$', uuid, re.IGNORECASE):
            raise ValueError(
                f"Invalid UUID format: {uuid}\n"
                f"Expected format: 8-4-4-4-12 hex digits with dashes"
            )
    
    def get_metrics(self) -> dict[str, float]:
        """
        Get quality metrics for DSPy-style optimization.
        
        Returns:
            Dictionary with success rate, average execution time, and total processed
            
        Examples:
            >>> parser = URLParser()
            >>> parser.parse("https://claude.ai/chat/test-id")
            >>> metrics = parser.get_metrics()
            >>> metrics['success_rate'] >= 0.99
            True
        """
        total = self.success_count + self.failure_count
        avg_time = (
            sum(self.execution_times) / len(self.execution_times)
            if self.execution_times
            else 0
        )
        
        return {
            "success_rate": self.success_count / total if total > 0 else 0,
            "avg_execution_time_ms": avg_time * 1000,  # Convert to milliseconds
            "total_processed": total,
            "successes": self.success_count,
            "failures": self.failure_count
        }
    
    def reset_metrics(self) -> None:
        """Reset quality tracking metrics."""
        self.success_count = 0
        self.failure_count = 0
        self.execution_times = []


if __name__ == "__main__":
    # Quick test
    parser = URLParser()
    
    test_urls = [
        "https://claude.ai/chat/abc-123-def-456-789",
        "claude.ai/project/my-project/chat/def-456-ghi-789-012",
        "https://claude.ai/chat/INVALID",  # Should fail
    ]
    
    for url in test_urls:
        try:
            result = parser.parse(url)
            print(f"✓ Parsed: {url}")
            print(f"  Conv ID: {result.conv_id}")
            print(f"  Project: {result.is_project_conv}")
        except ValueError as e:
            print(f"✗ Failed: {url}")
            print(f"  Error: {e}")
    
    print("\nMetrics:", parser.get_metrics())
