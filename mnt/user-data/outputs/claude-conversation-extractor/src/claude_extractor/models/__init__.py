"""
Data models for Claude conversation extraction.

These Pydantic models define the structure of extracted conversation data
and provide validation, serialization, and type safety.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ArtifactType(str, Enum):
    """Artifact type enumeration."""
    CODE = "code"
    MARKDOWN = "markdown"
    HTML = "html"
    REACT = "react"
    MERMAID = "mermaid"
    SVG = "svg"
    TEXT = "text"
    UNKNOWN = "unknown"


class ToolCallStatus(str, Enum):
    """Tool call status enumeration."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


class Message(BaseModel):
    """Represents a single message in a conversation."""
    
    id: str = Field(..., description="Unique message identifier")
    role: MessageRole = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content text")
    timestamp: datetime = Field(..., description="Message creation timestamp")
    parent_id: Optional[str] = Field(None, description="Parent message ID")
    branch_id: str = Field(..., description="Branch this message belongs to")
    tokens: Optional[int] = Field(None, description="Token count for this message")
    thinking_content: Optional[str] = Field(None, description="Claude's thinking process")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool invocations")
    artifacts: List[str] = Field(default_factory=list, description="Artifact IDs in this message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Artifact(BaseModel):
    """Represents an artifact created in the conversation."""
    
    id: str = Field(..., description="Unique artifact identifier")
    type: ArtifactType = Field(..., description="Type of artifact")
    title: str = Field(..., description="Artifact title")
    content: str = Field(..., description="Artifact content")
    language: Optional[str] = Field(None, description="Programming language (for code artifacts)")
    created_in_message: str = Field(..., description="Message ID where artifact was created")
    created_at: datetime = Field(..., description="Creation timestamp")
    version: int = Field(1, description="Version number")
    version_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Version history"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Branch(BaseModel):
    """Represents a conversation branch."""
    
    id: str = Field(..., description="Unique branch identifier")
    name: Optional[str] = Field(None, description="Branch name")
    parent_message_id: str = Field(..., description="Message ID where branch diverges")
    created_at: datetime = Field(..., description="Branch creation timestamp")
    is_active: bool = Field(False, description="Whether this is the active branch")
    message_ids: List[str] = Field(default_factory=list, description="Message IDs in this branch")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ToolCall(BaseModel):
    """Represents a tool call made by Claude."""
    
    id: str = Field(..., description="Tool call identifier")
    tool_name: str = Field(..., description="Name of the tool invoked")
    message_id: str = Field(..., description="Message ID where tool was called")
    timestamp: datetime = Field(..., description="Tool call timestamp")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    result: Optional[Dict[str, Any]] = Field(None, description="Tool execution result")
    status: ToolCallStatus = Field(ToolCallStatus.SUCCESS, description="Tool call status")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationMetadata(BaseModel):
    """Metadata about the conversation."""
    
    id: str = Field(..., description="Conversation ID")
    url: str = Field(..., description="Conversation URL")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    model: str = Field(..., description="Claude model used")
    project_id: Optional[str] = Field(None, description="Project ID if in a project")
    project_name: Optional[str] = Field(None, description="Project name if in a project")
    custom_instructions: Optional[str] = Field(None, description="User's custom instructions")
    active_skills: List[str] = Field(default_factory=list, description="Skills active in conversation")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationStatistics(BaseModel):
    """Statistics about the conversation."""
    
    total_messages: int = Field(0, description="Total number of messages")
    user_messages: int = Field(0, description="Number of user messages")
    assistant_messages: int = Field(0, description="Number of assistant messages")
    total_tokens: int = Field(0, description="Total token count")
    user_tokens: int = Field(0, description="User token count")
    assistant_tokens: int = Field(0, description="Assistant token count")
    artifact_count: int = Field(0, description="Number of artifacts")
    tool_call_count: int = Field(0, description="Number of tool calls")
    branch_count: int = Field(0, description="Number of branches")
    thinking_messages: int = Field(0, description="Messages with thinking content")
    average_message_length: float = Field(0.0, description="Average message length")
    conversation_duration_minutes: float = Field(0.0, description="Duration in minutes")


class Conversation(BaseModel):
    """Complete conversation data structure."""
    
    metadata: ConversationMetadata = Field(..., description="Conversation metadata")
    messages: List[Message] = Field(default_factory=list, description="All messages")
    artifacts: List[Artifact] = Field(default_factory=list, description="All artifacts")
    branches: List[Branch] = Field(default_factory=list, description="All branches")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="All tool calls")
    statistics: ConversationStatistics = Field(
        default_factory=ConversationStatistics,
        description="Conversation statistics"
    )
    system_prompt: Optional[str] = Field(None, description="System prompt if available")
    extraction_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the extraction process"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_llm_json(self) -> Dict[str, Any]:
        """
        Export to LLM-optimized JSON format.
        
        Returns flat structure with minimal nesting for better LLM consumption.
        """
        return {
            "format_version": "1.0.0",
            "conversation_id": self.metadata.id,
            "conversation_url": self.metadata.url,
            "conversation_title": self.metadata.title,
            "model": self.metadata.model,
            "created_at": self.metadata.created_at.isoformat(),
            "updated_at": self.metadata.updated_at.isoformat(),
            "project_id": self.metadata.project_id,
            "project_name": self.metadata.project_name,
            "total_messages": self.statistics.total_messages,
            "total_tokens": self.statistics.total_tokens,
            "messages": [msg.dict() for msg in self.messages],
            "artifacts": [art.dict() for art in self.artifacts],
            "branches": [branch.dict() for branch in self.branches],
            "tool_calls": [tool.dict() for tool in self.tool_calls],
            "statistics": self.statistics.dict(),
            "system_prompt": self.system_prompt,
            "extraction_metadata": self.extraction_metadata,
        }

    def get_active_branch_messages(self) -> List[Message]:
        """Get messages from the active branch."""
        active_branch = next((b for b in self.branches if b.is_active), None)
        if not active_branch:
            return self.messages
        
        active_msg_ids = set(active_branch.message_ids)
        return [msg for msg in self.messages if msg.id in active_msg_ids]

    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """Get a specific message by ID."""
        return next((msg for msg in self.messages if msg.id == message_id), None)

    def get_artifacts_in_message(self, message_id: str) -> List[Artifact]:
        """Get all artifacts created in a specific message."""
        return [art for art in self.artifacts if art.created_in_message == message_id]
