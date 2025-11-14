# Quick Start Guide

Get up and running with Claude Conversation Extractor in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-conversation-extractor.git
cd claude-conversation-extractor

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Install Playwright browsers
playwright install chromium
```

## Get Your Authentication Cookie

1. Open Claude.ai in your browser
2. Open Developer Tools (F12)
3. Go to the Application/Storage tab
4. Find Cookies → https://claude.ai
5. Copy the value of the `sessionKey` cookie

## Basic Usage

### Extract a Single Conversation

```bash
# Method 1: Use environment variable
export CLAUDE_SESSION_KEY="your_session_cookie_here"
claude-extract https://claude.ai/chat/YOUR_CONVERSATION_ID

# Method 2: Use command line flag
claude-extract https://claude.ai/chat/YOUR_CONVERSATION_ID \
  --auth-cookie "your_session_cookie_here"

# Method 3: Store in config (saves for future use)
claude-extract https://claude.ai/chat/YOUR_CONVERSATION_ID \
  --auth-method stored \
  --save-credentials
```

### Specify Output Directory

```bash
claude-extract https://claude.ai/chat/YOUR_CONVERSATION_ID \
  --output-dir ./my-exports
```

### Choose Export Format

```bash
# JSON only (LLM-optimized)
claude-extract URL --format json

# Markdown only (human-friendly)
claude-extract URL --format markdown

# Both (default)
claude-extract URL --format both
```

### Extract Multiple Conversations

Create a file `conversations.txt`:
```
https://claude.ai/chat/conversation1
https://claude.ai/chat/conversation2
https://claude.ai/chat/conversation3
```

Then run:
```bash
claude-extract batch conversations.txt --output-dir ./batch-exports
```

## Output Files

After extraction, you'll find these files in your output directory:

```
exports/
├── conversation.json     # LLM-optimized JSON
└── conversation.md       # Human-friendly Markdown report
```

### JSON Structure (LLM-Optimized)

```json
{
  "format_version": "1.0.0",
  "conversation_id": "abc123",
  "conversation_title": "Python Development Help",
  "model": "claude-sonnet-4-20250514",
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "Help me build a Python CLI tool",
      "timestamp": "2024-11-12T10:30:00Z",
      "tokens": 156
    }
  ],
  "artifacts": [...],
  "statistics": {...}
}
```

### Markdown Report Features

- 📊 Summary statistics
- 🌳 Conversation flow diagram (Mermaid)
- 💬 Full conversation transcript
- 🎨 All artifacts with syntax highlighting
- 🔧 Tool usage analysis
- ⚙️ System configuration

## Configuration

### Create Config File

Create `~/.claude-extractor/config.yaml`:

```yaml
# Default settings
output_dir: ~/claude-exports
format: both
include_artifacts: true
include_thinking: true

# Authentication
auth:
  method: stored
  save_credentials: true

# Performance
performance:
  timeout: 60
  max_concurrent: 3
  retry_attempts: 3
```

### Environment Variables

```bash
# Authentication
export CLAUDE_SESSION_KEY="your_cookie"

# Output directory
export CLAUDE_OUTPUT_DIR="~/exports"
```

## Troubleshooting

### "Authentication failed"
- Check that your session cookie is valid
- Try logging out and back in to Claude.ai
- Copy the cookie again

### "Timeout error"
- Increase timeout: `--timeout 120`
- Check your internet connection
- Try again later (might be rate limited)

### "No messages extracted"
- Enable verbose mode: `--verbose`
- Check if conversation URL is correct
- Verify you have access to the conversation

### "Module not found"
- Make sure you're in the virtual environment
- Run `pip install -e .` again
- Check Python version (requires 3.9+)

## Using as a Python Library

```python
from claude_extractor.extractors.hybrid_extractor import HybridExtractor
from claude_extractor.exporters.json_exporter import JSONExporter

# Extract
extractor = HybridExtractor(auth_cookie="your_cookie")
conversation = extractor.extract("https://claude.ai/chat/YOUR_ID")

# Export
exporter = JSONExporter(pretty=True)
exporter.export(conversation, "./conversation.json")

# Access data
print(f"Messages: {conversation.statistics.total_messages}")
print(f"Artifacts: {conversation.statistics.artifact_count}")

for message in conversation.messages:
    print(f"{message.role}: {message.content[:100]}...")
```

## Next Steps

1. **Read the full README**: More features and options
2. **Check examples/**: More usage examples
3. **Read AI_AGENT_PROMPTS.md**: If you want to extend the tool
4. **Join discussions**: Share your use cases and get help

## Common Use Cases

### 1. Backup Important Conversations

```bash
# Export to multiple formats for redundancy
claude-extract URL --format both --output-dir ./backups
```

### 2. Prepare for RAG/Embedding

```bash
# Get LLM-optimized JSON for embedding pipeline
claude-extract URL --format json --output-dir ./rag-data
```

### 3. Create Shareable Reports

```bash
# Generate beautiful Markdown for sharing
claude-extract URL --format markdown --output-dir ./reports
```

### 4. Batch Archive Conversations

```bash
# Archive all conversations from a project
claude-extract batch project-conversations.txt \
  --output-dir ./archive/$(date +%Y-%m-%d)
```

### 5. Analyze Conversation Patterns

```bash
# Extract multiple conversations and analyze
claude-extract batch conversations.txt --format json
# Then use Python to analyze the JSON files
```

## Performance Tips

1. **Reuse authentication**: Save credentials to avoid repeated logins
2. **Batch processing**: Extract multiple conversations at once
3. **Adjust timeout**: Increase for large conversations
4. **Use JSON only**: Skip Markdown generation if not needed

## Getting Help

- 🐛 **Bug reports**: [GitHub Issues](https://github.com/yourusername/claude-conversation-extractor/issues)
- 💡 **Feature requests**: [GitHub Discussions](https://github.com/yourusername/claude-conversation-extractor/discussions)
- 📚 **Documentation**: See `docs/` directory
- 🤝 **Contributing**: See `CONTRIBUTING.md`

---

**Ready to extract? Run your first extraction now!**

```bash
claude-extract https://claude.ai/chat/YOUR_CONVERSATION_ID
```
