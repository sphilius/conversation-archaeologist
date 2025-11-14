# Conversation Archaeologist - Technical Architecture

## System Overview

Conversation Archaeologist is a production-grade conversation extraction system built using **nano-agent architecture**. Each component (nano-agent) has a single responsibility and clear input/output contracts, enabling composability, testability, and continuous improvement.

## Design Principles

### 1. Nano-Agent Philosophy
- **Single Responsibility**: Each agent does one thing excellently
- **Clear I/O Contracts**: Typed inputs and outputs (Python type hints)
- **Quality Metrics**: Every agent tracks performance for DSPy-style optimization
- **Error Recovery**: Graceful degradation with helpful error messages
- **Reusability**: Agents compose across projects

### 2. Economic Design
- **Cost Transparency**: Track cost per operation
- **Strategy Optimization**: Automatic selection of cheapest viable approach
- **Budget Constraints**: Target <$0.02 per conversation

### 3. Quality-First
- **Metrics-Driven**: Track success rates, execution time, data completeness
- **Continuous Improvement**: Use quality metrics to identify optimization opportunities
- **Test Coverage**: 80%+ unit test coverage required

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│  CLI Tool          │  MCP Server        │  Web API (Future) │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Orchestration Layer                        │
├─────────────────────────────────────────────────────────────┤
│         ConversationExtractor (Agent Coordinator)            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ URL Parser   │───▶│ API Fetcher  │───▶│   Branch     │
│   (Agent 1)  │    │  (Agent 2)   │    │  Detector    │
│              │    │              │    │  (Agent 3)   │
└──────────────┘    └──────────────┘    └──────────────┘
                            │                     │
                            ▼                     ▼
                    ┌──────────────┐    ┌──────────────┐
                    │   Artifact   │    │   Markdown   │
                    │  Extractor   │    │  Generator   │
                    │  (Agent 4)   │    │  (Agent 5)   │
                    └──────────────┘    └──────────────┘
                            │                     │
                            └──────────┬──────────┘
                                       ▼
                              ┌──────────────┐
                              │   Quality    │
                              │   Tracker    │
                              │  (Agent 6)   │
                              └──────────────┘
```

## Nano-Agent Specifications

### Agent 1: URL Parser
**Purpose**: Extract conversation identifiers from Claude URLs

**Input**: 
```python
url: str  # Claude conversation URL
```

**Output**:
```python
ConversationIdentifier(
    conv_id: str,
    project_id: Optional[str],
    org_id: Optional[str],
    is_project_conv: bool,
    platform: str
)
```

**Quality Metrics**:
- Parse success rate: Target 99.5%
- Execution time: Target <100ms
- Validation accuracy: 100%

**Implementation**: Pure Python, regex-based pattern matching

---

### Agent 2: API Data Fetcher
**Purpose**: Fetch conversation data using optimal strategy

**Input**:
```python
conv_id: str
auth_token: Optional[str]
```

**Output**:
```python
Dict[str, Any]  # Full conversation JSON
```

**Strategies** (Priority Order):
1. **Official API** - Free, instant, 100% complete (not yet available)
2. **Web Scraping** - $0.02, 5-10s, 95% complete (Phase 2)
3. **Manual Export** - Free, user-initiated, 100% complete (Phase 1)

**Quality Metrics**:
- Strategy success rates
- Cost per conversation
- Data completeness percentage
- Execution time

**Implementation**: 
- Phase 1: Manual export guidance
- Phase 2: Playwright for scraping
- Phase 3: httpx for API calls

---

### Agent 3: Branch Detector
**Purpose**: Reconstruct conversation tree structure

**Input**:
```python
messages: List[Dict[str, Any]]  # Flat message list
```

**Output**:
```python
ConversationTree(
    root_id: str,
    nodes: Dict[str, MessageNode],
    branches: Dict[str, List[str]],
    active_branch: str
)
```

**Algorithm**:
1. Build parent-child map (O(n))
2. Traverse tree, labeling branches (O(n))
3. Identify active branch (most recent)
4. Mark active messages

**Quality Metrics**:
- Tree accuracy: 100% (deterministic)
- Branch detection: 100%
- Performance: O(n) complexity

**Implementation**: Pure Python graph algorithms

---

### Agent 4: Artifact Extractor (Phase 2)
**Purpose**: Extract and categorize artifacts

**Input**:
```python
tree: ConversationTree
```

**Output**:
```python
List[Artifact]  # Code blocks, images, etc.
```

**Artifact Types**:
- Code blocks (language detected)
- Images (base64 or URLs)
- Mermaid diagrams
- React components
- HTML/SVG

---

### Agent 5: Markdown Generator (Phase 2)
**Purpose**: Generate human-readable reports

**Input**:
```python
tree: ConversationTree
artifacts: List[Artifact]
```

**Output**:
```python
markdown_text: str  # Beautiful markdown report
```

**Template Sections**:
- Summary statistics
- Conversation tree (Mermaid diagram)
- Full transcript
- Artifacts section
- Tool usage analysis
- Branch details

---

### Agent 6: Quality Tracker
**Purpose**: Persistent quality tracking for optimization

**Input**:
```python
ExecutionMetrics(
    conversation_id: str,
    strategy_used: FetchStrategy,
    success: bool,
    execution_time: float,
    cost: float,
    data_completeness: float
)
```

**Output**:
```python
Dict[str, Any]  # Aggregated metrics
```

**Storage**: `~/.conversation_archaeologist/metrics.json`

**Optimization Triggers**:
- If user_edit_rate > 20%: Flag for format improvement
- If execution_time > 10s: Optimize strategy
- If cost > $0.05: Switch to cheaper method

## Data Flow

### Phase 1 (MVP) Flow
```
User provides URL
    │
    ▼
