# Quick Start Guide

Get up and running with Conversation Archaeologist in 5 minutes.

## Prerequisites

- Python 3.10 or higher
- Git
- Claude.ai account with conversations to extract

## Installation (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/boss/conversation-archaeologist
cd conversation-archaeologist
```

### 2. Create Virtual Environment
```bash
# Create venv
python -m venv .venv

# Activate (Unix/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example config
cp config/example.env .env

# Edit .env with your settings (optional for Phase 1)
nano .env  # or use your preferred editor
```

## First Extraction (2 minutes)

### Option A: From URL (Phase 1 - Manual Export)

```bash
python scripts/extract.py https://claude.ai/chat/YOUR_CONVERSATION_ID
```

This will show you instructions for manually exporting the conversation from Claude.ai.

After exporting, process the file:

```bash
python scripts/extract.py --from-file path/to/exported_conversation.json
```

### Option B: From File (If You Already Have Export)

```bash
python scripts/extract.py --from-file conversation.json
```

## What You Get

After extraction, you'll find:
```
/mnt/user-data/outputs/
└── conv_YOUR_CONVERSATION_ID.json
```

The JSON contains:
- ✅ All messages with metadata
- ✅ Complete conversation tree structure
- ✅ Branch information (if any)
- ✅ Artifact references
- ✅ Tool usage data
- ✅ Quality metrics

## Example Output

```json
{
  "conversation_id": "abc-123-def",
  "extracted_at": "2024-11-14T15:30:00Z",
  "tree_structure": {
    "root_id": "msg_1",
    "branches": {
      "main": ["msg_1", "msg_2", "msg_3"],
      "branch_1": ["msg_1", "msg_4"]
    },
    "active_branch": "main"
  },
  "messages": [
    {
      "id": "msg_1",
      "role": "user",
      "content": "Hello, Claude!",
      "timestamp": "2024-11-14T10:00:00Z",
      "branch_id": "main",
      "is_active": true
    }
  ],
  "metrics": {
    "total_messages": 3,
    "total_branches": 2,
    "max_depth": 3
  }
}
```

## Testing Your Setup

Run the test suite to verify everything works:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=nano_agents

# Test specific agent
pytest tests/test_url_parser.py -v
```

Expected output:
```
tests/test_url_parser.py::TestURLParser::test_parse_standard_conversation_url PASSED
tests/test_url_parser.py::TestURLParser::test_parse_project_conversation_url PASSED
...
======================== X passed in Y.YYs ========================
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'nano_agents'"
**Solution**: Make sure you're in the project directory and virtual environment is activated.

```bash
cd conversation-archaeologist
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### Issue: "Invalid URL format"
**Solution**: Ensure URL includes the full conversation ID (UUID format):
```
✅ Good: https://claude.ai/chat/abc123de-f456-7890-abcd-ef1234567890
✗ Bad:  claude.ai/chat/abc-123
```

### Issue: "File not found"
**Solution**: Check the path to your exported JSON file:
```bash
# Use absolute path
python scripts/extract.py --from-file /full/path/to/conversation.json

# Or relative path from project root
python scripts/extract.py --from-file ./exports/conversation.json
```

## Next Steps

### Phase 1 (Current)
- ✅ Extract conversations manually
- ✅ Process JSON exports
- ✅ View conversation trees
- ✅ Track quality metrics

### Phase 2 (Coming Soon)
- 🚧 Automated web scraping
- 🚧 Batch processing (extract 100+ conversations)
- 🚧 Markdown report generation
- 🚧 Enhanced error recovery

### Phase 3 (Planned)
- 📋 Pattern analysis
- 📋 Topic extraction
- 📋 Insight generation
- 📋 Prompting strategy recommendations

### Phase 4 (Future)
- 🎯 PCoS integration
- 🎯 Knowledge graph visualization
- 🎯 Cross-project linking
- 🎯 Real-time extraction

## Getting Help

### Documentation
- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical details
- [CLAUDE.md](CLAUDE.md) - Full development guide

### Troubleshooting
```bash
# Enable verbose logging
python scripts/extract.py URL --verbose

# View logs
tail -f ~/.conversation_archaeologist/logs/app.log

# Check metrics
python scripts/show_metrics.py
```

### Support
- GitHub Issues: Report bugs or request features
- GitHub Discussions: Ask questions or share ideas
- Documentation: Check docs/ folder

## Tips & Tricks

### Batch Processing (Manual)
```bash
# Create a file with URLs (one per line)
echo "https://claude.ai/chat/conv-1" > urls.txt
echo "https://claude.ai/chat/conv-2" >> urls.txt

# Process each (manual export for each in Phase 1)
while read url; do
  python scripts/extract.py "$url"
done < urls.txt
```

### Custom Output Directory
```bash
python scripts/extract.py URL --output-dir ./my_exports
```

### Viewing Metrics
```bash
# Show all quality metrics
python scripts/show_metrics.py

# Metrics location
cat ~/.conversation_archaeologist/metrics.json
```

### Organizing Exports
```bash
# Create project-specific directories
mkdir -p exports/gator-belt
python scripts/extract.py URL --output-dir exports/gator-belt
```

## Development Workflow

### Making Changes
```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes, write tests
pytest tests/ -v

# Run linters
ruff check .
black .
mypy nano_agents/

# Commit and push
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

### Running in Development Mode
```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run extraction with verbose output
python scripts/extract.py URL --verbose
```

## Performance Tips

### For Large Conversations (1000+ messages)
- Expect ~1-2 seconds for tree building
- JSON files may be large (1-5 MB)
- Consider compressing old exports

### For Batch Processing
- Process during off-peak hours
- Use `MAX_CONCURRENT_EXTRACTIONS=3` for slower connections
- Monitor metrics to track success rates

## Success Checklist

After setup, you should be able to:
- [x] Activate virtual environment
- [x] Run `python scripts/extract.py --help`
- [x] Parse a Claude conversation URL
- [x] Process an exported JSON file
- [x] View extracted data in outputs directory
- [x] Run test suite successfully
- [x] View quality metrics

If all checkboxes pass, you're ready to extract! 🎉

---

**Estimated Total Setup Time**: 5-7 minutes  
**Estimated First Extraction**: 2-3 minutes  
**Next Steps**: Try extracting one of your conversations!
