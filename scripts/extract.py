#!/usr/bin/env python3
"""
Conversation Extraction CLI Tool

Extract Claude conversations from batch exports or individual files.

Usage:
    python scripts/extract.py https://claude.ai/chat/YOUR_CONV_ID
    python scripts/extract.py --from-file conversations.json --list
    python scripts/extract.py --from-file conversations.json --index 0
    python scripts/extract.py --from-file conversations.json --conv-id UUID

Examples:
    # Extract from URL (triggers manual export in Phase 1)
    python scripts/extract.py https://claude.ai/chat/abc-123-def

    # List all conversations in batch export
    python scripts/extract.py --from-file conversations.json --list

    # Extract specific conversation by index
    python scripts/extract.py --from-file conversations.json --index 5

    # Extract specific conversation by UUID
    python scripts/extract.py --from-file conversations.json --conv-id abc-123-def
"""

import asyncio
from pathlib import Path
from typing import Optional
import json
import sys
from datetime import datetime
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nano_agents.url_parser import URLParser, ConversationIdentifier
from nano_agents.api_fetcher import APIDataFetcher
from nano_agents.branch_detector import BranchDetector
from nano_agents.batch_parser import BatchExportParser


class ConversationExtractor:
    """
    Main orchestrator for conversation extraction.

    Coordinates all nano-agents to extract and process conversations.
    Handles both single conversation files and Claude batch exports.
    """

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        """
        Initialize extractor.

        Args:
            output_dir: Directory for output files
        """
        if output_dir is None:
            # Use current directory on Windows, /mnt/user-data/outputs on Linux
            if os.name == 'nt':  # Windows
                output_dir = Path.cwd() / "outputs"
            else:
                output_dir = Path("/mnt/user-data/outputs")

        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.url_parser = URLParser()
        self.fetcher = APIDataFetcher()
        self.branch_detector = BranchDetector()
        self.batch_parser = BatchExportParser()

    async def extract_from_url(self, url: str) -> Path:
        """
        Extract conversation from URL.

        Args:
            url: Claude conversation URL

        Returns:
            Path to exported JSON file
        """
        print(f"🔍 Parsing URL: {url}")

        # Step 1: Parse URL
        try:
            conv_id_obj = self.url_parser.parse(url)
            print(f"✓ Conversation ID: {conv_id_obj.conv_id}")
            if conv_id_obj.is_project_conv:
                print(f"  Project: {conv_id_obj.project_id}")
        except ValueError as e:
            print(f"✗ URL parsing failed: {e}")
            sys.exit(1)

        # Step 2: Fetch conversation data
        print(f"\n📥 Fetching conversation data...")
        try:
            raw_data = await self.fetcher.fetch(conv_id_obj.conv_id)

            # Check if manual export needed
            if raw_data.get("status") == "manual_export_required":
                print("\n📋 Manual Export Required")
                print("=" * 80)
                print("\nClaude.ai exports ALL conversations in a batch, not individually.")
                print("\nTo export your conversations:")
                print("  1. Go to: https://claude.ai/settings/data")
                print("  2. Click 'Export your data'")
                print("  3. You'll receive an email with a download link")
                print("  4. Download and extract the ZIP file")
                print("\nThe export contains:")
                print("  - conversations.json (ALL your conversations)")
                print("  - projects.json")
                print("  - memories.json")
                print("  - users.json")
                print("\n" + "=" * 80)
                print("\nAfter exporting, list your conversations:")
                print(f"  python scripts/extract.py --from-file conversations.json --list")
                print("\nThen extract a specific one:")
                print(f"  python scripts/extract.py --from-file conversations.json --index 0")
                print("=" * 80)
                return Path()  # Empty path indicates manual export needed

        except Exception as e:
            print(f"✗ Fetch failed: {e}")
            sys.exit(1)

        # This section will be reached in Phase 2 when automated fetching works
        return await self._process_conversation_data(raw_data, conv_id_obj.conv_id)

    async def list_batch_conversations(self, filepath: Path, limit: int = 50) -> None:
        """
        List all conversations in a batch export.

        Args:
            filepath: Path to conversations.json
            limit: Maximum number to display
        """
        print(f"📂 Loading batch export: {filepath}\n")

        try:
            conversations = self.batch_parser.parse_batch_export(filepath)
            listing = self.batch_parser.list_conversations(conversations, limit=limit)
            print(listing)
        except Exception as e:
            print(f"✗ Failed to list conversations: {e}")
            sys.exit(1)

    async def extract_from_batch(
        self,
        filepath: Path,
        conv_id: Optional[str] = None,
        index: Optional[int] = None
    ) -> Path:
        """
        Extract a specific conversation from batch export.

        Args:
            filepath: Path to conversations.json
            conv_id: UUID of conversation to extract (optional)
            index: Index of conversation in batch (optional)

        Returns:
            Path to extracted conversation file
        """
        print(f"📂 Loading batch export: {filepath}")

        # Check if path is a directory
        if filepath.is_dir():
            print(f"\n✗ Error: Path is a directory, not a file")
            print(f"   Path: {filepath}")
            print(f"\n💡 You provided a folder path. Please specify the JSON file:")
            print(f"   {filepath / 'conversations.json'}")
            print(f"\n   Correct command:")
            print(f"   python scripts/extract.py --from-file \"{filepath / 'conversations.json'}\" --list")
            sys.exit(1)

        try:
            # Parse batch export
            conversations = self.batch_parser.parse_batch_export(filepath)
            print(f"✓ Loaded batch export with {len(conversations)} conversations\n")

            # Select conversation
            selected_conv = self.batch_parser.select_conversation(
                conversations,
                conv_id=conv_id,
                index=index
            )

            # Normalize conversation format
            normalized_conv = self.batch_parser.normalize_conversation(selected_conv)

            # Extract conversation metadata
            conv_uuid = normalized_conv['id']
            conv_name = normalized_conv.get('metadata', {}).get('title', 'Untitled')

            print(f"✓ Selected conversation:")
            print(f"  UUID: {conv_uuid}")
            print(f"  Name: {conv_name}")
            print(f"  Messages: {len(normalized_conv['messages'])}")

            # Process conversation
            return await self._process_conversation_data(normalized_conv, conv_uuid)

        except ValueError as e:
            print(f"\n✗ {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Failed to extract conversation: {e}")
            if "--verbose" in sys.argv:
                import traceback
                traceback.print_exc()
            sys.exit(1)

    async def extract_from_file(self, filepath: Path) -> Path:
        """
        Extract conversation from file (handles both single and batch formats).

        Args:
            filepath: Path to JSON file

        Returns:
            Path to processed JSON file
        """
        print(f"📂 Loading from file: {filepath}")

        # Check if path is a directory
        if filepath.is_dir():
            print(f"\n✗ Error: Path is a directory, not a file")
            print(f"   Path: {filepath}")
            print(f"\n💡 You provided a folder path. Please specify the JSON file:")
            print(f"   {filepath / 'conversations.json'}")
            print(f"\n   Correct command:")
            print(f"   python scripts/extract.py --from-file \"{filepath / 'conversations.json'}\" --list")
            sys.exit(1)

        try:
            # Try to detect if it's a batch export or single conversation
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check format
            if isinstance(data, list):
                # Batch export format
                print(f"✓ Detected batch export format ({len(data)} conversations)")
                print(f"\n💡 This file contains multiple conversations.")
                print(f"   Use --list to see all conversations")
                print(f"   Use --index N to extract a specific conversation")
                print(f"\nExample:")
                print(f"  python scripts/extract.py --from-file \"{filepath}\" --list")
                sys.exit(0)
            elif isinstance(data, dict) and 'messages' in data:
                # Single conversation format
                raw_data = data
                conv_id = raw_data.get('id', filepath.stem)
                print(f"✓ Loaded single conversation ({len(raw_data['messages'])} messages)")
                return await self._process_conversation_data(raw_data, conv_id)
            else:
                # Unknown format
                print(f"\n✗ Unknown file format")
                print(f"   Expected: conversations.json (batch export) or single conversation JSON")
                print(f"   Found fields: {list(data.keys())[:10]}")
                sys.exit(1)

        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ File loading failed: {e}")
            sys.exit(1)

    async def _process_conversation_data(
        self,
        raw_data: dict,
        conv_id: str
    ) -> Path:
        """
        Process conversation data through all agents.

        Args:
            raw_data: Raw conversation data
            conv_id: Conversation ID

        Returns:
            Path to final output file
        """
        # Step 3: Build conversation tree
        print(f"\n🌳 Building conversation tree...")
        try:
            tree = self.branch_detector.build_tree(raw_data['messages'])
            metrics = self.branch_detector.get_metrics(tree)

            print(f"✓ Tree built successfully")
            print(f"  Total messages: {metrics['total_messages']}")
            print(f"  Branches: {metrics['total_branches']}")
            if metrics['branch_points'] > 0:
                print(f"  Branch points: {metrics['branch_points']}")
            print(f"  Active branch: {tree.active_branch}")
        except Exception as e:
            print(f"✗ Tree building failed: {e}")
            if "--verbose" in sys.argv:
                import traceback
                traceback.print_exc()
            sys.exit(1)

        # Step 4: Generate output
        print(f"\n💾 Generating output...")

        # Sanitize conversation ID for filename
        safe_conv_id = conv_id.replace('/', '_').replace('\\', '_')[:50]

        output_data = {
            "conversation_id": conv_id,
            "extracted_at": datetime.now().isoformat(),
            "metadata": raw_data.get('metadata', {}),
            "tree_structure": {
                "root_id": tree.root_id,
                "branches": {
                    bid: [nodes for nodes in message_ids]
                    for bid, message_ids in tree.branches.items()
                },
                "active_branch": tree.active_branch
            },
            "messages": [
                {
                    "id": node.id,
                    "parent_id": node.parent_id,
                    "role": node.role,
                    "content": node.content,
                    "timestamp": node.timestamp,
                    "branch_id": node.branch_id,
                    "is_active": node.is_active,
                    "artifacts": node.artifacts,
                    "tool_calls": node.tool_calls
                }
                for node in tree.nodes.values()
            ],
            "metrics": metrics
        }

        # Save to file
        output_path = self.output_dir / f"conv_{safe_conv_id}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved to: {output_path}")

        # Display summary
        print(f"\n📊 Extraction Summary")
        print(f"=" * 80)
        print(f"Conversation ID: {conv_id}")
        print(f"Total Messages:  {metrics['total_messages']}")
        print(f"Branches:        {metrics['total_branches']}")
        print(f"Max Depth:       {metrics['max_depth']}")
        print(f"Output File:     {output_path}")
        print(f"=" * 80)

        return output_path


