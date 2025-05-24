"""
MCP服务器配置模块 - 包含连接A股MCP服务器的配置信息
"""

# 服务器配置，用于初始化MCP客户端
SERVER_CONFIGS = {
    "a_share_mcp_v2": {  # 重命名以提高清晰度，原名为 "a-share-mcp-v2"
        "command": "uv",  # 假设'uv'在PATH中或使用完整路径
        "args": [
            "run",  # uv run命令
            "--directory",
            r"E:\github\a_share_mcp",  # MCP服务器项目的路径
            "python",  # 在uv中运行的命令
            "mcp_server.py"  # MCP服务器脚本
        ],
        "transport": "stdio",
    }
}
