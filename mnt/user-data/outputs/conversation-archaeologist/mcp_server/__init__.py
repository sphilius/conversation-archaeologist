"""
Model Context Protocol Server for Conversation Archaeologist.

Exposes conversation extraction and analysis as MCP tools.

Usage:
    # Run as standalone MCP server
    python -m mcp_server.conversation_archaeologist
    
    # Or configure in Claude Desktop config:
    {
      "mcpServers": {
        "conversation-archaeologist": {
          "command": "python",
          "args": ["-m", "mcp_server.conversation_archaeologist"]
        }
      }
    }
"""

__version__ = "0.1.0"
