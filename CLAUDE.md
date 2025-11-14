# CLAUDE CODE AGENT: CONVERSATION ARCHAEOLOGIST MISSION BRIEF

## 🎯 PROJECT MISSION

Build a production-grade conversation extraction and analysis system using nano-agent architecture. This system extracts Claude conversation data, reconstructs conversation trees with branches, generates human-friendly reports, and tracks quality metrics for continuous improvement.

**Project Status**: Phase 1 → Phase 4 (Full shipping and polish)  
**Timeline**: ~40 hours AI implementation time  
**Budget**: <$5 total development + testing costs  
**Success Criteria**: 95%+ extraction success rate on 50-conversation test set

---

## 🏗️ ARCHITECTURE OVERVIEW

### Nano-Agent Philosophy
Each agent has:
- **Single responsibility** (does one thing excellently)
- **Clear I/O contracts** (typed inputs/outputs)
- **Quality metrics** (tracks performance for optimization)
- **Error recovery** (graceful degradation with helpful messages)
- **Reusability** (composable across projects)

### Agent Chain
```
URL → [Parser] → ConversationID → [Fetcher] → RawJSON → [Detector] → Tree →
[Extractor] → Artifacts → [Generator] → Markdown → [Tracker] → Metrics
```

### Technology Stack
- **Python 3.10+** (type hints, dataclasses, async/await)
- **MCP SDK** (Model Context Protocol server)
- **Playwright** (web scraping fallback)
- **Pydantic** (data validation)
- **pytest** (testing framework)
- **rich** (beautiful CLI output)

---

## 📋 PHASE 1: MVP (PRIORITY)

**Goal**: Extract single conversations successfully with JSON output

### Deliverables
1. ✅ URL Parser (nano_agents/url_parser.py)
2. ✅ API Fetcher with fallback (nano_agents/api_fetcher.py)
3. ✅ Branch Detector (nano_agents/branch_detector.py)
4. ✅ CLI tool (scripts/extract.py)
5. ✅ Unit tests with 80%+ coverage
6. ✅ Documentation (README, ARCHITECTURE)

### Implementation Order
1. **Start with url_parser.py** - Pure Python, no external dependencies, fully testable
2. **Add branch_detector.py** - Pure logic, deterministic algorithm
3. **Build api_fetcher.py** - Requires async, Playwright setup, fallback logic
4. **Create extract.py CLI** - Orchestrates agents, provides UX
5. **Write tests** - TDD approach, test each agent independently
6. **Document** - README with quick start, architecture doc

### Key Implementation Notes

**URL Parser**:
- Handle both project and non-project conversation URLs
- Extract: conv_id, project_id (optional), org_id (optional)
- Pattern: `claude.ai/chat/{uuid}` or `claude.ai/project/{id}/chat/{uuid}`
- Validate UUID format (36 chars, lowercase hex with dashes)

**API Fetcher**:
```python
# Fallback strategy priority:
1. Try official API (not available yet, but future-proof)
2. Authenticated web scraping with Playwright
3. Prompt user for manual export

# Cost tracking:
- API calls: $0 (when available)
- Scraping: ~$0.02 per conversation (compute time)
- Track in quality_tracker for optimization
```

**Branch Detector**:
```python
# Algorithm:
1. Build parent-child map from flat message list
2. Traverse tree, label each node with branch_id
3. Branch occurs when node has >1 child
4. Mark active branch (most recent or longest path)
5. Return ConversationTree with complete structure
```

### Testing Strategy
```bash
# Unit tests (run frequently)
pytest tests/ -v

# Integration test (end-to-end)
python scripts/extract.py https://claude.ai/chat/test-conv-id

# Coverage report
pytest --cov=nano_agents --cov-report=html
```

### Success Criteria - Phase 1
- [ ] Extract 3 test conversations successfully
- [ ] Generate valid JSON output with all messages
- [ ] Detect branches correctly (manual verification)
- [ ] Unit test coverage ≥80%
- [ ] CLI runs without errors
- [ ] Documentation complete

