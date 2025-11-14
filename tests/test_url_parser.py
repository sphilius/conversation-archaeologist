"""
Unit tests for URL Parser nano-agent.

Run with: pytest tests/test_url_parser.py -v
"""

import pytest
from nano_agents.url_parser import URLParser, ConversationIdentifier


class TestURLParser:
    """Test suite for URLParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = URLParser()
    
    def test_parse_standard_conversation_url(self):
        """Test parsing standard conversation URL."""
        url = "https://claude.ai/chat/abc123de-f456-7890-abcd-ef1234567890"
        result = self.parser.parse(url)
        
        assert result.conv_id == "abc123de-f456-7890-abcd-ef1234567890"
        assert not result.is_project_conv
        assert result.project_id is None
        assert result.platform == "claude.ai"
    
    def test_parse_project_conversation_url(self):
        """Test parsing project conversation URL."""
        url = "https://claude.ai/project/my-project/chat/abc123de-f456-7890-abcd-ef1234567890"
        result = self.parser.parse(url)
        
        assert result.conv_id == "abc123de-f456-7890-abcd-ef1234567890"
        assert result.is_project_conv
        assert result.project_id == "my-project"
    
    def test_parse_url_without_scheme(self):
        """Test parsing URL without http:// or https://."""
        url = "claude.ai/chat/abc123de-f456-7890-abcd-ef1234567890"
        result = self.parser.parse(url)
        
        assert result.conv_id == "abc123de-f456-7890-abcd-ef1234567890"
    
    def test_parse_url_case_insensitive(self):
        """Test that UUID parsing is case insensitive."""
        url = "https://claude.ai/chat/ABC123DE-F456-7890-ABCD-EF1234567890"
        result = self.parser.parse(url)
        
        # Should normalize to lowercase
        assert result.conv_id == "abc123de-f456-7890-abcd-ef1234567890"
    
    def test_parse_invalid_domain(self):
        """Test that non-Claude URLs are rejected."""
        url = "https://not-claude.ai/chat/abc123de-f456-7890-abcd-ef1234567890"
        
        with pytest.raises(ValueError, match="Invalid domain"):
            self.parser.parse(url)
    
    def test_parse_invalid_uuid_format(self):
        """Test that invalid UUID formats are rejected."""
        invalid_urls = [
            "https://claude.ai/chat/not-a-uuid",
            "https://claude.ai/chat/abc-123",  # Too short
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError, match="Invalid"):
                self.parser.parse(url)
    
    def test_parse_invalid_path(self):
        """Test that incorrect paths are rejected."""
        url = "https://claude.ai/chats/abc123de-f456-7890-abcd-ef1234567890"
        
        with pytest.raises(ValueError, match="Invalid Claude conversation URL format"):
            self.parser.parse(url)
    
    def test_metrics_tracking(self):
        """Test that metrics are tracked correctly."""
        # Successful parse
        self.parser.parse("https://claude.ai/chat/abc123de-f456-7890-abcd-ef1234567890")
        
        # Failed parse
        try:
            self.parser.parse("https://invalid.com/chat/test")
        except ValueError:
            pass
        
        metrics = self.parser.get_metrics()
        
        assert metrics['success_rate'] == 0.5  # 1 success, 1 failure
        assert metrics['total_processed'] == 2
        assert metrics['successes'] == 1
        assert metrics['failures'] == 1
        assert metrics['avg_execution_time_ms'] > 0
    
    def test_metrics_reset(self):
        """Test that metrics can be reset."""
        self.parser.parse("https://claude.ai/chat/abc123de-f456-7890-abcd-ef1234567890")
        self.parser.reset_metrics()
        
        metrics = self.parser.get_metrics()
        
        assert metrics['total_processed'] == 0
        assert metrics['successes'] == 0
        assert metrics['failures'] == 0
    
    def test_conversation_identifier_dataclass(self):
        """Test ConversationIdentifier properties."""
        conv_id = ConversationIdentifier(
            conv_id="test-id",
            project_id="proj-123",
            is_project_conv=True
        )
        
        assert conv_id.conv_id == "test-id"
        assert conv_id.project_id == "proj-123"
        assert conv_id.is_project_conv
        assert conv_id.org_id is None
        assert conv_id.platform == "claude.ai"


class TestURLParserEdgeCases:
    """Test edge cases and error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = URLParser()
    
    def test_empty_url(self):
        """Test that empty URL is rejected."""
        with pytest.raises(ValueError):
            self.parser.parse("")
    
    def test_whitespace_url(self):
        """Test that whitespace-only URL is rejected."""
        with pytest.raises(ValueError):
            self.parser.parse("   ")
    
    def test_malformed_url(self):
        """Test various malformed URLs."""
        malformed_urls = [
            "not-a-url",
            "http://",
            "https://claude.ai",
            "https://claude.ai/",
            "https://claude.ai/chat/",
        ]
        
        for url in malformed_urls:
            with pytest.raises(ValueError):
                self.parser.parse(url)
    
    def test_url_with_query_params(self):
        """Test URL with query parameters (should still work)."""
        url = "https://claude.ai/chat/abc123de-f456-7890-abcd-ef1234567890?foo=bar"
        result = self.parser.parse(url)
        
        assert result.conv_id == "abc123de-f456-7890-abcd-ef1234567890"
    
    def test_url_with_fragment(self):
        """Test URL with fragment (should still work)."""
        url = "https://claude.ai/chat/abc123de-f456-7890-abcd-ef1234567890#section"
        result = self.parser.parse(url)
        
        assert result.conv_id == "abc123de-f456-7890-abcd-ef1234567890"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
