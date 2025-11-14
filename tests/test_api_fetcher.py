"""
Unit tests for API Data Fetcher nano-agent.

Run with: pytest tests/test_api_fetcher.py -v
"""

import pytest
import asyncio
from pathlib import Path
from nano_agents.api_fetcher import APIDataFetcher, FetchStrategy
import json
import tempfile


class TestAPIDataFetcher:
    """Test suite for APIDataFetcher class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = APIDataFetcher()

    @pytest.mark.asyncio
    async def test_fetch_from_file_valid_json(self):
        """Test loading valid conversation from file."""
        # Create temporary JSON file
        test_data = {
            "id": "test-conv-id",
            "messages": [
                {
                    "id": "msg_1",
                    "parent_id": None,
                    "role": "user",
                    "content": "Test message",
                    "timestamp": "2024-01-01T10:00:00Z"
                }
            ],
            "metadata": {"title": "Test Conversation"}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            result = await self.fetcher.fetch_from_file(temp_path)

            assert result["id"] == "test-conv-id"
            assert len(result["messages"]) == 1
            assert result["messages"][0]["content"] == "Test message"
        finally:
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_fetch_from_file_not_found(self):
        """Test that missing file raises error."""
        nonexistent_path = Path("/tmp/nonexistent-file-12345.json")

        with pytest.raises(FileNotFoundError, match="Manual export file not found"):
            await self.fetcher.fetch_from_file(nonexistent_path)

    @pytest.mark.asyncio
    async def test_fetch_from_file_invalid_json(self):
        """Test that invalid JSON raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json {")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                await self.fetcher.fetch_from_file(temp_path)
        finally:
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_fetch_from_file_missing_messages(self):
        """Test that data without messages field is rejected."""
        test_data = {"id": "test-id"}  # Missing 'messages'

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="missing 'messages' field"):
                await self.fetcher.fetch_from_file(temp_path)
        finally:
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_fetch_prompts_manual_export(self):
        """Test that fetch() prompts for manual export in Phase 1."""
        result = await self.fetcher.fetch("test-conv-id")

        assert result["status"] == "manual_export_required"
        assert result["conv_id"] == "test-conv-id"
        assert "instructions" in result
        assert len(result["instructions"]) > 0

    def test_metrics_tracking(self):
        """Test that metrics are tracked correctly."""
        metrics = self.fetcher.get_metrics()

        assert "overall_success_rate" in metrics
        assert "strategy_breakdown" in metrics
        assert "total_cost_usd" in metrics
        assert "phase" in metrics
        assert metrics["phase"] == "1 (manual export only)"

    @pytest.mark.asyncio
    async def test_strategy_attempts_tracked(self):
        """Test that strategy attempts are tracked."""
        # Trigger manual export
        await self.fetcher.fetch("test-conv-id")

        metrics = self.fetcher.get_metrics()
        manual_stats = metrics["strategy_breakdown"]["manual"]

        assert manual_stats["attempts"] == 1


class TestAPIDataFetcherValidation:
    """Test data validation logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = APIDataFetcher()

    def test_validate_empty_messages_list(self):
        """Test that empty messages list is rejected."""
        data = {"messages": []}

        with pytest.raises(ValueError, match="'messages' list is empty"):
            self.fetcher._validate_conversation_data(data)

    def test_validate_non_list_messages(self):
        """Test that non-list messages field is rejected."""
        data = {"messages": "not a list"}

        with pytest.raises(ValueError, match="'messages' must be a list"):
            self.fetcher._validate_conversation_data(data)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
