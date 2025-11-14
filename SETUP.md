# Conversation Archaeologist - Setup Guide

## 🚀 Quick Start for PowerShell (Windows)

This guide will walk you through setting up and using Conversation Archaeologist from a fresh PowerShell terminal.

---

## Prerequisites

- **Python 3.10 or higher** installed
- **Git** installed (for cloning the repository)
- **PowerShell** (comes with Windows)

### Check Prerequisites

```powershell
# Check Python version (should be 3.10+)
python --version

# Check Git
git --version

# Check pip
pip --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/).

---

## Step-by-Step Setup

### 1. Open PowerShell

- Press `Win + X` and select "Windows PowerShell" or "Windows Terminal"
- Or search for "PowerShell" in the Start menu

### 2. Navigate to Your Projects Directory

```powershell
# Create a projects directory if you don't have one
mkdir $HOME\Projects
cd $HOME\Projects
```

### 3. Clone the Repository

```powershell
# Clone the repository
git clone https://github.com/yourusername/conversation-archaeologist.git

# Navigate into the directory
cd conversation-archaeologist
```

### 4. Create a Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```

**Note**: If you get a script execution error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` at the start of your command prompt when activated.

### 5. Install Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install pytest pytest-asyncio pytest-cov
```

### 6. Verify Installation

```powershell
# Run the test suite
python -m pytest tests/ -v

# You should see: "36 passed" with 97% coverage
```

---

## 📖 Using the Extraction Tool

### Phase 1: Manual Export Method

Since automated scraping is not yet implemented in Phase 1, you'll need to manually export conversations from Claude.ai:

#### Step 1: Extract Conversation ID from URL

```powershell
# Parse a Claude conversation URL to get the conversation ID
python scripts/extract.py https://claude.ai/chat/YOUR-CONVERSATION-ID
```

This will display instructions for manual export.

#### Step 2: Export Conversation from Claude.ai

1. Open your conversation in Claude.ai
2. Click the `...` menu in the top right corner
3. Select **"Export conversation"**
4. Save the JSON file to your computer (e.g., `conversation.json`)

#### Step 3: Process the Exported File

```powershell
# Process the manually exported JSON file
python scripts/extract.py --from-file path\to\conversation.json

# Example:
python scripts/extract.py --from-file $HOME\Downloads\conversation.json
```

#### Step 4: View Results

```powershell
# The output will be saved to /mnt/user-data/outputs/ by default
# On Windows, you can also specify a custom output directory:
python scripts/extract.py --from-file conversation.json --output-dir .\my_exports

# View the JSON output
cat .\my_exports\conv_YOUR-ID.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 📋 Common Commands

### Running Tests

```powershell
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_url_parser.py -v

# Run with coverage report
python -m pytest tests/ --cov=nano_agents --cov-report=html

# View coverage report (opens in browser)
start htmlcov\index.html
```

### Using Individual Nano-Agents

```powershell
# Test URL Parser
python -c "from nano_agents import URLParser; parser = URLParser(); print(parser.parse('https://claude.ai/chat/abc-123-def-456-789'))"

# Test Branch Detector
python nano_agents/branch_detector.py

# Test API Fetcher
python nano_agents/api_fetcher.py
```

### Getting Help

```powershell
# View CLI help
python scripts/extract.py --help

# View examples
python scripts/extract.py --help | Select-String -Pattern "Examples:" -Context 0,10
```

---

## 🔧 Troubleshooting

### "python is not recognized"

**Solution**: Add Python to your PATH
1. Search for "Environment Variables" in Start menu
2. Click "Environment Variables"
3. Add Python installation directory to PATH (e.g., `C:\Python311\`)

### "cannot be loaded because running scripts is disabled"

**Solution**: Enable script execution
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "ModuleNotFoundError: No module named 'nano_agents'"

**Solution**: Make sure you're in the project directory and virtual environment is activated
```powershell
# Check current directory
pwd

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Tests Fail with Import Errors

**Solution**: Install test dependencies
```powershell
pip install pytest pytest-asyncio pytest-cov
```

---

## 📁 Project Structure

```
conversation-archaeologist/
├── nano_agents/           # Core extraction agents
│   ├── __init__.py
│   ├── url_parser.py      # URL parsing agent
│   ├── api_fetcher.py     # Data fetching agent
│   └── branch_detector.py # Branch detection agent
├── scripts/               # CLI tools
│   └── extract.py         # Main extraction script
├── tests/                 # Unit tests
│   ├── test_url_parser.py
│   ├── test_api_fetcher.py
│   └── test_branch_detector.py
├── requirements.txt       # Python dependencies
├── README.md             # Project overview
├── SETUP.md              # This file
├── CLAUDE.md             # AI agent mission brief
└── ARCHITECTURE.md       # Technical architecture
```

---

## 🎯 Next Steps

After setup, you can:

1. **Extract a conversation**: Follow the "Using the Extraction Tool" section above
2. **Read the documentation**: Check out `README.md` for project overview
3. **View the architecture**: See `ARCHITECTURE.md` for technical details
4. **Run tests**: Use `python -m pytest tests/ -v` to verify everything works

---

## 🚧 Phase 1 Limitations

Current limitations (will be addressed in Phase 2):

- ❌ **No automated scraping**: Must manually export from Claude.ai
- ❌ **No batch processing**: Can only process one conversation at a time
- ❌ **No markdown export**: Only JSON output available
- ❌ **No official API**: Waiting for Anthropic to release conversation history API

These will be implemented in upcoming phases!

---

## 📞 Getting Help

If you encounter issues:

1. Check this SETUP.md for troubleshooting steps
2. Review error messages carefully
3. Make sure all prerequisites are installed
4. Check that virtual environment is activated
5. Verify you're in the correct directory

---

## ✅ Success Checklist

- [ ] Python 3.10+ installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Tests pass (36 passed with 97% coverage)
- [ ] Successfully extracted a conversation

Once all items are checked, you're ready to use Conversation Archaeologist!

---

**Happy Excavating! 🏺**
