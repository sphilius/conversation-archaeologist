#!/usr/bin/env python3
"""
Conversation Extraction CLI Tool

Extract Claude conversations and generate structured reports.

Usage:
    python scripts/extract.py https://claude.ai/chat/YOUR_CONV_ID
    python scripts/extract.py --from-file conversation.json
    python scripts/extract.py URL --output-dir ./my_exports

Examples:
    # Extract from URL (triggers manual export in Phase 1)
    python scripts/extract.py https://claude.ai/chat/abc-123-def

    # Process manually exported file
    python scripts/extract.py --from-file conversation.json
    
    # Extract with custom output directory
    python scripts/extract.py URL --output-dir ./exports
"""

import asyncio
from pathlib import Path
from typing import Optional
import json
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nano_agents.url_parser import URLParser, ConversationIdentifier
from nano_agents.api_fetcher import APIDataFetcher
from nano_agents.branch_detector import BranchDetector


class ConversationExtractor:
    """
    Main orchestrator for conversation extraction.
    
    Coordinates all nano-agents to extract and process conversations.
    """
    
    def __init__(self, output_dir: Path = Path("/mnt/user-data/outputs")) -> None:
        """
        Initialize extractor.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.url_parser = URLParser()
        self.fetcher = APIDataFetcher()
        self.branch_detector = BranchDetector()
    
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
                print("=" * 60)
                for instruction in raw_data["instructions"]:
                    print(instruction)
                print("=" * 60)
                print("\nAfter exporting, run:")
                print(f"  python scripts/extract.py --from-file conversation.json")
                return Path()  # Empty path indicates manual export needed
            
        except Exception as e:
            print(f"✗ Fetch failed: {e}")
            sys.exit(1)
        
        # This section will be reached in Phase 2 when automated fetching works
        return await self._process_conversation_data(raw_data, conv_id_obj.conv_id)
    
    async def extract_from_file(self, filepath: Path) -> Path:
        """
        Extract conversation from manually exported file.
        
        Args:
            filepath: Path to exported JSON file
            
        Returns:
            Path to processed JSON file
        """
        print(f"📂 Loading from file: {filepath}")
        
        try:
            raw_data = await self.fetcher.fetch_from_file(filepath)
            print(f"✓ Loaded {len(raw_data['messages'])} messages")
        except Exception as e:
            print(f"✗ File loading failed: {e}")
            sys.exit(1)
        
        # Extract conversation ID from data or filename
        conv_id = raw_data.get('id', filepath.stem)
        
        return await self._process_conversation_data(raw_data, conv_id)
    
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
            sys.exit(1)
        
        # Step 4: Generate output
        print(f"\n💾 Generating output...")
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
        output_path = self.output_dir / f"conv_{conv_id}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved to: {output_path}")
        
        # Display summary
        print(f"\n📊 Extraction Summary")
        print(f"=" * 60)
        print(f"Conversation ID: {conv_id}")
        print(f"Total Messages:  {metrics['total_messages']}")
        print(f"Branches:        {metrics['total_branches']}")
        print(f"Max Depth:       {metrics['max_depth']}")
        print(f"Output File:     {output_path}")
        print(f"=" * 60)
        
        # Display quality metrics
        print(f"\n📈 Quality Metrics")
        print(f"URL Parser:  {self.url_parser.get_metrics()}")
        print(f"API Fetcher: {self.fetcher.get_metrics()}")
        
        return output_path


def main() -> None:
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract Claude conversation data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from URL (triggers manual export in Phase 1)
  %(prog)s https://claude.ai/chat/abc-123-def

  # Process manually exported file
  %(prog)s --from-file conversation.json
  
  # Custom output directory
  %(prog)s URL --output-dir ./my_exports
        """
    )
    
    parser.add_argument(
        'url',
        nargs='?',
        help='Claude conversation URL'
    )
    parser.add_argument(
        '--from-file',
        type=Path,
        help='Path to manually exported JSON file'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path("/mnt/user-data/outputs"),
        help='Output directory for extracted data (default: /mnt/user-data/outputs)'
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
    
    # Create extractor
    extractor = ConversationExtractor(output_dir=args.output_dir)
    
    # Run extraction
    try:
        if args.from_file:
            result = asyncio.run(extractor.extract_from_file(args.from_file))
        else:
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