---

## 📋 PHASE 2: PRODUCTION

**Goal**: Batch extraction, quality tracking, markdown export

### New Deliverables
1. Quality Tracker (nano_agents/quality_tracker.py)
2. Markdown Generator (nano_agents/markdown_generator.py)
3. Artifact Extractor (nano_agents/artifact_extractor.py)
4. Batch processor (scripts/batch_extract.py)
5. Enhanced error recovery
6. Performance optimization

### Implementation Notes

**Quality Tracker**:
```python
# Metrics to track:
- extraction_success_rate
- avg_execution_time
- cost_per_conversation
- data_completeness_percent
- user_edit_rate (manual feedback)
- strategy_breakdown (API vs scraping effectiveness)

# Storage: ~/.conversation_archaeologist/metrics.json
# Auto-optimize based on thresholds
```

**Markdown Generator**:
```markdown
# Template structure:
- Summary statistics
- Conversation tree visualization (Mermaid diagram)
- Full conversation transcript
- Artifacts section (code blocks, images)
- Tool usage analysis
- Branch details (if applicable)
```

**Batch Processing**:
```python
# Parallel extraction with rate limiting
- Max 5 concurrent extractions (avoid overwhelming API/site)
- Progress bar with rich library
- Aggregate quality metrics
- Generate batch report
```

### Success Criteria - Phase 2
- [ ] 95%+ success rate on 50-conversation test
- [ ] Markdown exports are human-readable
- [ ] Quality metrics persist across runs
- [ ] Batch processing handles 100 conversations
- [ ] Error recovery suggests solutions
- [ ] Cost stays under $2 for 100 conversations

---

## 📋 PHASE 3: INTELLIGENCE

**Goal**: Automatic insight generation from conversations

### New Deliverables
1. Pattern Analyzer (nano_agents/pattern_analyzer.py)
2. Decision Mapper (nano_agents/decision_mapper.py)
3. Topic Extractor (nano_agents/topic_extractor.py)
4. Insight Generator (nano_agents/insight_generator.py)

### Implementation Notes

**Pattern Analyzer**:
```python
# Detect patterns in:
- Prompt structures (what works)
- Tool usage sequences
- Conversation flow (user → assistant patterns)
- Branching behavior (when/why branches occur)

# Use simple heuristics + LLM for complex patterns
# Cost: ~$0.005 per conversation analyzed
```

**Topic Extractor**:
```python
# Methods:
1. Keyword extraction (TF-IDF)
2. Named entity recognition (spaCy)
3. LLM summarization (optional, costs $0.003)

# Output: List of topics with confidence scores
```

**Insight Generator**:
```python
# Generate insights on:
- Common themes across conversations
- Prompting strategies that worked
- Tools most frequently used
- Decision points and outcomes
- Knowledge gaps (repeated questions)

# Format: Actionable recommendations
```

### Success Criteria - Phase 3
- [ ] 80%+ of generated insights rated "useful"
- [ ] Insight generation completes in <30s per conversation
- [ ] Cost ≤$0.50 per 100 conversations analyzed
- [ ] Insights integrated into markdown report
- [ ] Topic extraction accuracy ≥70% (manual eval)

---

## 📋 PHASE 4: PCOST INTEGRATION

**Goal**: Feed insights into Personal Chief of Staff system

### New Deliverables
1. PCoS Connector (integrations/pcost_connector.py)
2. Knowledge Graph Builder (integrations/knowledge_graph.py)
3. Auto-tagging system
4. Cross-project insight linker

### Implementation Notes

**PCoS Connector**:
```python
# Integration points:
- Export insights to PCoS-compatible format
- Auto-create tasks from action items in conversations
- Link conversations to active projects
- Surface relevant past conversations when working on project

# Format: JSON schema compatible with PCoS
```

