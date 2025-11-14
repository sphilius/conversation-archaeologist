"""
Unit tests for Batch Export Parser nano-agent.

Run with: pytest tests/test_batch_parser.py -v
"""

import pytest
import json
import tempfile
from pathlib import Path
from nano_agents.batch_parser import BatchExportParser, ConversationMetadata


class TestBatchExportParser:
    """Test suite for BatchExportParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = BatchExportParser()

        # Sample batch export data (array format)
        self.batch_data = [
            {
                "uuid": "conv-001",
                "name": "Test Conversation 1",
                "created_at": "2024-11-14T10:00:00Z",
                "updated_at": "2024-11-14T11:00:00Z",
                "chat_messages": [
                    {"id": "msg1", "role": "user", "content": "Hello"}
                ]
            },
            {
                "uuid": "conv-002",
                "name": "Test Conversation 2",
                "created_at": "2024-11-14T12:00:00Z",
                "updated_at": "2024-11-14T13:00:00Z",
                "chat_messages": [
                    {"id": "msg2", "role": "user", "content": "Hi"},
                    {"id": "msg3", "role": "assistant", "content": "Hello!"}
                ]
            }
        ]

        # Sample single conversation (dict format)
        self.single_data = {
            "uuid": "conv-single",
            "name": "Single Conversation",
            "created_at": "2024-11-14T14:00:00Z",
            "updated_at": "2024-11-14T15:00:00Z",
            "chat_messages": [
                {"id": "msg4", "role": "user", "content": "Test"}
            ]
        }

    def test_parse_batch_export_list_format(self):
        """Test parsing batch export with list format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.batch_data, f)
            temp_path = Path(f.name)

        try:
            conversations = self.parser.parse_batch_export(temp_path)

            assert len(conversations) == 2
            assert conversations[0]['uuid'] == 'conv-001'
            assert conversations[1]['uuid'] == 'conv-002'
            assert self.parser.parse_count == 1
            assert self.parser.error_count == 0
        finally:
            temp_path.unlink()

    def test_parse_single_conversation_dict_format(self):
        """Test parsing single conversation with dict format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.single_data, f)
            temp_path = Path(f.name)

        try:
            conversations = self.parser.parse_batch_export(temp_path)

            # Single conversation should be wrapped in list
            assert len(conversations) == 1
            assert conversations[0]['uuid'] == 'conv-single'
            assert self.parser.parse_count == 1
        finally:
            temp_path.unlink()

    def test_parse_file_not_found(self):
        """Test that missing file raises FileNotFoundError."""
        non_existent = Path("/tmp/does_not_exist_12345.json")

        with pytest.raises(FileNotFoundError, match="Batch export file not found"):
            self.parser.parse_batch_export(non_existent)

    def test_parse_invalid_json(self):
        """Test that invalid JSON raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                self.parser.parse_batch_export(temp_path)
            assert self.parser.error_count == 1
        finally:
            temp_path.unlink()

    def test_parse_invalid_structure(self):
        """Test that invalid structure raises ValueError."""
        invalid_data = {"some": "dict", "without": "messages"}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Invalid conversation data structure"):
                self.parser.parse_batch_export(temp_path)
        finally:
            temp_path.unlink()

    def test_parse_invalid_type(self):
        """Test that non-list/dict type raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump("just a string", f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Invalid JSON structure"):
                self.parser.parse_batch_export(temp_path)
        finally:
            temp_path.unlink()


class TestConversationSelection:
    """Test conversation selection methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = BatchExportParser()
        self.conversations = [
            {"uuid": "abc-123", "name": "Conv 1", "chat_messages": []},
            {"uuid": "def-456", "name": "Conv 2", "chat_messages": []},
            {"id": "ghi-789", "name": "Conv 3", "messages": []}  # Different field names
        ]

    def test_select_by_index_valid(self):
        """Test selecting conversation by valid index."""
        conv = self.parser.select_conversation(self.conversations, index=0)
        assert conv['uuid'] == 'abc-123'

        conv = self.parser.select_conversation(self.conversations, index=1)
        assert conv['uuid'] == 'def-456'

        conv = self.parser.select_conversation(self.conversations, index=2)
        assert conv['id'] == 'ghi-789'

    def test_select_by_index_out_of_range(self):
        """Test that out of range index raises ValueError."""
        with pytest.raises(ValueError, match="Index .* out of range"):
            self.parser.select_conversation(self.conversations, index=10)

        with pytest.raises(ValueError, match="Index .* out of range"):
            self.parser.select_conversation(self.conversations, index=-1)

    def test_select_by_conv_id_uuid_field(self):
        """Test selecting conversation by UUID (uuid field)."""
        conv = self.parser.select_conversation(self.conversations, conv_id="abc-123")
        assert conv['name'] == 'Conv 1'

        conv = self.parser.select_conversation(self.conversations, conv_id="def-456")
        assert conv['name'] == 'Conv 2'

    def test_select_by_conv_id_id_field(self):
        """Test selecting conversation by UUID (id field)."""
        conv = self.parser.select_conversation(self.conversations, conv_id="ghi-789")
        assert conv['name'] == 'Conv 3'

    def test_select_by_conv_id_not_found(self):
        """Test that missing conv_id raises ValueError."""
        with pytest.raises(ValueError, match="Conversation ID .* not found"):
            self.parser.select_conversation(self.conversations, conv_id="xyz-999")

    def test_select_no_criteria(self):
        """Test that missing both index and conv_id raises ValueError."""
        with pytest.raises(ValueError, match="Must provide either conv_id or index"):
            self.parser.select_conversation(self.conversations)


