# AI Coding Agent Prompts for Claude Conversation Extractor

This document contains specialized prompts for AI coding agents (Cursor, Aider, Continue, etc.) to help them understand, extend, and improve the Claude Conversation Extractor codebase.

---

## 🎯 General Context Prompt

```
You are working on the Claude Conversation Extractor project, a Python CLI tool that extracts complete conversation data from Claude.ai, including all messages, branches, artifacts, tool calls, and metadata.

ARCHITECTURE OVERVIEW:
- Models: Pydantic data models in src/claude_extractor/models/
- Extractors: Multiple extraction strategies (API, browser automation)
- Exporters: JSON (LLM-optimized) and Markdown (human-friendly) formats
- CLI: Rich Click-based interface with progress bars and formatting
- Config: YAML-based configuration with Pydantic validation

KEY DESIGN PRINCIPLES:
1. Type safety: All code uses Python type hints and Pydantic models
2. Multiple strategies: Hybrid extractor tries API first, falls back to browser
3. Two audiences: JSON for LLMs/RAG, Markdown for humans
4. Rich UX: Progress bars, colored output, comprehensive error messages
5. Extensibility: Plugin-ready architecture for custom processors

CURRENT STATE:
- Core extraction works via Playwright browser automation
- API extraction is a TODO (requires reverse engineering Claude's API)
- Basic analysis features are placeholders for enhancement
- All code follows Black formatting, isort import sorting, type checking with mypy

When making changes:
1. Maintain type safety - use type hints everywhere
2. Follow existing patterns - check similar code before implementing
3. Add logging - use loguru for all significant operations
4. Write docstrings - use Google style for all public functions
5. Update tests - add tests for new features in tests/ directory
```

---

## 🔧 Enhancement Prompts

### Prompt 1: Implementing API-Based Extraction

```
TASK: Implement API-based extraction for Claude conversations

CONTEXT:
The HybridExtractor class in src/claude_extractor/extractors/hybrid_extractor.py has a placeholder _extract_via_api() method that needs implementation. This method should use Claude.ai's internal API to fetch conversation data more reliably than browser scraping.

REQUIREMENTS:
1. Research Claude.ai's network requests to identify the conversation API endpoint
2. Implement authentication using the session cookie
3. Parse the API response into our Conversation model
4. Handle pagination if conversations are returned in chunks
5. Extract all metadata: branches, artifacts, tool calls, thinking content
6. Add comprehensive error handling with specific exceptions
7. Include retry logic with exponential backoff
8. Log all API requests and responses (at DEBUG level)

ACCEPTANCE CRITERIA:
- API extraction completes faster than browser automation
- All conversation data matches what browser extraction provides
- Works with and without authentication (degraded mode if no auth)
- Handles rate limiting gracefully
- Falls back to browser extraction if API fails

IMPLEMENTATION NOTES:
- Use httpx for async HTTP requests
- Store API endpoints in config.py for easy updates
- Add API response examples to docs/ for reference
- Consider caching responses to avoid duplicate requests
```

### Prompt 2: Advanced Conversation Analysis

```
TASK: Enhance conversation analysis with NLP and pattern detection

CONTEXT:
The ConversationAnalyzer class in src/claude_extractor/analyzers/conversation_analyzer.py is currently a placeholder with basic heuristics. We need real analysis features.

REQUIREMENTS:
1. Topic Extraction:
   - Use sentence transformers or spaCy for semantic analysis
   - Identify 3-7 main topics discussed in the conversation
   - Track topic transitions across messages
   
2. Complexity Scoring:
   - Measure technical depth (specialized terminology frequency)
   - Calculate branching complexity (decision trees)
   - Assess information density (ideas per message)
   - Consider tool usage patterns
   
3. Decision Point Detection:
   - Identify branch points where conversation could have gone differently
   - Flag messages where Claude asked clarifying questions
   - Note when user changed direction or pivoted topic
   
4. Conversation Flow:
   - Map information flow: who introduces new concepts
   - Track question → answer → follow-up patterns
   - Identify teaching moments vs. task execution

LIBRARIES TO CONSIDER:
- spacy: NLP pipeline
- sentence-transformers: Semantic similarity
- scikit-learn: Clustering for topic detection
- networkx: Conversation flow graphs

OUTPUT FORMAT:
Return structured analysis that can be added to both JSON and Markdown exports:
{
  "topics": [{"name": str, "weight": float, "message_ids": List[str]}],
  "complexity": {"score": float, "factors": Dict[str, float]},
  "decision_points": [{"message_id": str, "type": str, "description": str}],
  "flow": {"type": str, "transitions": List[Dict]}
}
```

