"""
Command-line interface for Claude Conversation Extractor.

Provides a rich CLI experience with progress bars, formatted output,
and comprehensive options for extraction and export.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from claude_extractor import __version__
from claude_extractor.config import Config, load_config
from claude_extractor.extractors.hybrid_extractor import HybridExtractor
from claude_extractor.exporters.json_exporter import JSONExporter
from claude_extractor.exporters.markdown_exporter import MarkdownExporter
from claude_extractor.utils.logger import setup_logger

console = Console()
logger = setup_logger()


@click.group()
@click.version_option(version=__version__)
@click.option("--config", type=click.Path(exists=True), help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool) -> None:
    """
    Claude Conversation Extractor - Extract and analyze Claude.ai conversations.
    
    Extract complete conversations including all branches, artifacts, tool calls,
    and metadata. Export to LLM-optimized JSON and human-friendly Markdown.
    """
    ctx.ensure_object(dict)
    
    # Load configuration
    if config:
        ctx.obj["config"] = load_config(Path(config))
    else:
        ctx.obj["config"] = Config()
    
    ctx.obj["verbose"] = verbose
    
    if verbose:
        logger.setLevel("DEBUG")
        console.print("[dim]Verbose mode enabled[/dim]")


@cli.command()
@click.argument("url")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    help="Output directory for exports"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown", "both"], case_sensitive=False),
    default="both",
    help="Export format"
)
@click.option(
    "--auth-cookie",
    envvar="CLAUDE_SESSION_KEY",
    help="Authentication cookie (or set CLAUDE_SESSION_KEY env var)"
)
@click.option(
    "--include-artifacts/--no-artifacts",
    default=True,
    help="Include artifacts in export"
)
@click.option(
    "--include-thinking/--no-thinking",
    default=True,
    help="Include Claude's thinking content"
)
@click.option(
    "--extract-branches",
    type=click.Choice(["all", "active", "none"], case_sensitive=False),
    default="all",
    help="Which branches to extract"
)
@click.option(
    "--timeout",
    type=int,
    default=60,
    help="Request timeout in seconds"
)
@click.pass_context
def extract(
    ctx: click.Context,
    url: str,
    output_dir: Optional[str],
    format: str,
    auth_cookie: Optional[str],
    include_artifacts: bool,
    include_thinking: bool,
    extract_branches: str,
    timeout: int,
) -> None:
    """
    Extract a conversation from Claude.ai.
    
    URL should be in the format: https://claude.ai/chat/CONVERSATION_ID
    
    Example:
        claude-extract https://claude.ai/chat/abc123 -o ./exports
    """
    config: Config = ctx.obj["config"]
    verbose: bool = ctx.obj["verbose"]
    
    # Validate URL
    if not url.startswith("https://claude.ai/chat/"):
        console.print("[red]Error: Invalid Claude conversation URL[/red]")
        console.print("Expected format: https://claude.ai/chat/CONVERSATION_ID")
        sys.exit(1)
    
    # Set output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = config.output_dir
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Check authentication
    if not auth_cookie:
        console.print("[yellow]Warning: No authentication provided[/yellow]")
        console.print("Some features may not work without authentication.")
        console.print("Set CLAUDE_SESSION_KEY environment variable or use --auth-cookie")
        
        if not click.confirm("Continue anyway?"):
            sys.exit(0)
    
    # Extract conversation
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Extracting conversation...", total=None)
            
            extractor = HybridExtractor(
                auth_cookie=auth_cookie,
                timeout=timeout,
                include_thinking=include_thinking,
                verbose=verbose,
            )
            
            conversation = extractor.extract(url)
            
            progress.update(task, description="✓ Conversation extracted")
        
        # Display summary
        _display_conversation_summary(conversation)
        
        # Export
        _export_conversation(
            conversation,
            output_path,
            format,
            include_artifacts,
            verbose,
        )
        
        console.print(f"\n[green]✓ Export complete![/green] Files saved to: {output_path}")
        
    except Exception as e:
        console.print(f"[red]✗ Error during extraction: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("batch_file", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    required=True,
    help="Output directory for exports"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown", "both"], case_sensitive=False),
    default="both",
    help="Export format"
)
@click.option(
    "--auth-cookie",
    envvar="CLAUDE_SESSION_KEY",
    help="Authentication cookie"
)
@click.option(
    "--max-concurrent",
    type=int,
    default=3,
    help="Maximum concurrent extractions"
)
@click.pass_context
def batch(
    ctx: click.Context,
    batch_file: str,
    output_dir: str,
    format: str,
    auth_cookie: Optional[str],
    max_concurrent: int,
) -> None:
    """
    Extract multiple conversations from a file.
    
    The batch file should contain one conversation URL per line.
    
    Example batch file:
        https://claude.ai/chat/abc123
        https://claude.ai/chat/def456
        https://claude.ai/chat/ghi789
    """
    # Read URLs from file
    urls = []
    with open(batch_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    
    if not urls:
        console.print("[red]No valid URLs found in batch file[/red]")
        sys.exit(1)
    
    console.print(f"Found {len(urls)} conversations to extract")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each URL
    successful = 0
    failed = 0
    
    with Progress(console=console) as progress:
        task = progress.add_task("Processing conversations...", total=len(urls))
        
        for url in urls:
            try:
                # Extract conversation ID for folder name
                conv_id = url.split("/")[-1]
                conv_output = output_path / conv_id
                conv_output.mkdir(exist_ok=True)
                
                # Extract
                extractor = HybridExtractor(auth_cookie=auth_cookie)
                conversation = extractor.extract(url)
                
                # Export
                _export_conversation(conversation, conv_output, format, True, False)
                
                successful += 1
                progress.console.print(f"[green]✓[/green] {conv_id}")
                
            except Exception as e:
                failed += 1
                progress.console.print(f"[red]✗[/red] {url}: {e}")
            
            progress.advance(task)
    
    console.print(f"\n[bold]Batch extraction complete![/bold]")
    console.print(f"Successful: {successful}")
    console.print(f"Failed: {failed}")


@cli.command()
@click.argument("conversation_file", type=click.Path(exists=True))
@click.pass_context
def analyze(ctx: click.Context, conversation_file: str) -> None:
    """
    Analyze an extracted conversation JSON file.
    
    Displays detailed statistics, topic analysis, and insights.
    """
    import json
    from claude_extractor.analyzers.conversation_analyzer import ConversationAnalyzer
    
    # Load conversation
    with open(conversation_file, "r") as f:
        data = json.load(f)
    
    # Analyze
    analyzer = ConversationAnalyzer()
    analysis = analyzer.analyze(data)
    
    # Display results
    _display_analysis(analysis)


def _display_conversation_summary(conversation) -> None:
    """Display a summary of the extracted conversation."""
    table = Table(title="Conversation Summary", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    stats = conversation.statistics
    
    table.add_row("Title", conversation.metadata.title)
    table.add_row("Messages", str(stats.total_messages))
    table.add_row("User Messages", str(stats.user_messages))
    table.add_row("Assistant Messages", str(stats.assistant_messages))
    table.add_row("Total Tokens", f"{stats.total_tokens:,}")
    table.add_row("Artifacts", str(stats.artifact_count))
    table.add_row("Tool Calls", str(stats.tool_call_count))
    table.add_row("Branches", str(stats.branch_count))
    
    console.print()
    console.print(table)
    console.print()


def _export_conversation(
    conversation,
    output_path: Path,
    format: str,
    include_artifacts: bool,
    verbose: bool,
) -> None:
    """Export conversation to specified format(s)."""
    
    if format in ["json", "both"]:
        json_exporter = JSONExporter(pretty=True)
        json_path = output_path / "conversation.json"
        json_exporter.export(conversation, json_path)
        if verbose:
            console.print(f"[dim]JSON exported to: {json_path}[/dim]")
    
    if format in ["markdown", "both"]:
        md_exporter = MarkdownExporter(
            include_statistics=True,
            include_mermaid=True,
            include_artifacts=include_artifacts,
        )
        md_path = output_path / "conversation.md"
        md_exporter.export(conversation, md_path)
        if verbose:
            console.print(f"[dim]Markdown exported to: {md_path}[/dim]")


def _display_analysis(analysis: dict) -> None:
    """Display conversation analysis results."""
    console.print("\n[bold]Conversation Analysis[/bold]\n")
    
    # Topics
    if "topics" in analysis:
        console.print("[cyan]Topics Detected:[/cyan]")
        for topic in analysis["topics"]:
            console.print(f"  • {topic}")
        console.print()
    
    # Complexity
    if "complexity_score" in analysis:
        console.print(f"[cyan]Complexity Score:[/cyan] {analysis['complexity_score']}/10")
        console.print()
    
    # Decision Points
    if "decision_points" in analysis:
        console.print("[cyan]Decision Points:[/cyan]")
        for dp in analysis["decision_points"]:
            console.print(f"  • Turn {dp['turn']}: {dp['description']}")
        console.print()


def main() -> None:
    """Main entry point for CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
