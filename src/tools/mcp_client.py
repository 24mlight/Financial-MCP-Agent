from langchain_mcp_adapters.client import MultiServerMCPClient
from src.utils.logging_config import setup_logger, SUCCESS_ICON, ERROR_ICON, WAIT_ICON
from src.tools.mcp_config import SERVER_CONFIGS
import asyncio  # Required for async operations like get_tools
import json

logger = setup_logger(__name__)

# Global client instance, initialized when tools are first requested.
_mcp_client_instance = None
_mcp_tools = None


def print_tool_details(tools):
    """打印工具的详细信息，用于调试"""
    logger.info(f"{SUCCESS_ICON} 工具详细信息:")
    for i, tool in enumerate(tools, 1):
        logger.info(f"  {i}. 工具名称: {tool.name}")
        logger.info(f"     描述: {tool.description}")

        # 打印参数schema
        if hasattr(tool, 'args') and tool.args:
            logger.info(
                f"     参数schema: {json.dumps(tool.args, ensure_ascii=False, indent=6)}")
        elif hasattr(tool, 'args_schema') and tool.args_schema:
            logger.info(f"     参数schema: {tool.args_schema}")
        else:
            logger.info(f"     参数schema: 无")

        # 打印其他可能的属性
        for attr in ['input_schema', 'parameters', 'schema']:
            if hasattr(tool, attr):
                attr_value = getattr(tool, attr)
                if attr_value:
                    logger.info(f"     {attr}: {attr_value}")

        logger.info(f"     工具类型: {type(tool)}")
        logger.info(f"     所有属性: {dir(tool)}")
        logger.info("     " + "-" * 50)


async def get_mcp_tools():
    """
    Initializes the MultiServerMCPClient with the defined server configurations
    and fetches the available tools from the a-share-mcp-v2 server.

    Returns:
        list: A list of LangChain-compatible tools loaded from the MCP server.
              Returns an empty list if initialization or tool loading fails.
    """
    global _mcp_client_instance, _mcp_tools

    if _mcp_tools is not None:
        logger.info(f"{SUCCESS_ICON} Returning cached MCP tools.")
        return _mcp_tools

    logger.info(
        f"{WAIT_ICON} Initializing MultiServerMCPClient with config: {SERVER_CONFIGS}")
    try:
        _mcp_client_instance = MultiServerMCPClient(SERVER_CONFIGS)

        logger.info(
            f"{WAIT_ICON} Fetching tools from MCP server 'a_share_mcp_v2'...")
        # The get_tools() method is asynchronous.
        loaded_tools = await _mcp_client_instance.get_tools()

        if not loaded_tools:
            logger.warning(
                f"{ERROR_ICON} No tools loaded from MCP server 'a_share_mcp_v2'. Check server logs and configuration.")
            _mcp_tools = []  # Cache empty list on failure to load
            return []

        _mcp_tools = loaded_tools
        logger.info(
            f"{SUCCESS_ICON} Successfully loaded {len(_mcp_tools)} tools from 'a_share_mcp_v2'.")

        # 打印工具名称列表
        tool_names = [tool.name for tool in _mcp_tools]
        logger.info(f"工具名称列表: {tool_names}")

        # 打印详细的工具信息
        print_tool_details(_mcp_tools)

        return _mcp_tools

    except Exception as e:
        logger.error(
            f"{ERROR_ICON} Failed to initialize MCP client or load tools: {e}", exc_info=True)
        _mcp_tools = []  # Cache empty list on failure
        return []


async def test_tool_call(tool_name, tool_args):
    """
    测试特定工具的调用

    Args:
        tool_name: 工具名称
        tool_args: 工具参数

    Returns:
        工具调用结果
    """
    try:
        tools = await get_mcp_tools()
        target_tool = None

        for tool in tools:
            if tool.name == tool_name:
                target_tool = tool
                break

        if not target_tool:
            logger.error(f"{ERROR_ICON} 未找到工具: {tool_name}")
            return None

        logger.info(f"{WAIT_ICON} 测试调用工具: {tool_name}")
        logger.info(f"参数: {tool_args}")

        # 调用工具
        result = await target_tool.ainvoke(tool_args)

        logger.info(f"{SUCCESS_ICON} 工具调用成功")
        logger.info(f"结果: {result}")

        return result

    except Exception as e:
        logger.error(f"{ERROR_ICON} 工具调用失败: {e}", exc_info=True)
        return None


async def close_mcp_client_sessions():
    """
    Closes any open sessions managed by the MultiServerMCPClient.
    This should be called on application shutdown if necessary.
    """
    global _mcp_client_instance
    if _mcp_client_instance:
        logger.info(f"{WAIT_ICON} Closing MCP client sessions...")
        try:
            logger.info(
                f"{SUCCESS_ICON} MCP client sessions (if any were persistently open) assumed closed or managed by library.")
            _mcp_client_instance = None  # Allow re-initialization
            global _mcp_tools
            _mcp_tools = None
        except Exception as e:
            logger.error(
                f"{ERROR_ICON} Error during MCP client session cleanup: {e}", exc_info=True)
    else:
        logger.info("MCP client was not initialized, no sessions to close.")


# Example of how to test this module (optional, for direct execution)
async def _main_test_mcp_client():
    logger.info("--- Testing MCP Client Tool Loading ---")
    tools = await get_mcp_tools()
    if tools:
        print(f"Successfully loaded {len(tools)} tools:")
        for tool in tools:
            print(
                f"- Name: {tool.name}, Description: {tool.description}")

        # 测试一个简单的工具调用（如果有合适的工具）
        if tools:
            logger.info("--- Testing Tool Call ---")
            # 尝试调用第一个工具（需要根据实际工具调整参数）
            first_tool = tools[0]
            logger.info(f"尝试调用工具: {first_tool.name}")

            # 这里需要根据实际的工具参数schema来构造测试参数
            # 暂时跳过实际调用，只是展示结构
            logger.info("工具调用测试跳过（需要实际参数）")
    else:
        print("Failed to load tools or no tools found.")

    # Test closing (if applicable)
    await close_mcp_client_sessions()
    logger.info("--- MCP Client Test Complete ---")

if __name__ == '__main__':
    # This allows running the test directly, e.g., python -m src.tools.mcp_client
    # Ensure your environment is set up (e.g., 'uv' command is available).
    # The a_share_mcp server at E:\github\a_share_mcp should be ready to be run.

    # Setup basic logging for the test run if not already configured
    if not logger.hasHandlers():
        import logging
        logging.basicConfig(level=logging.INFO)
        logger.info("Basic logging configured for test run.")

    asyncio.run(_main_test_mcp_client())
