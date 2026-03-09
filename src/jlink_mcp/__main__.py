"""JLink MCP 服务器启动入口.

使用方法:
    python -m jlink_mcp
    
或:
    python -m jlink_mcp.server
"""

import sys
from .server import main

if __name__ == "__main__":
    sys.exit(main() or 0)
