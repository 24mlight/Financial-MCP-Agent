"""
TechnicalAnalysis Agent: Performs technical analysis of a stock using ReAct Agent framework.
"""
import os
import json
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
import time

from src.utils.state_definition import AgentState
from src.tools.mcp_client import get_mcp_tools
from src.utils.logging_config import setup_logger, ERROR_ICON, SUCCESS_ICON, WAIT_ICON
from src.utils.execution_logger import get_execution_logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

logger = setup_logger(__name__)


async def technical_agent(state: AgentState) -> AgentState:
    """
    Performs technical analysis using direct MCP integration with standard ReAct format.

    Args:
        state: The current agent state containing user query

    Returns:
        Updated AgentState with technical analysis results
    """
    logger.info(f"{WAIT_ICON} TechnicalAgent: Starting technical analysis using ReAct framework.")

    # 获取执行日志记录器
    execution_logger = get_execution_logger()
    agent_name = "technical_agent"

    current_data = state.get("data", {})
    current_messages = state.get("messages", [])
    current_metadata = state.get("metadata", {})
    user_query = current_data.get("query")

    # 记录agent开始执行
    execution_logger.log_agent_start(agent_name, {
        "user_query": user_query,
        "stock_code": current_data.get("stock_code"),
        "company_name": current_data.get("company_name"),
        "input_data_keys": list(current_data.keys())
    })

    if not user_query:
        logger.error(f"{ERROR_ICON} TechnicalAgent: User query is missing in state data.")
        current_data["technical_analysis_error"] = "User query is missing."
        execution_logger.log_agent_complete(agent_name, current_data, 0, False, "User query is missing")
        return {"data": current_data, "messages": current_messages, "metadata": current_metadata}

    agent_start_time = time.time()

    try:
        # 1. Create ChatOpenAI model using environment variables
        api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")
        base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL")
        model_name = os.getenv("OPENAI_COMPATIBLE_MODEL")

        if not all([api_key, base_url, model_name]):
            logger.error(f"{ERROR_ICON} TechnicalAgent: Missing OpenAI environment variables.")
            current_data["technical_analysis_error"] = "Missing OpenAI environment variables."
            execution_logger.log_agent_complete(agent_name, current_data, time.time() - agent_start_time, False, "Missing OpenAI environment variables")
            return {"data": current_data, "messages": current_messages, "metadata": current_metadata}

        logger.info(f"{WAIT_ICON} TechnicalAgent: Creating ChatOpenAI with model {model_name}")
        llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.3,
            max_tokens=3000
        )

        # 2. 获取MCP工具
        logger.info(f"{WAIT_ICON} TechnicalAgent: Fetching MCP tools...")
        try:
            mcp_tools = await get_mcp_tools()
            if not mcp_tools:
                logger.error(f"{ERROR_ICON} TechnicalAgent: No MCP tools available.")
                current_data["technical_analysis_error"] = "No MCP tools available."
                execution_logger.log_agent_complete(agent_name, current_data, time.time() - agent_start_time, False, "No MCP tools available")
                return {"data": current_data, "messages": current_messages, "metadata": current_metadata}

            logger.info(f"{SUCCESS_ICON} TechnicalAgent: Successfully loaded {len(mcp_tools)} tools.")

            # 打印可用工具列表
            tool_names = [tool.name for tool in mcp_tools]
            logger.info(f"Available tools: {tool_names}")

            # 3. 创建ReAct agent - 只传入LLM和工具
            logger.info(f"{WAIT_ICON} TechnicalAgent: Creating ReAct agent...")
            agent = create_react_agent(llm, mcp_tools)

            # 4. 准备输入数据
            stock_code = current_data.get('stock_code', 'Unknown')
            company_name = current_data.get('company_name', 'Unknown')
            current_time_info = current_data.get('current_time_info', '未知时间')
            current_date = current_data.get('current_date', '未知日期')
            
            # 构建详细的分析请求
            agent_input = f"""请分析{company_name}（股票代码：{stock_code}）的技术指标。

当前时间：{current_time_info}
当前日期：{current_date}

请进行以下技术分析：
1. 获取股票基本信息和最新价格
2. 获取历史K线数据（建议获取最近3-6个月的数据）
3. 分析价格趋势和技术形态
4. 分析成交量变化
5. 计算和分析主要技术指标（如移动平均线、MACD、RSI等）
6. 识别支撑位和阻力位
7. 提供技术面总结和短期走势判断

请使用可用的工具获取实际数据进行分析，而不是基于假设。"""

            logger.info(f"Agent input: {agent_input}")

            # 5. 调用ReAct agent - 使用正确的messages格式
            logger.info(f"{WAIT_ICON} TechnicalAgent: Calling ReAct agent...")
            start_time = time.time()

            # LangGraph ReAct agent需要messages格式
            input_data = {
                "messages": [HumanMessage(content=agent_input)]
            }

            # 调用agent
            response = await agent.ainvoke(input_data)

            end_time = time.time()
            execution_time = end_time - start_time

            logger.info(f"ReAct agent execution completed in {execution_time:.2f} seconds")

            # 6. 提取结果
            final_output = "No analysis generated."
            
            if "messages" in response and isinstance(response["messages"], list):
                messages = response["messages"]
                # 查找最后一条AI消息
                ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
                if ai_messages:
                    last_ai_message = ai_messages[-1]
                    final_output = last_ai_message.content
                    logger.info(f"Extracted analysis from AI message: {final_output[:100]}...")
                else:
                    logger.warning("No AI messages found in response")
                    # 如果没有AI消息，尝试获取所有消息的内容
                    all_content = []
                    for msg in messages:
                        if hasattr(msg, 'content') and msg.content:
                            all_content.append(str(msg.content))
                    if all_content:
                        final_output = "\n".join(all_content)
            else:
                logger.error(f"Unexpected response format: {type(response)}")
                logger.error(f"Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")

            logger.info(f"Final extracted analysis length: {len(final_output)} characters")

            # 7. 记录LLM交互
            execution_logger.log_llm_interaction(
                agent_name=agent_name,
                interaction_type="react_agent",
                input_messages=[{"role": "user", "content": agent_input}],
                output_content=final_output,
                model_config={
                    "model": model_name,
                    "temperature": 0.3,
                    "max_tokens": 3000,
                    "api_base": base_url
                },
                execution_time=execution_time
            )

            logger.info(f"{SUCCESS_ICON} TechnicalAgent: Successfully completed technical analysis.")

            # 8. 更新状态
            current_data["technical_analysis"] = final_output
            current_metadata["technical_agent_executed"] = True
            current_metadata["technical_agent_timestamp"] = str(time.time())
            current_metadata["technical_agent_execution_time"] = f"{execution_time:.2f} seconds"

            # 9. 添加消息记录
            new_message = {"role": "assistant", "content": "技术分析已完成"}
            updated_messages = current_messages + [new_message]

            # 记录agent执行成功
            total_execution_time = time.time() - agent_start_time
            execution_logger.log_agent_complete(agent_name, {
                "technical_analysis_length": len(final_output),
                "analysis_preview": final_output[:500] if len(final_output) > 500 else final_output,
                "llm_execution_time": execution_time,
                "total_execution_time": total_execution_time
            }, total_execution_time, True)

            return {
                "data": current_data,
                "messages": updated_messages,
                "metadata": current_metadata
            }

        except Exception as e:
            logger.error(f"{ERROR_ICON} TechnicalAgent: Error in MCP or agent execution: {e}", exc_info=True)
            current_data["technical_analysis_error"] = f"Error in MCP or agent execution: {e}"
            current_data["technical_analysis"] = f"技术分析过程中出现错误: {str(e)}"
            current_metadata["technical_agent_error"] = str(e)
            execution_logger.log_agent_complete(agent_name, current_data, time.time() - agent_start_time, False, str(e))
            return {"data": current_data, "messages": current_messages, "metadata": current_metadata}

    except Exception as e:
        logger.error(f"{ERROR_ICON} TechnicalAgent: Error during execution: {e}", exc_info=True)
        current_data["technical_analysis_error"] = f"Error during execution: {e}"
        current_metadata["technical_agent_error"] = str(e)
        execution_logger.log_agent_complete(agent_name, current_data, time.time() - agent_start_time, False, str(e))
        return {"data": current_data, "messages": current_messages, "metadata": current_metadata}


# For local testing
async def test_technical_agent():
    """Test function for the technical agent"""
    from src.utils.state_definition import AgentState
    from datetime import datetime

    # 准备测试数据
    current_datetime = datetime.now()
    current_date_cn = current_datetime.strftime("%Y年%m月%d日")
    current_date_en = current_datetime.strftime("%Y-%m-%d")
    current_weekday_cn = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][current_datetime.weekday()]
    current_time = current_datetime.strftime("%H:%M:%S")
    current_time_info = f"{current_date_cn} ({current_date_en}) {current_weekday_cn} {current_time}"

    test_state = AgentState(
        messages=[],
        data={
            "query": "分析嘉友国际的技术指标",
            "stock_code": "sh.603871",
            "company_name": "嘉友国际",
            "current_date": current_date_en,
            "current_date_cn": current_date_cn,
            "current_time": current_time,
            "current_weekday_cn": current_weekday_cn,
            "current_time_info": current_time_info,
            "analysis_timestamp": current_datetime.isoformat()
        },
        metadata={}
    )

    # Run the agent
    result = await technical_agent(test_state)
    print("Technical Analysis Result:")
    print(result.get("data", {}).get("technical_analysis", "No analysis found"))

    return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_technical_agent()) 