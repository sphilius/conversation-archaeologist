"""
JSON exporter for LLM-optimized conversation format.

Exports conversations in a flat, easily parseable JSON structure
optimized for AI/LLM consumption and RAG systems.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from claude_extractor.models import Conversation


class JSONExporter:
    """
    Export conversations to LLM-optimized JSON format.
    
    The output format is designed to be:
    - Flat structure (minimal nesting)
    - Easy to parse and search
    - Suitable for RAG/embedding systems
    - Preserves all important metadata
    """
    
    def __init__(
        self,
        pretty: bool = True,
        indent: int = 2,
        include_metadata: bool = True,
    ):
        """
        Initialize JSON exporter.
        
        Args:
            pretty: Pretty print with indentation
            indent: Number of spaces for indentation
            include_metadata: Include extraction metadata
        """
        self.pretty = pretty
        self.indent = indent if pretty else None
        self.include_metadata = include_metadata
    
    def export(self, conversation: Conversation, output_path: Path) -> None:
        """
        Export conversation to JSON file.
        
        Args:
            conversation: Conversation object to export
            output_path: Path to output JSON file
        """
        logger.info(f"Exporting conversation to JSON: {output_path}")
        
        # Convert to dictionary
        data = self._conversation_to_dict(conversation)
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=self.indent, ensure_ascii=False, default=str)
        
        logger.success(f"JSON export complete: {output_path}")
    
    def export_string(self, conversation: Conversation) -> str:
        """
        Export conversation to JSON string.
        
        Args:
            conversation: Conversation object to export
        
        Returns:
            JSON string
        """
        data = self._conversation_to_dict(conversation)
        return json.dumps(data, indent=self.indent, ensure_ascii=False, default=str)
    
    def _conversation_to_dict(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Convert conversation to LLM-optimized dictionary.
        
        Creates a flat structure with:
        - Metadata at top level
        - All messages in simple array
        - All artifacts in simple array
        - Statistics readily accessible
        """
        data = {
            "format_version": "1.0.0",
            "conversation_id": conversation.metadata.id,
            "conversation_url": conversation.metadata.url,
            "conversation_title": conversation.metadata.title,
            "model": conversation.metadata.model,
            "created_at": conversation.metadata.created_at.isoformat(),
            "updated_at": conversation.metadata.updated_at.isoformat(),
        }
        
        # Add project info if available
        if conversation.metadata.project_id:
            data["project_id"] = conversation.metadata.project_id
            data["project_name"] = conversation.metadata.project_name
        
        # Add custom instructions if available
        if conversation.metadata.custom_instructions:
            data["custom_instructions"] = conversation.metadata.custom_instructions
        
        # Add active skills
        if conversation.metadata.active_skills:
            data["active_skills"] = conversation.metadata.active_skills
        
        # Add system prompt if available
        if conversation.system_prompt:
            data["system_prompt"] = conversation.system_prompt
        
        # Statistics
        data["statistics"] = {
            "total_messages": conversation.statistics.total_messages,
            "user_messages": conversation.statistics.user_messages,
            "assistant_messages": conversation.statistics.assistant_messages,
            "total_tokens": conversation.statistics.total_tokens,
            "user_tokens": conversation.statistics.user_tokens,
            "assistant_tokens": conversation.statistics.assistant_tokens,
            "artifact_count": conversation.statistics.artifact_count,
            "tool_call_count": conversation.statistics.tool_call_count,
            "branch_count": conversation.statistics.branch_count,
            "thinking_messages": conversation.statistics.thinking_messages,
            "average_message_length": conversation.statistics.average_message_length,
            "conversation_duration_minutes": conversation.statistics.conversation_duration_minutes,
        }
        
        # Messages (flat array)
        data["messages"] = []
        for msg in conversation.messages:
            msg_dict = {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "branch_id": msg.branch_id,
            }
            
            if msg.parent_id:
                msg_dict["parent_id"] = msg.parent_id
            
            if msg.tokens:
                msg_dict["tokens"] = msg.tokens
            
            if msg.thinking_content:
                msg_dict["thinking_content"] = msg.thinking_content
            
            if msg.artifacts:
                msg_dict["artifacts"] = msg.artifacts
            
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            
            if msg.metadata:
                msg_dict["metadata"] = msg.metadata
            
            data["messages"].append(msg_dict)
        
        # Artifacts (flat array)
        data["artifacts"] = []
        for art in conversation.artifacts:
            art_dict = {
                "id": art.id,
                "type": art.type.value,
                "title": art.title,
                "content": art.content,
                "created_in_message": art.created_in_message,
                "created_at": art.created_at.isoformat(),
                "version": art.version,
            }
            
            if art.language:
                art_dict["language"] = art.language
            
            if art.version_history:
                art_dict["version_history"] = art.version_history
            
            if art.metadata:
                art_dict["metadata"] = art.metadata
            
            data["artifacts"].append(art_dict)
        
        # Branches
        data["branches"] = []
        for branch in conversation.branches:
            branch_dict = {
                "id": branch.id,
                "parent_message_id": branch.parent_message_id,
                "created_at": branch.created_at.isoformat(),
                "is_active": branch.is_active,
                "message_ids": branch.message_ids,
            }
            
            if branch.name:
                branch_dict["name"] = branch.name
            
            if branch.metadata:
                branch_dict["metadata"] = branch.metadata
            
            data["branches"].append(branch_dict)
        
        # Tool calls
        data["tool_calls"] = []
        for tool in conversation.tool_calls:
            tool_dict = {
                "id": tool.id,
                "tool_name": tool.tool_name,
                "message_id": tool.message_id,
                "timestamp": tool.timestamp.isoformat(),
                "parameters": tool.parameters,
                "status": tool.status.value,
            }
            
            if tool.result:
                tool_dict["result"] = tool.result
            
            if tool.error:
                tool_dict["error"] = tool.error
            
            if tool.execution_time_ms:
                tool_dict["execution_time_ms"] = tool.execution_time_ms
            
            data["tool_calls"].append(tool_dict)
        
        # Extraction metadata
        if self.include_metadata and conversation.extraction_metadata:
            data["extraction_metadata"] = conversation.extraction_metadata
        
        return data
