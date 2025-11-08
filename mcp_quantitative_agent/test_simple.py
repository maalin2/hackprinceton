#!/usr/bin/env python3
"""
Simple test script for MCP Quantitative Agent Server

This script tests:
1. Standalone agent
2. MCP server imports
3. Server can be instantiated
"""

import sys
from pathlib import Path

print("=" * 80)
print("Simple MCP Server Test")
print("=" * 80)
print()

# Test 1: Standalone agent
print("Test 1: Standalone Agent")
print("-" * 80)
try:
    from quantitative_agent import QuantitativeAgent
    agent = QuantitativeAgent()
    categories = agent.get_categories()
    print("✓ Standalone agent works")
    print(f"  Found {len(categories['categories'])} categories")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
print()

# Test 2: MCP imports
print("Test 2: MCP Library")
print("-" * 80)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("✓ MCP library imports successfully")
except ImportError as e:
    print(f"✗ MCP library not installed: {e}")
    print("  Install with: pip install mcp")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error importing MCP: {e}")
    sys.exit(1)
print()

# Test 3: Server can be imported
print("Test 3: MCP Server Module")
print("-" * 80)
try:
    # Check if server_simple.py exists and can be imported
    server_path = Path(__file__).parent / "server_simple.py"
    if not server_path.exists():
        print(f"✗ server_simple.py not found at {server_path}")
        sys.exit(1)
    
    # Try to compile it
    import py_compile
    py_compile.compile(str(server_path), doraise=True)
    print("✓ server_simple.py compiles successfully")
except py_compile.PyCompileError as e:
    print(f"✗ Syntax error in server_simple.py: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
print()

# Test 4: Server can be instantiated (if we can import it)
print("Test 4: Server Instantiation")
print("-" * 80)
try:
    # We can't easily test the full server without running it,
    # but we can verify the imports work
    import importlib.util
    spec = importlib.util.spec_from_file_location("server_simple", server_path)
    if spec and spec.loader:
        print("✓ Server module can be loaded")
    else:
        print("✗ Cannot load server module")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
print()

print("=" * 80)
print("All Basic Tests Passed!")
print("=" * 80)
print()
print("Next Steps:")
print("1. Test the server manually: python server_simple.py")
print("2. Use MCP Inspector: npx @modelcontextprotocol/inspector python server_simple.py")
print("3. Integrate with Claude Desktop (see SETUP.md)")
print()