**Knowledge Graph**:
```python
# Graph structure:
Nodes: [Conversations, Topics, Projects, Decisions, Tools]
Edges: [discusses, relates_to, uses, decides, references]

# Storage: JSON or Neo4j (if available)
# Queries: "What conversations discuss Project X?"
```

### Success Criteria - Phase 4
- [ ] Successfully export 3 conversations to PCoS
- [ ] Knowledge graph contains 50+ nodes
- [ ] Cross-project links surfaced in 3+ projects
- [ ] Integration runs automatically (no manual steps)
- [ ] User reports using extracted insights in work

---

## 🔧 IMPLEMENTATION GUIDELINES

### Code Style
```python
# Type hints everywhere
def parse_url(url: str) -> ConversationIdentifier:
    ...

# Docstrings with examples
"""
Extract conversation ID from URL.

Args:
    url: Claude conversation URL

Returns:
    ConversationIdentifier with metadata

Raises:
    ValueError: If URL format is invalid

Examples:
    >>> parser = URLParser()
    >>> result = parser.parse("https://claude.ai/chat/abc-123")
    >>> result.conv_id
    'abc-123'
"""

# Use dataclasses for structured data
@dataclass
class ConversationIdentifier:
    conv_id: str
    project_id: Optional[str]
    is_project_conv: bool

# Async for I/O operations
async def fetch_conversation(conv_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        ...
```

### Error Handling
```python
# Always provide context and recovery suggestions
try:
    result = await fetcher.fetch(conv_id)
except AuthenticationError as e:
    logger.error(f"Auth failed: {e}")
    return {
        "error": str(e),
        "recovery_suggestions": [
            "Check that your Claude session token is valid",
            "Try refreshing your browser and extracting new token"
        ]
    }
```

### Testing
```python
# Test each agent independently
def test_url_parser_valid_conversation():
    parser = URLParser()
    result = parser.parse("https://claude.ai/chat/test-id")
    assert result.conv_id == "test-id"
    assert not result.is_project_conv

# Test error cases
def test_url_parser_invalid_url():
    parser = URLParser()
    with pytest.raises(ValueError, match="Invalid Claude URL"):
        parser.parse("https://not-claude.com/chat/test")

# Use fixtures for complex data
@pytest.fixture
def sample_conversation():
    return {
        "messages": [...],
        "metadata": {...}
    }
```

### Performance Optimization
```python
# Profile before optimizing
import cProfile
cProfile.run('extract_conversation(url)')

# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=100)
def parse_message(message_id: str) -> Message:
    ...

# Use async for I/O-bound operations
async def batch_extract(urls: List[str]) -> List[Result]:
    tasks = [extract_conversation(url) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

---

## 🧪 TESTING PROTOCOL

### Pre-Commit Checklist
```bash
# 1. Lint code
ruff check .
black .

# 2. Type check
mypy nano_agents/

# 3. Run tests
pytest tests/ -v --cov=nano_agents

# 4. Integration test
python scripts/extract.py https://claude.ai/chat/test-id

# 5. Check docs
python -m pydoc nano_agents.url_parser
```

### Test Coverage Targets
- **Unit tests**: 80%+ coverage
- **Integration tests**: All main workflows
- **Edge cases**: Invalid inputs, network errors, auth failures
- **Performance**: Extraction completes in <10s

### Manual Testing Checklist
- [ ] Extract conversation with no branches
- [ ] Extract conversation with multiple branches
- [ ] Extract conversation with artifacts (code, images)
- [ ] Extract conversation with tool usage
- [ ] Batch extract 10 conversations
- [ ] Generate markdown report
- [ ] Verify quality metrics persist
- [ ] Test error recovery (invalid URL, auth failure)

---

## 📊 QUALITY METRICS TARGETS

### Technical Metrics
```yaml
Phase 1:
  extraction_success_rate: ≥80%
  avg_execution_time: <10s
  unit_test_coverage: ≥80%

