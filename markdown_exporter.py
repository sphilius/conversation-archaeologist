"""
Markdown exporter for human-friendly conversation reports.

Generates beautiful, readable Markdown reports with:
- Summary statistics
- Conversation flow visualization
- Full message content
- Artifact listings
- Tool usage analysis
"""

from datetime import datetime
from pathlib import Path
from typing import List

from loguru import logger

from claude_extractor.models import Artifact, Conversation, Message, MessageRole


class MarkdownExporter:
    """
    Export conversations to human-friendly Markdown format.
    
    Creates comprehensive reports with proper formatting, statistics,
    and optional Mermaid diagrams for visualization.
    """
    
    def __init__(
        self,
        include_statistics: bool = True,
        include_mermaid: bool = True,
        include_artifacts: bool = True,
        include_tool_analysis: bool = True,
    ):
        """
        Initialize Markdown exporter.
        
        Args:
            include_statistics: Include statistics section
            include_mermaid: Include Mermaid diagrams
            include_artifacts: Include artifact content
            include_tool_analysis: Include tool usage analysis
        """
        self.include_statistics = include_statistics
        self.include_mermaid = include_mermaid
        self.include_artifacts = include_artifacts
        self.include_tool_analysis = include_tool_analysis
    
    def export(self, conversation: Conversation, output_path: Path) -> None:
        """
        Export conversation to Markdown file.
        
        Args:
            conversation: Conversation object to export
            output_path: Path to output Markdown file
        """
        logger.info(f"Exporting conversation to Markdown: {output_path}")
        
        # Generate Markdown content
        markdown = self._generate_markdown(conversation)
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        
        logger.success(f"Markdown export complete: {output_path}")
    
    def export_string(self, conversation: Conversation) -> str:
        """
        Export conversation to Markdown string.
        
        Args:
            conversation: Conversation object to export
        
        Returns:
            Markdown string
        """
        return self._generate_markdown(conversation)
    
    def _generate_markdown(self, conversation: Conversation) -> str:
        """Generate complete Markdown report."""
        sections = []
        
        # Header
        sections.append(self._generate_header(conversation))
        
        # Summary Statistics
        if self.include_statistics:
            sections.append(self._generate_statistics(conversation))
        
        # Conversation Flow Diagram
        if self.include_mermaid:
            sections.append(self._generate_mermaid(conversation))
        
        # Full Conversation
        sections.append(self._generate_conversation(conversation))
        
        # Artifacts
        if self.include_artifacts and conversation.artifacts:
            sections.append(self._generate_artifacts(conversation))
        
        # Tool Usage Analysis
        if self.include_tool_analysis and conversation.tool_calls:
            sections.append(self._generate_tool_analysis(conversation))
        
        # System Configuration
        sections.append(self._generate_system_config(conversation))
        
        # Footer
        sections.append(self._generate_footer(conversation))
        
        return "\n\n".join(sections)
    
    def _generate_header(self, conversation: Conversation) -> str:
        """Generate report header."""
        meta = conversation.metadata
        return f"""# Conversation Export Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Source**: [{meta.url}]({meta.url})  
**Conversation ID**: `{meta.id}`  
**Title**: {meta.title}

---"""
    
    def _generate_statistics(self, conversation: Conversation) -> str:
        """Generate statistics section."""
        stats = conversation.statistics
        meta = conversation.metadata
        
        return f"""## 📊 Summary Statistics

| Metric | Value |
|--------|-------|
| **Model** | {meta.model} |
| **Created** | {meta.created_at.strftime("%Y-%m-%d %H:%M:%S")} |
| **Last Updated** | {meta.updated_at.strftime("%Y-%m-%d %H:%M:%S")} |
| **Total Messages** | {stats.total_messages} |
| **User Messages** | {stats.user_messages} |
| **Assistant Messages** | {stats.assistant_messages} |
| **Total Tokens** | {stats.total_tokens:,} |
| **User Tokens** | {stats.user_tokens:,} |
| **Assistant Tokens** | {stats.assistant_tokens:,} |
| **Artifacts** | {stats.artifact_count} |
| **Tool Calls** | {stats.tool_call_count} |
| **Branches** | {stats.branch_count} |
| **Duration** | {stats.conversation_duration_minutes:.1f} minutes |

---"""
    
    def _generate_mermaid(self, conversation: Conversation) -> str:
        """Generate Mermaid diagram of conversation flow."""
        lines = ["## 🌳 Conversation Structure", "", "```mermaid", "graph TD"]
        
        # Simplified flow for first 10 messages
        messages = conversation.messages[:10]
        for i, msg in enumerate(messages):
            node_id = f"M{i}"
            role = "User" if msg.role == MessageRole.USER else "Claude"
            label = f"{role}: {msg.content[:30]}..."
            
            # Escape special characters for Mermaid
            label = label.replace('"', "'").replace("[", "(").replace("]", ")")
            
            lines.append(f'    {node_id}["{label}"]')
            
            if i > 0:
                lines.append(f"    M{i-1} --> {node_id}")
        
        if len(conversation.messages) > 10:
            lines.append(f'    M9 --> More["... {len(conversation.messages) - 10} more messages"]')
        
        lines.append("```")
        lines.append("")
        lines.append("---")
        
        return "\n".join(lines)
    
    def _generate_conversation(self, conversation: Conversation) -> str:
        """Generate full conversation transcript."""
        lines = ["## 💬 Full Conversation", ""]
        
        for i, msg in enumerate(conversation.messages, 1):
            lines.append(self._format_message(i, msg, conversation))
            lines.append("")
        
        lines.append("---")
        
        return "\n".join(lines)
    
    def _format_message(
        self,
        turn: int,
        msg: Message,
        conversation: Conversation,
    ) -> str:
        """Format a single message."""
        role_emoji = "👤" if msg.role == MessageRole.USER else "🤖"
        role_name = "User" if msg.role == MessageRole.USER else "Claude"
        
        lines = [
            f"### Turn {turn}: {role_emoji} {role_name}",
            f"*{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')} • Branch: {msg.branch_id}*",
            "",
        ]
        
        # Message content
        lines.append("> " + msg.content.replace("\n", "\n> "))
        lines.append("")
        
        # Metadata
        metadata_items = []
        if msg.tokens:
            metadata_items.append(f"Tokens: {msg.tokens:,}")
        if msg.artifacts:
            metadata_items.append(f"Artifacts: {len(msg.artifacts)}")
        if msg.tool_calls:
            metadata_items.append(f"Tools Used: {len(msg.tool_calls)}")
        
        if metadata_items:
            lines.append("**Metadata**: " + " | ".join(metadata_items))
            lines.append("")
        
        # Thinking content
        if msg.thinking_content:
            lines.append("<details>")
            lines.append("<summary><b>💭 Thinking Process</b></summary>")
            lines.append("")
            lines.append("```")
            lines.append(msg.thinking_content)
            lines.append("```")
            lines.append("</details>")
            lines.append("")
        
        # Tool calls
        if msg.tool_calls:
            lines.append("**🔧 Tools Used**:")
            for tool_call in msg.tool_calls:
                lines.append(f"- `{tool_call.get('tool_name', 'unknown')}(...)`")
            lines.append("")
        
        # Artifacts
        if msg.artifacts:
            lines.append("**🎨 Artifacts Created**:")
            for art_id in msg.artifacts:
                art = next((a for a in conversation.artifacts if a.id == art_id), None)
                if art:
                    lines.append(f"- [{art.title}](#artifact-{art_id}) ({art.type.value})")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_artifacts(self, conversation: Conversation) -> str:
        """Generate artifacts section."""
        lines = ["## 🎨 Artifacts", ""]
        
        for i, art in enumerate(conversation.artifacts, 1):
            lines.append(f"### Artifact {i}: {art.title}")
            lines.append(f"<span id=\"artifact-{art.id}\"></span>")
            lines.append("")
            lines.append(f"**Type**: {art.type.value}")
            if art.language:
                lines.append(f"**Language**: {art.language}")
            lines.append(f"**Created**: {art.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"**Version**: {art.version}")
            lines.append("")
            
            # Content
            if art.type.value == "code" or art.language:
                lang = art.language or ""
                lines.append(f"```{lang}")
                lines.append(art.content)
                lines.append("```")
            else:
                lines.append(art.content)
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_tool_analysis(self, conversation: Conversation) -> str:
        """Generate tool usage analysis."""
        lines = ["## 🔧 Tool Usage Analysis", ""]
        
        # Count tool usage
        tool_counts = {}
        for tool in conversation.tool_calls:
            name = tool.tool_name
            tool_counts[name] = tool_counts.get(name, 0) + 1
        
        # Sort by usage
        sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
        
        lines.append("| Tool | Usage Count | % of Total |")
        lines.append("|------|-------------|------------|")
        
        total = len(conversation.tool_calls)
        for tool_name, count in sorted_tools:
            percentage = (count / total) * 100 if total > 0 else 0
            lines.append(f"| `{tool_name}` | {count} | {percentage:.1f}% |")
        
        lines.append("")
        lines.append("---")
        
        return "\n".join(lines)
    
    def _generate_system_config(self, conversation: Conversation) -> str:
        """Generate system configuration section."""
        meta = conversation.metadata
        lines = ["## ⚙️ System Configuration", ""]
        
        # Custom instructions
        if meta.custom_instructions:
            lines.append("### Custom Instructions")
            lines.append("```")
            lines.append(meta.custom_instructions)
            lines.append("```")
            lines.append("")
        
        # Active skills
        if meta.active_skills:
            lines.append("### Active Skills")
            for skill in meta.active_skills:
                lines.append(f"- {skill}")
            lines.append("")
        
        # System prompt
        if conversation.system_prompt:
            lines.append("<details>")
            lines.append("<summary><b>System Prompt</b></summary>")
            lines.append("")
            lines.append("```")
            lines.append(conversation.system_prompt)
            lines.append("```")
            lines.append("</details>")
            lines.append("")
        
        lines.append("---")
        
        return "\n".join(lines)
    
    def _generate_footer(self, conversation: Conversation) -> str:
        """Generate report footer."""
        extraction_meta = conversation.extraction_metadata
        
        lines = ["## 📋 Export Information", ""]
        
        if extraction_meta:
            lines.append(f"- **Extracted At**: {extraction_meta.get('extracted_at', 'Unknown')}")
            lines.append(f"- **Extractor Version**: {extraction_meta.get('extractor_version', 'Unknown')}")
            lines.append(f"- **Extraction Method**: {extraction_meta.get('method', 'Unknown')}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Claude Conversation Extractor*")
        
        return "\n".join(lines)