### Prompt 3: Multi-Conversation Comparison

```
TASK: Add ability to compare multiple conversations and find patterns

CONTEXT:
Users often want to compare conversations to find similarities, track how their usage evolves over time, or identify which conversations were most valuable.

REQUIREMENTS:
1. Comparison Features:
   - Find conversations about similar topics
   - Compare token usage and efficiency
   - Identify recurring patterns (same questions, similar workflows)
   - Track skill/tool usage evolution over time
   
2. Similarity Metrics:
   - Semantic similarity between conversations
   - Topic overlap
   - Tool usage overlap
   - Conversation structure similarity (Q&A vs. collaborative)
   
3. Visualization:
   - Generate comparison tables
   - Create timeline of conversation topics
   - Build network graph of related conversations
   - Export comparison reports in Markdown

IMPLEMENTATION:
- Add new ComparisonAnalyzer class in analyzers/
- Create CLI command: claude-extract compare <url1> <url2> [url3...]
- Support batch comparison from conversation list
- Export results to comparison.md and comparison.json

ACCEPTANCE CRITERIA:
- Can compare 2-20 conversations efficiently
- Produces meaningful similarity scores (0-100)
- Generates visual comparison report
- Identifies common patterns across conversations
```

### Prompt 4: Export to Additional Formats

```
TASK: Add exporters for Obsidian, Notion, and HTML formats

CONTEXT:
Users want to save conversations to their preferred note-taking systems. We need exporters for popular platforms.

REQUIREMENTS:
1. Obsidian Exporter:
   - Create linked markdown files (one per conversation)
   - Add frontmatter with metadata (date, model, tags)
   - Generate index file linking all conversations
   - Support Obsidian-specific features (backlinks, tags, dataview)
   
2. Notion Exporter:
   - Use Notion API to create pages
   - Preserve formatting (code blocks, quotes)
   - Organize in databases with properties
   - Support nested pages for branches
   
3. HTML Exporter:
   - Generate standalone HTML with embedded CSS
   - Make it self-contained (no external dependencies)
   - Add syntax highlighting for code
   - Include search functionality
   - Responsive design for mobile

IMPLEMENTATION:
- Add new exporter classes in exporters/
- Follow same interface as JSONExporter and MarkdownExporter
- Add --format obsidian|notion|html to CLI
- Include CSS/JS templates in package resources

PLUGIN SYSTEM:
Consider designing a plugin system where users can add custom exporters:
- Abstract BaseExporter class
- Entry point for third-party exporters
- Configuration for enabled exporters
```

### Prompt 5: Real-Time Monitoring Mode

```
TASK: Add ability to monitor and auto-export active conversations in real-time

CONTEXT:
Users want to automatically back up their conversations as they happen, rather than manually exporting after the fact.

REQUIREMENTS:
1. Watch Mode:
   - Monitor user's active Claude conversations
   - Detect when new messages are added
   - Auto-export when conversation pauses (no activity for N seconds)
   - Support multiple concurrent conversations
   
2. Configuration:
   - Set export interval (e.g., every 5 minutes)
   - Choose which formats to auto-export
   - Specify output directory structure
   - Filter by project or tag
   
3. CLI Interface:
   - New command: claude-extract watch [--interval 300]
   - Show live status of monitored conversations
   - Display notifications when exports complete
   
4. Features:
   - Differential exports (only save changes since last export)
   - Conflict resolution if conversation branches
   - Bandwidth-efficient polling
   - Error recovery and retry logic

IMPLEMENTATION NOTES:
- Use asyncio for concurrent monitoring
- Implement efficient polling (check for updates without full extraction)
- Store state in ~/.claude-extractor/watch_state.json
- Use file system watcher or periodic polling
- Add keyboard shortcuts (Ctrl+E to force export current conversation)
```