class TestMetadataExtraction:
    """Test metadata extraction methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = BatchExportParser()

    def test_extract_metadata_with_chat_messages(self):
        """Test metadata extraction with 'chat_messages' field."""
        conversations = [
            {
                "uuid": "conv-001",
                "name": "Test Conv",
                "created_at": "2024-11-14T10:00:00Z",
                "updated_at": "2024-11-14T11:00:00Z",
                "chat_messages": [{"id": "1"}, {"id": "2"}, {"id": "3"}]
            }
        ]

        metadata_list = self.parser.extract_conversation_metadata(conversations)

        assert len(metadata_list) == 1
        meta = metadata_list[0]
        assert meta.uuid == "conv-001"
        assert meta.name == "Test Conv"
        assert meta.message_count == 3
        assert meta.created_at == "2024-11-14T10:00:00Z"
        assert meta.updated_at == "2024-11-14T11:00:00Z"

    def test_extract_metadata_with_messages(self):
        """Test metadata extraction with 'messages' field."""
        conversations = [
            {
                "id": "conv-002",
                "title": "Another Conv",
                "created_at": "2024-11-14T12:00:00Z",
                "updated_at": "2024-11-14T13:00:00Z",
                "messages": [{"id": "1"}, {"id": "2"}]
            }
        ]

        metadata_list = self.parser.extract_conversation_metadata(conversations)

        assert len(metadata_list) == 1
        meta = metadata_list[0]
        assert meta.uuid == "conv-002"  # Should fallback to 'id'
        assert meta.name == "Another Conv"  # Should fallback to 'title'
        assert meta.message_count == 2

    def test_extract_metadata_missing_fields(self):
        """Test metadata extraction with missing optional fields."""
        conversations = [
            {
                # Minimal conversation with defaults
                "chat_messages": []
            }
        ]

        metadata_list = self.parser.extract_conversation_metadata(conversations)

        assert len(metadata_list) == 1
        meta = metadata_list[0]
        assert meta.uuid == "unknown"
        assert meta.name == "Untitled"
        assert meta.message_count == 0
        assert meta.created_at == ""
        assert meta.updated_at == ""

    def test_extract_metadata_multiple_conversations(self):
        """Test metadata extraction from multiple conversations."""
        conversations = [
            {"uuid": "1", "name": "Conv 1", "chat_messages": [{"id": "a"}]},
            {"uuid": "2", "name": "Conv 2", "chat_messages": [{"id": "b"}, {"id": "c"}]},
            {"uuid": "3", "name": "Conv 3", "messages": [{"id": "d"}, {"id": "e"}, {"id": "f"}]}
        ]

        metadata_list = self.parser.extract_conversation_metadata(conversations)

        assert len(metadata_list) == 3
        assert metadata_list[0].message_count == 1
        assert metadata_list[1].message_count == 2
        assert metadata_list[2].message_count == 3


class TestConversationNormalization:
    """Test conversation normalization methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = BatchExportParser()

    def test_normalize_chat_messages_to_messages(self):
        """Test conversion of 'chat_messages' to 'messages'."""
        conversation = {
            "uuid": "test",
            "chat_messages": [{"id": "1"}]
        }

        normalized = self.parser.normalize_conversation(conversation)

        assert 'messages' in normalized
        assert 'chat_messages' not in normalized
        assert len(normalized['messages']) == 1

    def test_normalize_uuid_to_id(self):
        """Test conversion of 'uuid' to 'id'."""
        conversation = {
            "uuid": "test-uuid-123",
            "messages": []
        }

        normalized = self.parser.normalize_conversation(conversation)

        assert 'id' in normalized
        assert normalized['id'] == "test-uuid-123"
        assert 'uuid' in normalized  # Original preserved

    def test_normalize_adds_metadata(self):
        """Test that missing metadata is added."""
        conversation = {
            "uuid": "test",
            "name": "Test Conversation",
            "created_at": "2024-11-14T10:00:00Z",
            "updated_at": "2024-11-14T11:00:00Z",
            "messages": []
        }

        normalized = self.parser.normalize_conversation(conversation)

        assert 'metadata' in normalized
        assert normalized['metadata']['title'] == "Test Conversation"
        assert normalized['metadata']['created_at'] == "2024-11-14T10:00:00Z"
        assert normalized['metadata']['updated_at'] == "2024-11-14T11:00:00Z"

    def test_normalize_preserves_existing_metadata(self):
        """Test that existing metadata is preserved."""
        conversation = {
            "uuid": "test",
            "messages": [],
            "metadata": {
                "title": "Existing Title",
                "custom_field": "custom_value"
            }
        }

        normalized = self.parser.normalize_conversation(conversation)

        # Should preserve original metadata
        assert normalized['metadata']['title'] == "Existing Title"
        assert normalized['metadata']['custom_field'] == "custom_value"

    def test_normalize_adds_empty_messages(self):
        """Test that missing messages array is added."""
        conversation = {
            "uuid": "test",
            "name": "Test"
        }

        normalized = self.parser.normalize_conversation(conversation)

        assert 'messages' in normalized
        assert normalized['messages'] == []

    def test_normalize_full_conversion(self):
        """Test full normalization of batch export format."""
        conversation = {
            "uuid": "abc-123",
            "name": "Full Test",
            "created_at": "2024-11-14T10:00:00Z",
            "updated_at": "2024-11-14T11:00:00Z",
            "chat_messages": [
                {"id": "msg1", "content": "Hello"}
            ]
        }

        normalized = self.parser.normalize_conversation(conversation)

        # Check all normalizations
        assert 'id' in normalized
        assert normalized['id'] == "abc-123"
        assert 'messages' in normalized
        assert 'chat_messages' not in normalized
        assert len(normalized['messages']) == 1
        assert 'metadata' in normalized
        assert normalized['metadata']['title'] == "Full Test"


