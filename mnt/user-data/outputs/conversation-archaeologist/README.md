# 🔍 Conversation Archaeologist

**Extract, analyze, and gain insights from your Claude conversation history.**

A production-grade conversation extraction system built with nano-agent architecture. Extracts complete conversation data including branches, artifacts, and tool usage, then generates human-friendly reports and actionable insights.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### Phase 1 (MVP) - Available Now
- ✅ **URL Parsing** - Extract conversation IDs from Claude URLs
- ✅ **Multi-Strategy Fetching** - API → Scraping → Manual fallback
- ✅ **Branch Detection** - Reconstruct complete conversation trees
- ✅ **JSON Export** - Machine-readable conversation data
- ✅ **CLI Tool** - Simple command-line interface

### Phase 2 (Coming Soon)
- 🚧 **Markdown Reports** - Human-friendly conversation exports
- 🚧 **Batch Processing** - Extract 100+ conversations in parallel
- 🚧 **Quality Tracking** - Automatic performance metrics
- 🚧 **Error Recovery** - Intelligent fallback strategies

### Phase 3 (Planned)
- 📋 **Pattern Analysis** - Discover what prompting strategies work
- 📋 **Topic Extraction** - Automatic conversation categorization
- 📋 **Insight Generation** - Actionable recommendations from conversation history

### Phase 4 (Future)
- 🎯 **PCoS Integration** - Feed insights to Personal Chief of Staff
- 🎯 **Knowledge Graph** - Map relationships across conversations
- 🎯 **Cross-Project Links** - Surface relevant past conversations

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/boss/conversation-archaeologist
cd conversation-archaeologist

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for scraping fallback)
playwright install chromium

# Configure environment
cp config/example.env .env
# Edit .env with your Claude session token
```

### Extract Your First Conversation

```bash
# Single conversation
python scripts/extract.py https://claude.ai/chat/YOUR_CONVERSATION_ID

# Output saved to: /mnt/user-data/outputs/conv_YOUR_CONVERSATION_ID.json
```

### Batch Extraction (Phase 2)

```bash
# Multiple conversations
python scripts/batch_extract.py urls.txt

# Where urls.txt contains one URL per line
```

---

## 📖 How It Works

### Nano-Agent Architecture

The system is built from 7 specialized nano-agents, each with a single responsibility:

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│ URL Parser  │───▶│  API Fetcher │───▶│ Branch Detector│
└─────────────┘    └──────────────┘    └────────────────┘
                            │
                            ▼
┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│   Quality   │◀───│   Markdown   │◀───│    Artifact    │
│   Tracker   │    │  Generator   │    │   Extractor    │
└─────────────┘    └──────────────┘    └────────────────┘
```

### Extraction Strategy

**3-Tier Fallback System:**
1. **Official API** (when available) → Free, instant, complete
2. **Web Scraping** (Playwright) → $0.02 per conversation, 95% complete
3. **Manual Export** (user-guided) → Free, 100% complete

---

## 💰 Economics

### Development Costs (One-Time)
- **AI-Assisted**: ~40 hours implementation
- **Human Equivalent**: ~260 hours
- **Cost**: <$5 total (testing + compute)

### Operational Costs (Per Use)
- **Single extraction**: $0 (API) or $0.02 (scraping)
- **Batch 100 conversations**: ~$2.00
- **Annual (heavy user, 500 conversations)**: ~$20

---

## 📊 Quality Metrics

The system tracks quality metrics automatically for continuous improvement:

```python
{
  "extraction_success_rate": 0.95,
  "avg_execution_time_seconds": 3.2,
  "cost_per_conversation_usd": 0.015,
  "data_completeness_percent": 98.5,
  "strategy_breakdown": {
    "api": {"success_rate": 0.0, "usage": 0},      # Not yet available
    "scraping": {"success_rate": 0.96, "usage": 47},
    "manual": {"success_rate": 1.0, "usage": 3}
  }
}
```

View metrics: `python scripts/show_metrics.py`

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=nano_agents --cov-report=html

# View coverage report
open htmlcov/index.html

# Run specific test
pytest tests/test_url_parser.py -v

# Integration test
python scripts/extract.py https://claude.ai/chat/test-id --dry-run
```

**Test Coverage Targets:**
- Unit tests: 80%+
- Integration tests: All main workflows
- Edge cases: Invalid inputs, network errors, auth failures

---

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture details
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment guide
- **[API.md](docs/API.md)** - API reference
- **[CLAUDE.md](CLAUDE.md)** - Full development guide for Claude Code

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
CLAUDE_SESSION_TOKEN=your_session_token_here

# Optional
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR
MAX_CONCURRENT_EXTRACTIONS=5          # For batch processing
SCRAPING_TIMEOUT_MS=30000            # Playwright timeout
METRICS_FILE=~/.conversation_archaeologist/metrics.json
```

### Getting Your Session Token

1. Open [Claude.ai](https://claude.ai) in your browser
2. Open DevTools (F12)
3. Go to **Application** → **Cookies**
4. Find `sessionKey` cookie
5. Copy the value to your `.env` file

**Note**: Session tokens expire after ~30 days. Update when extraction fails with auth error.

---

## 🐛 Troubleshooting

### Common Issues

**"Invalid URL format"**
```bash
# Valid formats:
https://claude.ai/chat/abc-def-123-456
https://claude.ai/project/proj-id/chat/abc-def-123-456

# Invalid formats:
claude.ai/chat/abc-def-123-456        # Missing https://
https://claude.ai/chats/abc-def       # Wrong path
```

**"Authentication failed"**
- Session token expired → Get new token from browser
- Token not set → Check `.env` file
- Wrong token → Verify you copied complete value

**"Scraping timeout"**
- Slow connection → Increase `SCRAPING_TIMEOUT_MS` in `.env`
- Website changes → Check for browser updates: `playwright install chromium`
- Anti-bot detection → Use manual export fallback

**"Incomplete conversation data"**
- Long conversation → Increase page load wait time
- Dynamic loading → Check for lazy-loaded messages
- Branches missing → Verify branch detection algorithm

### Debug Mode

```bash
# Run with verbose logging
python scripts/extract.py URL --verbose

# Check logs
tail -f ~/.conversation_archaeologist/logs/app.log

# Run diagnostics
python scripts/diagnose.py
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development Setup:**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linters
ruff check .
black .
mypy nano_agents/
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- Inspired by nano-agent architecture principles
- Powered by [Playwright](https://playwright.dev) for web automation
- Uses [Rich](https://rich.readthedocs.io) for beautiful CLI output

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/boss/conversation-archaeologist/issues)
- **Discussions**: [GitHub Discussions](https://github.com/boss/conversation-archaeologist/discussions)
- **Documentation**: [docs/](docs/)

---

## 🗺️ Roadmap

### Q1 2025
- [x] Phase 1: MVP with JSON export
- [ ] Phase 2: Markdown reports and batch processing
- [ ] Comprehensive test suite (80%+ coverage)

### Q2 2025
- [ ] Phase 3: Pattern analysis and insights
- [ ] Web dashboard for visualization
- [ ] API endpoint for external integrations

### Q3 2025
- [ ] Phase 4: PCoS integration
- [ ] Knowledge graph visualization
- [ ] Advanced analytics and recommendations

---

**Built with ❤️ by Boss | Powered by Nano-Agent Architecture**