---

## 🐛 Debugging Prompts

### Prompt 6: Debug Extraction Failures

```
TASK: Diagnose and fix extraction failures

WHEN THIS IS NEEDED:
- Extraction times out
- Missing messages or artifacts
- Authentication errors
- Parsing errors

DEBUGGING STRATEGY:
1. Enable verbose logging:
   claude-extract URL --verbose

2. Check authentication:
   - Verify CLAUDE_SESSION_KEY environment variable
   - Test cookie validity manually
   - Check for IP-based restrictions

3. Inspect browser automation:
   - Run with headless=False to see browser
   - Add page.screenshot() at key points
   - Log DOM structure when selectors fail

4. Validate data models:
   - Check Pydantic validation errors
   - Verify datetime parsing (timezone issues)
   - Test with minimal conversation first

5. Network issues:
   - Increase timeout values
   - Check for rate limiting (429 errors)
   - Verify proxy settings if applicable

COMMON FIXES:
- Update selectors if Claude UI changed
- Handle new message types in parser
- Add error handling for missing optional fields
- Implement retry with backoff for transient failures
```

---

## 🧪 Testing Prompts

### Prompt 7: Add Comprehensive Tests

```
TASK: Create comprehensive test suite

REQUIREMENTS:
1. Unit Tests:
   - Test each model for validation
   - Test parsers with sample HTML/JSON
   - Test exporters with sample Conversation objects
   - Test URL parsing and validation
   
2. Integration Tests:
   - Test full extraction pipeline with mock data
   - Test CLI commands with temp directories
   - Test configuration loading and validation
   
3. Fixtures:
   - Create sample conversation JSON files
   - Create sample HTML responses
   - Create test authentication cookies (expired/invalid)
   
4. Mocking:
   - Mock Playwright browser automation
   - Mock API responses
   - Mock file I/O operations

STRUCTURE:
tests/
├── unit/
│   ├── test_models.py
│   ├── test_parsers.py
│   ├── test_exporters.py
│   └── test_config.py
├── integration/
│   ├── test_extraction_pipeline.py
│   ├── test_cli.py
│   └── test_end_to_end.py
├── fixtures/
│   ├── sample_conversation.json
│   ├── sample_page.html
│   └── sample_api_response.json
└── conftest.py

RUN TESTS:
pytest --cov=claude_extractor --cov-report=html
pytest -v tests/unit/
pytest -v tests/integration/
```

---

## 📚 Documentation Prompts

### Prompt 8: Write Comprehensive Documentation

```
TASK: Create complete documentation for the project

STRUCTURE:
docs/
├── index.md                 # Overview and quick start
├── installation.md          # Detailed setup instructions
├── usage/
│   ├── basic.md            # Basic extraction
│   ├── advanced.md         # Advanced features
│   ├── batch.md            # Batch processing
│   └── configuration.md    # Config file reference
├── architecture/
│   ├── overview.md         # System design
│   ├── extractors.md       # Extraction strategies
│   ├── exporters.md        # Export formats
│   └── extending.md        # Plugin development
├── api/
│   ├── models.md           # Data models reference
│   ├── cli.md              # CLI reference
│   └── python_api.md       # Using as library
├── examples/
│   ├── basic_usage.md
│   ├── custom_exporter.md
│   └── analysis_pipeline.md
└── troubleshooting.md      # Common issues and fixes

REQUIREMENTS:
- Use MkDocs with Material theme
- Include code examples for every feature
- Add screenshots of CLI output
- Provide sample outputs (JSON, Markdown)
- Document all configuration options
- Include FAQs and troubleshooting guide
- Add contributor guidelines
```