def main() -> None:
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract Claude conversation data from batch exports or individual files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all conversations in batch export
  %(prog)s --from-file conversations.json --list

  # Extract conversation by index
  %(prog)s --from-file conversations.json --index 0

  # Extract conversation by UUID
  %(prog)s --from-file conversations.json --conv-id abc-123-def-456

  # Extract from single conversation file
  %(prog)s --from-file single_conversation.json

  # Extract from URL (triggers batch export instructions)
  %(prog)s https://claude.ai/chat/abc-123-def

Note: Claude.ai exports ALL conversations in one batch file, not individually.
      Use --list to see what's in your export, then use --index or --conv-id to extract.
        """
    )

    parser.add_argument(
        'url',
        nargs='?',
        help='Claude conversation URL (triggers export instructions)'
    )
    parser.add_argument(
        '--from-file',
        type=Path,
        help='Path to conversations.json (batch export) or single conversation JSON'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all conversations in batch export'
    )
    parser.add_argument(
        '--index',
        type=int,
        help='Extract conversation at this index (0-based)'
    )
    parser.add_argument(
        '--conv-id',
        type=str,
        help='Extract conversation with this UUID'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum conversations to list (default: 50)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Output directory for extracted data'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.url and not args.from_file:
        parser.error("Either URL or --from-file must be provided")

    if args.url and args.from_file:
        parser.error("Cannot specify both URL and --from-file")

    if args.list and (args.index is not None or args.conv_id):
        parser.error("Cannot use --list with --index or --conv-id")

    # Create extractor
    extractor = ConversationExtractor(output_dir=args.output_dir)

    # Run extraction
    try:
        if args.from_file:
            if args.list:
                # List conversations in batch
                asyncio.run(extractor.list_batch_conversations(
                    args.from_file,
                    limit=args.limit
                ))
            elif args.index is not None or args.conv_id:
                # Extract specific conversation from batch
                result = asyncio.run(extractor.extract_from_batch(
                    args.from_file,
                    conv_id=args.conv_id,
                    index=args.index
                ))
                if result and result.exists():
                    print(f"\n✨ Extraction complete! View your data at:")
                    print(f"   {result}")
            else:
                # Try to auto-detect format
                result = asyncio.run(extractor.extract_from_file(args.from_file))
                if result and result.exists():
                    print(f"\n✨ Extraction complete! View your data at:")
                    print(f"   {result}")
        else:
            # Extract from URL (triggers export instructions)
            result = asyncio.run(extractor.extract_from_url(args.url))
            if result and result.exists():
                print(f"\n✨ Extraction complete! View your data at:")
                print(f"   {result}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Extraction cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