class TestListConversations:
    """Test conversation listing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = BatchExportParser()

    def test_list_conversations_basic(self):
        """Test basic conversation listing."""
        conversations = [
            {
                "uuid": "conv-1",
                "name": "First Conversation",
                "created_at": "2024-11-14T10:00:00Z",
                "updated_at": "2024-11-14T11:00:00Z",
                "chat_messages": [{"id": "1"}]
            },
            {
                "uuid": "conv-2",
                "name": "Second Conversation",
                "created_at": "2024-11-14T12:00:00Z",
                "updated_at": "2024-11-14T13:00:00Z",
                "chat_messages": [{"id": "2"}, {"id": "3"}]
            }
        ]

        listing = self.parser.list_conversations(conversations, limit=50)

        assert "Found 2 conversations" in listing
        assert "[0] First Conversation" in listing
        assert "[1] Second Conversation" in listing
        assert "conv-1" in listing
        assert "conv-2" in listing
        assert "Messages: 1" in listing
        assert "Messages: 2" in listing

    def test_list_conversations_with_limit(self):
        """Test conversation listing with limit."""
        conversations = [
            {"uuid": f"conv-{i}", "name": f"Conv {i}", "chat_messages": []}
            for i in range(100)
        ]

        listing = self.parser.list_conversations(conversations, limit=10)

        assert "Found 100 conversations" in listing
        assert "[0] Conv 0" in listing
        assert "[9] Conv 9" in listing
        assert "and 90 more conversations" in listing
        assert "Use --limit to see more" in listing

    def test_list_conversations_empty(self):
        """Test listing with no conversations."""
        conversations = []

        listing = self.parser.list_conversations(conversations, limit=50)

        assert "Found 0 conversations" in listing


class TestQualityMetrics:
    """Test quality metrics tracking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = BatchExportParser()

    def test_metrics_initial_state(self):
        """Test that metrics start at zero."""
        metrics = self.parser.get_metrics()

        assert metrics['total_parses'] == 0
        assert metrics['successful_parses'] == 0
        assert metrics['failed_parses'] == 0
        assert metrics['success_rate'] == 0

    def test_metrics_successful_parse(self):
        """Test metrics after successful parse."""
        # Create temp file with valid data
        data = [{"uuid": "test", "chat_messages": []}]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            self.parser.parse_batch_export(temp_path)
            metrics = self.parser.get_metrics()

            assert metrics['total_parses'] == 1
            assert metrics['successful_parses'] == 1
            assert metrics['failed_parses'] == 0
            assert metrics['success_rate'] == 1.0
        finally:
            temp_path.unlink()

    def test_metrics_failed_parse(self):
        """Test metrics after failed parse."""
        # Create temp file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError):
                self.parser.parse_batch_export(temp_path)

            metrics = self.parser.get_metrics()

            assert metrics['total_parses'] == 1
            assert metrics['successful_parses'] == 0
            assert metrics['failed_parses'] == 1
            assert metrics['success_rate'] == 0.0
        finally:
            temp_path.unlink()

    def test_metrics_multiple_parses(self):
        """Test metrics with multiple parse operations."""
        # Create temp file with valid data
        data = [{"uuid": "test", "chat_messages": []}]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            # Successful parse
            self.parser.parse_batch_export(temp_path)
            self.parser.parse_batch_export(temp_path)

            # Failed parse
            temp_path.unlink()
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
                f2.write("invalid")
                temp_path2 = Path(f2.name)

            try:
                with pytest.raises(ValueError):
                    self.parser.parse_batch_export(temp_path2)
            finally:
                temp_path2.unlink()

            metrics = self.parser.get_metrics()

            assert metrics['total_parses'] == 3
            assert metrics['successful_parses'] == 2
            assert metrics['failed_parses'] == 1
            assert metrics['success_rate'] == pytest.approx(0.666, abs=0.01)
        except:
            if temp_path.exists():
                temp_path.unlink()
            raise


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