---

## 🚀 Performance Optimization Prompts

### Prompt 9: Optimize Extraction Performance

```
TASK: Improve extraction speed and resource usage

CURRENT BOTTLENECKS:
1. Browser automation is slow (5-10 seconds per conversation)
2. Large conversations timeout
3. Memory usage grows with conversation size
4. No caching of intermediate results

OPTIMIZATION OPPORTUNITIES:
1. Parallel Extraction:
   - Extract multiple conversations concurrently
   - Use asyncio for I/O-bound operations
   - Implement connection pooling
   
2. Caching:
   - Cache API responses (with TTL)
   - Store partially extracted data
   - Resume interrupted extractions
   
3. Smart Loading:
   - Load messages lazily (only visible portion)
   - Stream large artifacts to disk
   - Use generators instead of lists where possible
   
4. Browser Optimization:
   - Reuse browser instance across extractions
   - Disable unnecessary features (images, CSS)
   - Use faster selectors
   - Reduce wait times with better loading detection

BENCHMARKING:
- Add --benchmark flag to measure performance
- Track metrics: time per message, memory usage, API calls
- Compare strategies: API vs browser vs hybrid
- Profile with py-spy or cProfile

TARGET METRICS:
- Extract 50-message conversation in <3 seconds
- Support conversations with 500+ messages
- Keep memory usage under 200MB
- Batch extract 10 conversations in <30 seconds
```

---

## 🔐 Security Prompts

### Prompt 10: Enhance Security and Privacy

```
TASK: Implement security best practices and privacy protections

SECURITY REQUIREMENTS:
1. Credential Management:
   - Never log authentication cookies
   - Use keyring for secure storage
   - Support environment variables
   - Clear credentials from memory after use
   
2. Data Protection:
   - Encrypt exported files (optional)
   - Sanitize sensitive data before logging
   - Add --redact flag to remove PII
   - Secure temp file handling
   
3. Network Security:
   - Verify SSL certificates
   - Support proxy configurations
   - Implement rate limiting
   - Add request signing (if API supports it)
   
4. Access Control:
   - Set restrictive file permissions (600 for configs)
   - Validate file paths (prevent directory traversal)
   - Limit export destinations
   
5. Privacy Features:
   - Add --anonymize flag to remove identifiable info
   - Strip metadata that could identify user
   - Provide data deletion utilities
   - Document data handling in privacy policy

IMPLEMENTATION:
- Add AuthManager class for credential handling
- Use cryptography library for encryption
- Add security.md documentation
- Include security audit checklist
- Add --security-check command to validate setup
```

---

## 🌟 Feature Request Templates

### Prompt 11: Implement Feature X

```
Use this template when implementing new features:

FEATURE: [Name of feature]

USER STORY:
As a [type of user]
I want to [action]
So that [benefit]

REQUIREMENTS:
1. Functional Requirements:
   - [List specific behaviors]
   
2. Non-Functional Requirements:
   - Performance: [metrics]
   - Usability: [UX considerations]
   - Compatibility: [platforms, versions]

DESIGN:
1. API Design:
   - New classes/functions needed
   - Changes to existing interfaces
   - Configuration options
   
2. Data Model:
   - New models or fields
   - Database schema (if applicable)
   - Migration strategy

IMPLEMENTATION PLAN:
1. [Step 1]
2. [Step 2]
3. [Step 3]

TESTING:
- Unit tests: [what to test]
- Integration tests: [scenarios]
- Manual testing: [test cases]

DOCUMENTATION:
- Update README
- Add to docs/
- Update examples/
- Update CLI help text

ROLLOUT:
- Feature flag: [yes/no]
- Beta testing: [plan]
- Deprecation: [if replacing existing feature]
```

---

## 📊 Code Quality Prompts

### Prompt 12: Code Review Checklist

