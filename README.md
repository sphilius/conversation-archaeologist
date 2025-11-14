# Claude Conversation Extractor

🔍 **A powerful CLI tool for extracting, analyzing, and exporting Claude.ai conversations with all their branches, artifacts, and metadata.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

### Core Capabilities
- 🌳 **Complete Branch Extraction** - Captures all conversation branches and their relationships
- 🎨 **Artifact Preservation** - Extracts all artifacts (code, markdown, React, HTML, etc.) with version history
- 🔧 **Tool Usage Tracking** - Records all tool calls and their results
- 💭 **Thinking Content** - Preserves Claude's internal reasoning when available
- 📊 **Comprehensive Statistics** - Token counts, message metrics, and usage analysis
- 🔐 **Secure Authentication** - Cookie-based auth with optional keyring storage

### Export Formats
- 📄 **LLM-Optimized JSON** - Flat structure perfect for RAG systems and AI processing
- 📝 **Human-Friendly Markdown** - Beautiful reports with conversation flow, statistics, and visualizations
- 📦 **Artifact Bundles** - Separate artifact files organized by type
- 🗺️ **Mermaid Diagrams** - Visual conversation flow and branch structures

### Advanced Features
- 🔄 **Multiple Extraction Strategies** - API-first with browser automation fallback
- 🎯 **Smart Filtering** - Extract specific date ranges, message types, or branches
- 🔍 **Conversation Analysis** - Topic detection, complexity scoring, decision point identification
- 🚀 **Batch Processing** - Extract multiple conversations efficiently
- 💾 **Resume Capability** - Continue interrupted extractions
- 🧩 **Extensible Architecture** - Plugin system for custom processors and exporters

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-conversation-extractor.git
cd claude-conversation-extractor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Basic Usage

```bash
# Extract a conversation (interactive auth)
claude-extract https://claude.ai/chat/your-conversation-id

# With explicit authentication
claude-extract https://claude.ai/chat/your-conversation-id --auth-cookie "your_cookie"

# Specify output directory
claude-extract https://claude.ai/chat/your-conversation-id --output-dir ./my-exports

# Extract multiple conversations
claude-extract --batch conversations.txt

# Export only specific formats
claude-extract URL --format json
claude-extract URL --format markdown
claude-extract URL --format both  # default
```

---

## 📖 Detailed Usage

### Authentication

The tool supports multiple authentication methods:

```bash
# Method 1: Interactive browser authentication
claude-extract URL --auth-method browser

# Method 2: Cookie string
claude-extract URL --auth-cookie "sessionKey=your_session_key"

# Method 3: Stored credentials (uses keyring)
claude-extract URL --auth-method stored --save-credentials

# Method 4: Environment variable
export CLAUDE_SESSION_KEY="your_session_key"
claude-extract URL
```

### Advanced Options

```bash
# Full command with all options
claude-extract URL \
  --output-dir ./exports \
  --format both \
  --include-artifacts \
  --include-thinking \
  --extract-branches all \
  --date-range "2024-01-01:2024-12-31" \
  --max-messages 100 \
  --timeout 60 \
  --verbose
```

### Configuration File

Create `~/.claude-extractor/config.yaml`:

```yaml
# Default settings
output_dir: ~/claude-exports
format: both
include_artifacts: true
include_thinking: true
extract_branches: all

# Authentication
auth_method: stored
save_credentials: true

# Performance
timeout: 60
max_concurrent: 3
retry_attempts: 3

# Output customization
markdown:
  include_statistics: true
  include_mermaid: true
  include_tool_analysis: true
  
json:
  pretty_print: true
  include_metadata: true
```

---

## 📂 Project Structure