Phase 2:
  extraction_success_rate: ≥95%
  avg_execution_time: <5s
  data_completeness: ≥98%
  cost_per_conversation: <$0.02

Phase 3:
  insight_generation_time: <30s
  insight_usefulness_rate: ≥80%
  cost_per_analysis: <$0.005

Phase 4:
  pcost_integration_success: 100%
  cross_project_links: ≥5
  user_adoption: Daily use
```

### Economic Metrics
```yaml
Development:
  total_ai_time: ~40 hours
  total_cost: <$5
  
Operations:
  cost_per_conversation: <$0.02
  cost_per_100_batch: <$2
  annual_cost_heavy_user: <$20
```

---

## 🚀 DEPLOYMENT CHECKLIST

### Local Setup
```bash
# 1. Clone repository
git clone https://github.com/boss/conversation-archaeologist
cd conversation-archaeologist

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers (for scraping fallback)
playwright install chromium

# 5. Configure environment
cp config/example.env .env
# Edit .env with your Claude session token

# 6. Run tests
pytest tests/ -v

# 7. Try extraction
python scripts/extract.py https://claude.ai/chat/YOUR_CONV_ID
```

### MCP Server Deployment
```bash
# 1. Build package
python -m build

# 2. Install locally
pip install -e .

# 3. Configure Claude Desktop
# Add to claude_desktop_config.json:
{
  "mcpServers": {
    "conversation-archaeologist": {
      "command": "python",
      "args": ["-m", "mcp_server.conversation_archaeologist"],
      "env": {
        "CLAUDE_SESSION_TOKEN": "your_token_here"
      }
    }
  }
}

# 4. Restart Claude Desktop

# 5. Test MCP tools
# In Claude Desktop chat:
# "Use the conversation-archaeologist tool to extract https://claude.ai/chat/..."
```

### Production Deployment (Optional)
```bash
# If deploying as web service:
# 1. Containerize
docker build -t conversation-archaeologist .
docker run -p 8000:8000 conversation-archaeologist

# 2. Deploy to cloud (Railway, Render, etc.)
# 3. Set up monitoring (Sentry, LogRocket)
# 4. Configure rate limiting
# 5. Add authentication
```

---

## 🐛 DEBUGGING GUIDE

### Common Issues

**Issue: "Invalid URL format"**
```python
# Check URL pattern
# Valid: https://claude.ai/chat/abc-def-123
# Invalid: claude.ai/chat/abc (missing https://)
# Invalid: https://claude.ai/chats/abc (wrong path)

# Fix: Validate URL before parsing
parsed = urlparse(url)
if parsed.scheme not in ['http', 'https']:
    raise ValueError("URL must start with http:// or https://")
```

**Issue: "Authentication failed"**
```python
# Session token expired or invalid
# Solution:
1. Open Claude.ai in browser
2. Open DevTools (F12)
3. Go to Application > Cookies
4. Find sessionKey cookie
5. Copy value to .env file
6. Restart script

