# Conversation Archaeologist

🏺 **A nano-agent based tool for extracting, analyzing, and exporting Claude.ai conversations with all their branches, artifacts, and metadata.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

### Phase 1: MVP (Current)
- 🌳 **Complete Branch Extraction** - Captures all conversation branches and their relationships
- 📦 **Batch Export Support** - Process Claude.ai's batch export format (ALL conversations)
- 🔧 **Conversation Selection** - List and extract specific conversations from batch exports
- 📊 **Quality Metrics** - Track extraction success rates and performance
- 🎨 **Artifact Preservation** - Extracts code blocks and other artifacts
- 💾 **JSON Output** - Structured data with conversation trees

### Nano-Agent Architecture
Each agent has a single responsibility with clear I/O contracts:
- **URL Parser** - Extract conversation IDs from Claude URLs
- **Batch Parser** - Handle Claude's batch export format
- **Branch Detector** - Reconstruct conversation trees from flat message lists
- **API Fetcher** - Multi-strategy data fetcher (with fallbacks)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/sphilius/conversation-archaeologist.git
cd conversation-archaeologist

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov
```

### Verify Installation

```bash
# Run tests to verify installation
python -m pytest tests/ -v

# You should see all tests pass
```

---

## 📖 Usage

### Export Your Conversations from Claude.ai

**Important**: Claude.ai exports ALL conversations in a batch ZIP file, not individually.

1. Go to [claude.ai/settings/data](https://claude.ai/settings/data)
2. Click "Export your data"
3. You'll receive an email with a download link
4. Download and extract the ZIP file

The export contains:
- `conversations.json` - ALL your conversations (may be 100+ MB)
- `projects.json` - Project data
- `memories.json` - Memory/context data
- `users.json` - User information

### List Conversations in Batch Export

```bash
# List all conversations
python scripts/extract.py --from-file path/to/conversations.json --list

# List more conversations (default is 50)
python scripts/extract.py --from-file path/to/conversations.json --list --limit 100
```

### Extract Specific Conversation

```bash
# Extract by index (from --list output)
python scripts/extract.py --from-file path/to/conversations.json --index 0

# Extract by conversation UUID
python scripts/extract.py --from-file path/to/conversations.json --conv-id abc-123-def-456
```

### Extract from Single Conversation File

If you have a single conversation JSON file:

```bash
python scripts/extract.py --from-file path/to/single_conversation.json
```

### Get Conversation ID from URL

```bash
# This will show you the conversation ID and provide export instructions
python scripts/extract.py https://claude.ai/chat/abc-123-def-456
```

---

## 📂 Project Structure

```
conversation-archaeologist/
├── nano_agents/              # Core extraction agents
│   ├── __init__.py
│   ├── url_parser.py         # URL parsing agent
│   ├── api_fetcher.py        # Data fetching agent
│   ├── branch_detector.py    # Branch detection agent
│   └── batch_parser.py       # Batch export parser
│
├── scripts/                  # CLI tools
│   └── extract.py            # Main extraction script
│
├── tests/                    # Unit tests (97%+ coverage)
│   ├── test_url_parser.py
│   ├── test_api_fetcher.py
│   ├── test_branch_detector.py
│   └── test_batch_parser.py
│
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
├── README.md                # This file
├── SETUP.md                 # Detailed setup instructions
├── CLAUDE.md                # AI agent mission brief
└── ARCHITECTURE.md          # Technical architecture
```

---

## 🔧 Development

### Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=nano_agents --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_batch_parser.py -v
```

### Code Quality

```bash
# Format code
black nano_agents/ tests/ scripts/

# Type checking (if mypy is installed)
mypy nano_agents/

# Run individual agent
python nano_agents/url_parser.py
python nano_agents/branch_detector.py
python nano_agents/batch_parser.py
```

---

## 📊 Output Format

The extracted conversation is saved as JSON with this structure:

```json
{
  "conversation_id": "abc-123-def",
  "extracted_at": "2024-11-14T10:30:00Z",
  "metadata": {
    "title": "Conversation Title",
    "created_at": "2024-11-10T14:20:00Z",
    "updated_at": "2024-11-10T15:45:00Z"
  },
  "tree_structure": {
    "root_id": "msg_1",
    "branches": {
      "main": ["msg_1", "msg_2", "msg_3"],
      "branch_1": ["msg_1", "msg_2", "msg_4"]
    },
    "active_branch": "main"
  },
  "messages": [
    {
      "id": "msg_1",
      "parent_id": null,
      "role": "user",
      "content": "Hello, Claude!",
      "timestamp": "2024-11-10T14:20:00Z",
      "branch_id": "main",
      "is_active": true,
      "artifacts": [],
      "tool_calls": []
    }
  ],
  "metrics": {
    "total_messages": 24,
    "total_branches": 2,
    "max_depth": 12,
    "branch_points": 1
  }
}
```

---

## 🎯 Phase 1 Success Criteria

- [x] Extract conversations from batch exports
- [x] Detect branches correctly
- [x] Generate valid JSON output with all messages
- [x] Unit test coverage ≥80% (achieved 97%+)
- [x] CLI runs without errors
- [x] Documentation complete

---

## 🗺️ Roadmap

### Phase 2: Production (Planned)
- Quality tracker with metrics persistence
- Markdown export with Mermaid diagrams
- Batch processing with progress bars
- Enhanced error recovery

### Phase 3: Intelligence (Planned)
- Pattern analyzer
- Topic extraction
- Insight generation
- Decision point mapping

### Phase 4: Integration (Planned)
- PCoS (Personal Chief of Staff) integration
- Knowledge graph builder
- Auto-tagging system
- Cross-project insights

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Built for use with [Claude](https://claude.ai) by Anthropic
- Nano-agent architecture for clean, testable code
- Community feedback and contributions

---

## 📞 Support

For detailed setup instructions, see [SETUP.md](SETUP.md)

For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md) (if available)

For issues or questions, create a GitHub issue.

---

**Made with 🏺 for excavating conversation history**