```
Before submitting changes, verify:

TYPE SAFETY:
□ All functions have type hints
□ Return types are specified
□ Pydantic models used for data validation
□ mypy passes with no errors

CODE STYLE:
□ Formatted with Black (line length 100)
□ Imports sorted with isort
□ No unused imports or variables
□ Docstrings follow Google style
□ No commented-out code

ERROR HANDLING:
□ Specific exceptions used
□ Error messages are helpful
□ Logging at appropriate levels
□ Graceful degradation where possible

TESTING:
□ New code has tests
□ Tests pass locally
□ Coverage above 80%
□ Edge cases handled

DOCUMENTATION:
□ README updated if needed
□ API docs updated
□ Examples added/updated
□ Changelog entry added

PERFORMANCE:
□ No obvious inefficiencies
□ Appropriate data structures used
□ Async where beneficial
□ Resources cleaned up properly

SECURITY:
□ No hardcoded secrets
□ Input validation present
□ SQL injection prevented (if applicable)
□ XSS prevented (if applicable)
```

---

## 🎓 Learning Prompts

### Prompt 13: Understanding the Codebase

```
If you're new to this codebase, follow this learning path:

1. READ THESE FIRST:
   - README.md - Project overview
   - src/claude_extractor/models/__init__.py - Data structures
   - src/claude_extractor/cli.py - User interface
   
2. UNDERSTAND THE FLOW:
   - CLI receives URL → Config loaded → Extractor selected
   - Extractor tries strategies → Data parsed into models
   - Exporters generate outputs → Files written to disk
   
3. KEY ABSTRACTIONS:
   - Conversation: Root data structure containing everything
   - Message: Individual turn in conversation
   - Artifact: Code/content created during conversation
   - Branch: Alternative conversation paths
   
4. IMPORTANT PATTERNS:
   - Strategy pattern: Multiple extractors with same interface
   - Builder pattern: Exporters construct complex outputs
   - Factory pattern: Config creates appropriate extractors
   
5. COMMON TASKS:
   - Adding new field to model: Update Pydantic model → Update parser → Update exporters
   - Adding new export format: Create new exporter class → Register in CLI
   - Improving extraction: Update _extract_from_page() logic → Test with real conversations
   
6. DEBUG WITH:
   - --verbose flag for detailed logging
   - pytest -v -s for test output
   - python -m pdb for interactive debugging
   - Add logger.debug() liberally

7. CONTRIBUTE BY:
   - Picking issue labeled "good first issue"
   - Improving documentation
   - Adding tests for untested code
   - Optimizing slow operations
```

---

## 🚢 Release Prompts

### Prompt 14: Preparing a Release

```
TASK: Prepare version X.Y.Z for release

CHECKLIST:
1. Version Bump:
   □ Update __version__ in __init__.py
   □ Update version in setup.py
   □ Update version in pyproject.toml
   
2. Changelog:
   □ Update CHANGELOG.md with all changes
   □ Organize by: Added, Changed, Fixed, Removed
   □ Credit contributors
   
3. Testing:
   □ All tests pass
   □ Manual testing of critical paths
   □ Test on multiple Python versions (3.9-3.12)
   □ Test installation from source
   
4. Documentation:
   □ README is current
   □ API docs regenerated
   □ Examples work with new version
   □ Migration guide if breaking changes
   
5. Package:
   □ Build: python -m build
   □ Check: twine check dist/*
   □ Test install: pip install dist/*.whl
   
6. Git:
   □ All changes committed
   □ Tag created: git tag vX.Y.Z
   □ Push tags: git push --tags
   
7. PyPI:
   □ Upload to TestPyPI first
   □ Test install from TestPyPI
   □ Upload to PyPI: twine upload dist/*
   
8. Announce:
   □ GitHub release with notes
   □ Update project website
   □ Post to relevant communities
```

---

**Use these prompts to guide AI coding agents in making consistent, high-quality contributions to the Claude Conversation Extractor project.**