URLParser extracts conv_id
    │
    ▼
APIFetcher prompts for manual export
    │
    ▼
User exports JSON from Claude.ai
    │
    ▼
APIFetcher loads from file
    │
    ▼
BranchDetector builds tree
    │
    ▼
Output written to JSON file
    │
    ▼
QualityTracker updates metrics
```

### Phase 2 (Production) Flow
```
User provides URL
    │
    ▼
URLParser extracts conv_id
    │
    ▼
APIFetcher tries strategies:
    1. API (if available)
    2. Playwright scraping
    3. Manual export fallback
    │
    ▼
BranchDetector builds tree
    │
    ▼
ArtifactExtractor finds artifacts
    │
    ▼
MarkdownGenerator creates report
    │
    ▼
Both JSON and Markdown written
    │
    ▼
QualityTracker updates metrics
```

## Technology Stack

### Core Dependencies
- **Python 3.10+**: Type hints, dataclasses, async/await
- **MCP SDK**: Model Context Protocol integration
- **Playwright**: Browser automation (Phase 2+)
- **httpx**: Async HTTP client (Phase 3+)
- **Pydantic**: Data validation

### Development Tools
- **pytest**: Testing framework
- **ruff**: Fast linting
- **black**: Code formatting
- **mypy**: Static type checking

### Optional
- **rich**: Beautiful CLI output
- **typer**: CLI framework
- **loguru**: Enhanced logging

## Quality Assurance

### Testing Strategy
- **Unit Tests**: 80%+ coverage required
- **Integration Tests**: End-to-end workflows
- **Edge Cases**: Invalid inputs, network failures, auth errors
- **Performance Tests**: Execution time benchmarks

### Code Quality
- **Type Hints**: All functions typed
- **Docstrings**: Examples included
- **Comments**: Explain non-obvious logic
- **Linting**: ruff + black + mypy clean

### Metrics Tracking
Every execution tracks:
- Success rate
- Execution time
- Cost
- Data completeness
- Strategy effectiveness

## Performance Characteristics

### Time Complexity
- **URL Parsing**: O(1) - Regex matching
- **Branch Detection**: O(n) - Linear tree traversal
- **API Fetching**: O(1) - Single request (Phase 2+)
- **Overall**: O(n) where n = number of messages

### Space Complexity
- **In-memory tree**: O(n) - All nodes stored
- **JSON output**: O(n) - Full conversation serialized

### Execution Time Targets
- URL parsing: <100ms
- Branch detection: <1s for 1000 messages
- API fetch: <5s per conversation
- Full extraction: <10s per conversation

### Cost Targets
- API strategy: $0 (when available)
- Scraping strategy: ~$0.02 per conversation
- Manual export: $0
- Target average: <$0.01 per conversation

## Security Considerations

### Authentication
- Session tokens stored in `.env` (never committed)
- Tokens expire after ~30 days
- No passwords stored

### Data Privacy
- All processing happens locally
- No data sent to third parties
- User controls output location

### Input Validation
- URL format validation
- UUID format validation
- Message structure validation
- JSON schema validation

## Scalability

### Horizontal Scaling
- Batch processing: 5 concurrent extractions (default)
- Configurable via `MAX_CONCURRENT_EXTRACTIONS`
- Rate limiting to avoid API throttling

### Vertical Scaling
- Memory efficient: Stream large conversations
- Disk efficient: Compress old exports
- CPU efficient: O(n) algorithms throughout

## Future Enhancements

### Phase 3: Intelligence
- Pattern analyzer (prompting strategies)
- Topic extractor (conversation categorization)
- Decision mapper (track decision points)
- Insight generator (actionable recommendations)

### Phase 4: Integration
- PCoS connector (Personal Chief of Staff)
- Knowledge graph (Neo4j or JSON)
- Auto-tagging system
- Cross-project linking

### Phase 5: Advanced
- Real-time streaming extraction
- Incremental updates (only fetch new messages)
- Web dashboard visualization
- Multi-user support

## Debugging Guide

### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
python scripts/extract.py URL --verbose
```

### View Logs
```bash
tail -f ~/.conversation_archaeologist/logs/app.log
```

### Run Diagnostics
```bash
python scripts/diagnose.py
```

### Test Individual Agents
```bash
# Test URL parser
python -m nano_agents.url_parser

# Test branch detector
python -m nano_agents.branch_detector

# Run unit tests
pytest tests/test_url_parser.py -v
```

## Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/boss/conversation-archaeologist

# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v --cov
```

### Code Style
- Follow PEP 8
- Use type hints everywhere
- Write docstrings with examples
- Keep functions < 50 lines
- Keep files < 500 lines

### Pull Request Process
1. Create feature branch
2. Write tests (maintain 80%+ coverage)
3. Update documentation
4. Run linters (`ruff check .`, `black .`, `mypy .`)
5. Submit PR with description

---

**Last Updated**: 2025-11-14  
**Version**: 0.1.0 (Phase 1 MVP)
