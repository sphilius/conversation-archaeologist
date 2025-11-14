"""
Batch Export Parser Nano-Agent

Handles Claude.ai batch export format which includes ALL conversations in one export.

Claude exports contain:
- conversations.json: Array of all conversations
- projects.json: Project data
- memories.json: Memory/context data
- users.json: User information

Quality Metrics:
- Parse success rate: Target 100%
- Extraction accuracy: 100%
- Performance: O(n) where n = number of conversations

Example Usage:
    >>> parser = BatchExportParser()
    >>> conversations = parser.parse_batch_export(Path("conversations.json"))
    >>> print(f"Found {len(conversations)} conversations")
    >>> selected = parser.select_conversation(conversations, conv_id="abc-123")
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
import json


@dataclass
class ConversationMetadata:
    """
    Metadata for a single conversation in the batch export.

    Attributes:
        uuid: Conversation UUID
        name: Conversation title/name
        created_at: Creation timestamp
        updated_at: Last update timestamp
        message_count: Number of messages in conversation
    """
    uuid: str
    name: str
    created_at: str
    updated_at: str
    message_count: int = 0


class BatchExportParser:
    """
    Parses Claude.ai batch export format.

    Claude exports all conversations in a single JSON file with structure:
    [
        {
            "uuid": "conversation-id",
            "name": "Conversation title",
            "created_at": "2024-11-14T...",
            "updated_at": "2024-11-14T...",
            "chat_messages": [...]  # Array of messages
        },
        ...
    ]

    Quality Metrics:
    - Parse success rate: Target 100%
    - Extraction accuracy: 100%
    - Performance: O(n) linear time
    """

    def __init__(self) -> None:
        """Initialize parser with quality tracking."""
        self.parse_count = 0
        self.error_count = 0

    def parse_batch_export(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse conversations.json from Claude batch export.

        Args:
            file_path: Path to conversations.json file

        Returns:
            List of conversation dictionaries

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
            ValueError: If file structure is invalid

        Examples:
            >>> parser = BatchExportParser()
            >>> conversations = parser.parse_batch_export(Path("conversations.json"))
            >>> len(conversations) > 0
            True
        """
        if not file_path.exists():
            raise FileNotFoundError(
                f"Batch export file not found: {file_path}\n"
                f"Expected: conversations.json from Claude.ai export"
            )

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check if it's a list (batch export) or dict (single conversation)
            if isinstance(data, list):
                # Batch export format
                conversations = data
                self.parse_count += 1
                return conversations
            elif isinstance(data, dict):
                # Check if it's a single conversation
                if 'chat_messages' in data or 'messages' in data:
                    # Single conversation - wrap in list
                    self.parse_count += 1
                    return [data]
                else:
                    raise ValueError(
                        f"Invalid conversation data structure.\n"
                        f"Expected list of conversations or single conversation dict.\n"
                        f"Found: {list(data.keys())[:5]}"
                    )
            else:
                raise ValueError(
                    f"Invalid JSON structure. Expected list or dict, got {type(data)}"
                )

        except json.JSONDecodeError as e:
            self.error_count += 1
            raise ValueError(
                f"Invalid JSON in export file: {file_path}\n"
                f"Error: {str(e)}"
            ) from e

    def extract_conversation_metadata(
        self,
        conversations: List[Dict[str, Any]]
    ) -> List[ConversationMetadata]:
        """
        Extract metadata from all conversations in batch.

        Args:
            conversations: List of conversation dictionaries

        Returns:
            List of ConversationMetadata objects

        Examples:
            >>> parser = BatchExportParser()
            >>> conversations = [{"uuid": "123", "name": "Test", ...}]
            >>> metadata = parser.extract_conversation_metadata(conversations)
            >>> metadata[0].uuid
            '123'
        """
        metadata_list = []

        for conv in conversations:
            # Handle both 'chat_messages' and 'messages' keys
            messages = conv.get('chat_messages', conv.get('messages', []))

            metadata = ConversationMetadata(
                uuid=conv.get('uuid', conv.get('id', 'unknown')),
                name=conv.get('name', conv.get('title', 'Untitled')),
                created_at=conv.get('created_at', ''),
                updated_at=conv.get('updated_at', ''),
                message_count=len(messages)
            )
            metadata_list.append(metadata)

        return metadata_list

    def select_conversation(
        self,
        conversations: List[Dict[str, Any]],
        conv_id: Optional[str] = None,
        index: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Select a specific conversation from batch export.

        Args:
            conversations: List of conversation dictionaries
            conv_id: UUID of conversation to select (optional)
            index: Index of conversation in list (optional)

        Returns:
            Selected conversation dictionary

        Raises:
            ValueError: If conversation not found or no selection criteria provided

        Examples:
            >>> parser = BatchExportParser()
            >>> conversations = [{"uuid": "123", ...}, {"uuid": "456", ...}]
            >>> conv = parser.select_conversation(conversations, conv_id="123")
            >>> conv['uuid']
            '123'
        """
        if conv_id is None and index is None:
            raise ValueError(
                "Must provide either conv_id or index to select conversation"
            )

        if index is not None:
            if 0 <= index < len(conversations):
                return conversations[index]
            else:
                raise ValueError(
                    f"Index {index} out of range. "
                    f"Batch has {len(conversations)} conversations (0-{len(conversations)-1})"
                )

        if conv_id is not None:
            for conv in conversations:
                # Check both 'uuid' and 'id' fields
                if conv.get('uuid') == conv_id or conv.get('id') == conv_id:
                    return conv

            raise ValueError(
                f"Conversation ID '{conv_id}' not found in batch export.\n"
                f"Batch contains {len(conversations)} conversations.\n"
                f"Use --list to see all available conversations."
            )

        raise ValueError("Invalid selection criteria")

    def normalize_conversation(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize conversation to expected format.

        Converts 'chat_messages' to 'messages', adds missing fields, etc.

        Args:
            conversation: Raw conversation dictionary

        Returns:
            Normalized conversation dictionary
        """
        normalized = conversation.copy()

        # Normalize messages field
        if 'chat_messages' in normalized and 'messages' not in normalized:
            normalized['messages'] = normalized.pop('chat_messages')

        # Ensure 'messages' exists
        if 'messages' not in normalized:
            normalized['messages'] = []

        # Normalize id field
        if 'uuid' in normalized and 'id' not in normalized:
            normalized['id'] = normalized['uuid']

        # Ensure metadata exists
        if 'metadata' not in normalized:
            normalized['metadata'] = {
                'title': normalized.get('name', 'Untitled'),
                'created_at': normalized.get('created_at', ''),
                'updated_at': normalized.get('updated_at', '')
            }

        return normalized

    def list_conversations(
        self,
        conversations: List[Dict[str, Any]],
        limit: int = 50
    ) -> str:
        """
        Generate formatted list of conversations.

        Args:
            conversations: List of conversation dictionaries
            limit: Maximum number to display

        Returns:
            Formatted string listing conversations
        """
        metadata_list = self.extract_conversation_metadata(conversations)

        output = []
        output.append(f"\n{'='*80}")
        output.append(f"Found {len(conversations)} conversations in batch export")
        output.append(f"{'='*80}\n")

        for i, meta in enumerate(metadata_list[:limit]):
            output.append(f"[{i}] {meta.name}")
            output.append(f"    UUID: {meta.uuid}")
            output.append(f"    Messages: {meta.message_count}")
            output.append(f"    Updated: {meta.updated_at[:10]}")  # Show date only
            output.append("")

        if len(conversations) > limit:
            output.append(f"... and {len(conversations) - limit} more conversations")
            output.append(f"Use --limit to see more")

        output.append(f"{'='*80}")
        output.append(f"To extract a specific conversation:")
        output.append(f"  By index: python scripts/extract.py --from-file FILE --index 0")
        output.append(f"  By UUID:  python scripts/extract.py --from-file FILE --conv-id UUID")
        output.append(f"{'='*80}\n")

        return "\n".join(output)

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get quality metrics for parser.

        Returns:
            Dictionary with parser statistics
        """
        total = self.parse_count + self.error_count
        return {
            "total_parses": total,
            "successful_parses": self.parse_count,
            "failed_parses": self.error_count,
            "success_rate": self.parse_count / total if total > 0 else 0
        }


if __name__ == "__main__":
    # Quick test
    parser = BatchExportParser()

    print("Batch Export Parser")
    print("=" * 60)
    print("This parser handles Claude.ai batch exports.")
    print("Batch exports contain ALL conversations in one JSON file.")
    print("")
    print("Expected file structure:")
    print("  conversations.json - Array of all conversations")
    print("  projects.json - Project data")
    print("  memories.json - Memory/context data")
    print("  users.json - User information")
    print("=" * 60)
