"""
Example: Basic Conversation Extraction

This example demonstrates the basic usage of the Claude Conversation Extractor
as a Python library (rather than using the CLI).
"""

import asyncio
from pathlib import Path

from claude_extractor.extractors.hybrid_extractor import HybridExtractor
from claude_extractor.exporters.json_exporter import JSONExporter
from claude_extractor.exporters.markdown_exporter import MarkdownExporter


def main():
    """Extract and export a conversation."""
    
    # Configuration
    conversation_url = "https://claude.ai/chat/YOUR_CONVERSATION_ID"
    auth_cookie = "YOUR_SESSION_COOKIE"  # Or use environment variable
    output_dir = Path("./exports")
    
    print("🚀 Starting extraction...")
    
    # Initialize extractor
    extractor = HybridExtractor(
        auth_cookie=auth_cookie,
        timeout=60,
        include_thinking=True,
        verbose=True,
    )
    
    # Extract conversation
    print(f"📥 Extracting: {conversation_url}")
    conversation = extractor.extract(conversation_url)
    
    print(f"✅ Extracted {conversation.statistics.total_messages} messages")
    print(f"   - {conversation.statistics.artifact_count} artifacts")
    print(f"   - {conversation.statistics.tool_call_count} tool calls")
    print(f"   - {conversation.statistics.branch_count} branches")
    
    # Export to JSON
    print("\n📄 Exporting to JSON...")
    json_exporter = JSONExporter(pretty=True)
    json_path = output_dir / "conversation.json"
    json_exporter.export(conversation, json_path)
    print(f"   ✓ Saved to: {json_path}")
    
    # Export to Markdown
    print("\n📝 Exporting to Markdown...")
    md_exporter = MarkdownExporter(
        include_statistics=True,
        include_mermaid=True,
        include_artifacts=True,
    )
    md_path = output_dir / "conversation.md"
    md_exporter.export(conversation, md_path)
    print(f"   ✓ Saved to: {md_path}")
    
    print("\n🎉 Export complete!")
    print(f"\nView your exports at: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