```
claude-conversation-extractor/
├── README.md
├── LICENSE
├── setup.py
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── pyproject.toml
│
├── src/
│   └── claude_extractor/
│       ├── __init__.py
│       ├── __main__.py           # CLI entry point
│       ├── cli.py                # Command-line interface
│       ├── config.py             # Configuration management
│       │
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── authenticator.py  # Authentication handlers
│       │   ├── cookie_manager.py # Cookie extraction/storage
│       │   └── session.py        # Session management
│       │
│       ├── extractors/
│       │   ├── __init__.py
│       │   ├── base.py           # Base extractor interface
│       │   ├── api_extractor.py  # API-based extraction
│       │   ├── browser_extractor.py  # Playwright-based
│       │   └── hybrid_extractor.py   # Combined strategy
│       │
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── message_parser.py     # Message parsing
│       │   ├── artifact_parser.py    # Artifact extraction
│       │   ├── branch_parser.py      # Branch detection
│       │   └── metadata_parser.py    # Metadata extraction
│       │
│       ├── analyzers/
│       │   ├── __init__.py
│       │   ├── conversation_analyzer.py  # Analysis engine
│       │   ├── topic_detector.py         # Topic extraction
│       │   ├── complexity_scorer.py      # Complexity metrics
│       │   └── decision_mapper.py        # Decision points
│       │
│       ├── exporters/
│       │   ├── __init__.py
│       │   ├── base.py               # Base exporter
│       │   ├── json_exporter.py      # JSON export
│       │   ├── markdown_exporter.py  # Markdown export
│       │   └── artifact_bundler.py   # Artifact packaging
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── conversation.py   # Data models
│       │   ├── message.py
│       │   ├── artifact.py
│       │   └── branch.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── logger.py         # Logging utilities
│           ├── validators.py     # Input validation
│           └── helpers.py        # Helper functions
│
├── tests/
│   ├── __init__.py
│   ├── test_extractors.py
│   ├── test_parsers.py
│   ├── test_exporters.py
│   ├── fixtures/
│   └── integration/
│
├── docs/
│   ├── architecture.md
│   ├── api_reference.md
│   ├── contributing.md
│   └── examples/
│
└── examples/
    ├── basic_extraction.py
    ├── batch_processing.py
    ├── custom_exporter.py
    └── analysis_pipeline.py
```

---

## 🔧 Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=claude_extractor tests/

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
pylint src/
flake8 src/
```

---

## 📊 Output Examples

### JSON Structure (LLM-Optimized)

```json
{
  "format_version": "1.0.0",
  "extracted_at": "2024-11-12T10:30:00Z",
  "extractor_version": "0.1.0",
  "conversation": {
    "id": "abc123",
    "url": "https://claude.ai/chat/abc123",
    "title": "Python Development Help",
    "created_at": "2024-11-10T14:20:00Z",
    "updated_at": "2024-11-10T15:45:00Z",
    "model": "claude-sonnet-4-20250514",
    "messages": [
      {
        "id": "msg_001",
        "role": "user",
        "content": "Help me build a Python CLI tool",
        "timestamp": "2024-11-10T14:20:00Z",
        "parent_id": null,
        "branch_id": "main",
        "tokens": 156
      }
    ],
    "artifacts": [],
    "statistics": {
      "total_messages": 24,
      "user_messages": 12,
      "assistant_messages": 12,
      "total_tokens": 45678
    }
  }
}
```

### Markdown Report Preview

See [example_export.md](docs/examples/example_export.md) for a full sample report.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/contributing.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built for use with [Claude](https://claude.ai) by Anthropic
- Inspired by the need for better conversation archival and analysis
- Community contributions and feedback

---

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/claude-conversation-extractor/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/claude-conversation-extractor/discussions)
- 📧 **Contact**: your.email@example.com

---

## 🗺️ Roadmap

- [ ] Support for Claude API conversations
- [ ] Real-time conversation monitoring
- [ ] Export to Obsidian, Notion, and other PKM tools
- [ ] Conversation comparison and diff tools
- [ ] Web UI for extraction management
- [ ] Docker containerization
- [ ] Cloud storage integration (S3, GCS, Azure)
- [ ] Advanced search and filtering
- [ ] Conversation analytics dashboard
- [ ] Plugin marketplace

---

**Made with ❤️ for the Claude community**