# Note: Tokens expire after ~30 days
```

**Issue: "Scraping timeout"**
```python
# Playwright can't load page in time
# Solutions:
1. Increase timeout: page.goto(url, timeout=60000)
2. Check internet connection
3. Try different browser: playwright install firefox
4. Use headful mode for debugging: browser.launch(headless=False)
```

**Issue: "Incomplete conversation data"**
```python
# Scraping missed some messages
# Solutions:
1. Scroll page fully before extraction
2. Wait for lazy-loaded content
3. Check for dynamic message loading
4. Increase wait time after page load
```

---

## 📚 REFERENCE

### Key Files Explained

**nano_agents/url_parser.py**
- Pure Python, no external dependencies
- Regex patterns for URL parsing
- Dataclasses for type safety
- Quality metrics tracking

**nano_agents/api_fetcher.py**
- Async HTTP client (httpx)
- Playwright for scraping fallback
- 3-tier strategy (API → Scraping → Manual)
- Cost tracking per strategy

**nano_agents/branch_detector.py**
- Graph algorithms for tree building
- Parent-child relationship mapping
- Branch point detection
- Active path identification

**mcp_server/conversation_archaeologist.py**
- MCP SDK integration
- Tool registration (extract, batch, analyze)
- Orchestrates all nano-agents
- Returns TextContent responses

**scripts/extract.py**
- CLI interface with rich formatting
- Progress bars for batch operations
- File output to /mnt/user-data/outputs
- Colored error messages

### Dependencies Explained

**Core**:
- `mcp` - Model Context Protocol SDK
- `playwright` - Browser automation
- `httpx` - Async HTTP client
- `pydantic` - Data validation

**Development**:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reports
- `ruff` - Fast Python linter
- `black` - Code formatter
- `mypy` - Static type checker

**Optional**:
- `rich` - Beautiful CLI output
- `typer` - CLI framework
- `loguru` - Better logging
- `sentry-sdk` - Error tracking

---

## 🎯 SUCCESS DEFINITION

You'll know you're done when:

### Phase 1 (MVP)
✅ CLI extracts 3 test conversations  
✅ JSON output is valid and complete  
✅ Tests pass with 80%+ coverage  
✅ Documentation is clear and complete  

### Phase 2 (Production)
✅ 95%+ success rate on 50 conversations  
✅ Markdown reports are beautiful  
✅ Quality metrics tracked automatically  
✅ Cost stays under $2 per 100 conversations  

### Phase 3 (Intelligence)
✅ Insights are rated 80%+ useful  
✅ Pattern detection finds real patterns  
✅ Topic extraction is accurate  
✅ Recommendations are actionable  

### Phase 4 (Integration)
✅ PCoS receives conversation insights  
✅ Knowledge graph has 50+ nodes  
✅ Cross-project links work  
✅ Boss uses it daily  

---

## 💡 OPTIMIZATION OPPORTUNITIES

### After Phase 1
- Cache parsed URLs to avoid re-parsing
- Add progress indicators for long extractions
- Parallel test execution for faster CI

### After Phase 2
- Use connection pooling for batch operations
- Implement exponential backoff for retries
- Add compression for large JSON exports

### After Phase 3
- Fine-tune topic extraction models
- Use cheaper LLMs for simple insights (Gemini Flash)
- Cache LLM responses to reduce costs

### After Phase 4
- Build web dashboard for visualization
- Add real-time streaming extraction
- Implement incremental updates (only fetch new messages)

---

## 📞 SUPPORT

If you encounter issues:

1. **Check logs**: `tail -f ~/.conversation_archaeologist/logs/app.log`
2. **Run diagnostics**: `python scripts/diagnose.py`
3. **Review metrics**: `python scripts/show_metrics.py`
4. **Test individual agents**: `pytest tests/test_agent_name.py -v`

For additional help:
- Review docs/ folder for detailed guides
- Check issues on GitHub
- Run with --verbose flag for detailed output

---

## 🏁 FINAL NOTES

**Time Investment Summary**:
- Phase 1: 10-12 hours
- Phase 2: 14-16 hours  
- Phase 3: 9-10 hours
- Phase 4: 7-8 hours
- **Total**: ~40 hours AI time (vs. 260 hours human time)

**Economic Summary**:
- Development: <$5 total
- Operations: ~$0.02 per conversation
- Annual (heavy use): ~$20

**Impact Summary**:
- Extract unlimited conversations
- Gain insights from conversation patterns
- Improve prompting strategies
- Feed into PCoS for compound benefits
- Reusable agents for other projects

---

**Ready to build! Start with Phase 1, test thoroughly, then proceed to Phase 2.**

Good luck, and remember: ship fast, iterate based on real usage, and let quality metrics guide optimization! 🚀
