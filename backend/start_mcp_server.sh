#!/bin/bash
# MCP Server Startup Script for Univer Report System

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Set Python path to include backend directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Navigate to backend directory
cd "$SCRIPT_DIR"

# Start MCP server
python3 mcp_server/server.py
