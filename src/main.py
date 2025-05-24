from src.utils.logging_config import setup_logger, SUCCESS_ICON, ERROR_ICON, WAIT_ICON
from src.utils.state_definition import AgentState
from src.utils.execution_logger import initialize_execution_logger, finalize_execution_logger, get_execution_logger
from src.agents.summary_agent import summary_agent
from src.agents.value_agent import value_agent
from src.agents.technical_agent import technical_agent
from src.agents.fundamental_agent import fundamental_agent
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import argparse
import asyncio
import os
import sys
import re
from datetime import datetime


logger = setup_logger(__name__)
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


# Agent imports

# AgentState import

# Load environment variables
load_dotenv(override=True)

# Debug: 打印关键环境变量以验证配置
logger.info(f"Environment Variables Loaded:")
logger.info(
    f"  OPENAI_COMPATIBLE_MODEL: {os.getenv('OPENAI_COMPATIBLE_MODEL', 'Not Set')}")
logger.info(
    f"  OPENAI_COMPATIBLE_BASE_URL: {os.getenv('OPENAI_COMPATIBLE_BASE_URL', 'Not Set')}")
logger.info(
    f"  OPENAI_COMPATIBLE_API_KEY: {'*' * 20 if os.getenv('OPENAI_COMPATIBLE_API_KEY') else 'Not Set'}")

# Setup logger
logger = setup_logger(__name__)


async def main():
    # 初始化执行日志系统
    execution_logger = initialize_execution_logger()
    logger.info(
        f"{SUCCESS_ICON} 执行日志系统已初始化，日志目录: {execution_logger.execution_dir}")

    try:
        # 1. Define the LangGraph workflow (Step 15)
        workflow = StateGraph(AgentState)

        # Add a simple pass-through node to act as a clear starting point for parallel branches
        workflow.add_node("start_node", lambda state: state)

        # Add agent nodes
        workflow.add_node("fundamental_analyst", fundamental_agent)
        workflow.add_node("technical_analyst", technical_agent)
        workflow.add_node("value_analyst", value_agent)
        workflow.add_node("summarizer", summary_agent)

        # Set the entry point
        workflow.set_entry_point("start_node")

        # Edges for parallel execution of fundamental, technical, and value agents
        workflow.add_edge("start_node", "fundamental_analyst")
        workflow.add_edge("start_node", "technical_analyst")
        workflow.add_edge("start_node", "value_analyst")

        # Edges to converge the outputs into the summary agent
        # LangGraph will ensure "summarizer" waits for all its direct predecessors.
        workflow.add_edge("fundamental_analyst", "summarizer")
        workflow.add_edge("technical_analyst", "summarizer")
        workflow.add_edge("value_analyst", "summarizer")

        # Edge from the summary agent to the end of the workflow
        workflow.add_edge("summarizer", END)

        # Compile the workflow
        app = workflow.compile()

        # 2. Implement the command-line interface (Step 16)
        parser = argparse.ArgumentParser(description="Financial Agent CLI")
        parser.add_argument(
            "--command",
            type=str,
            required=False,  # 改为非必需
            help="The user query for financial analysis (e.g., '分析嘉友国际')"
        )
        args = parser.parse_args()

        # 如果未提供command参数，则提示用户输入查询
        if args.command:
            user_query = args.command
        else:
            # 显示ASCII艺术开屏图像
            print("\n")
            print(
                "╔══════════════════════════════════════════════════════════════════════════════╗")
            print(
                "║                                                                              ║")
            print(
                "║      ███████╗██╗███╗   ██╗ █████╗ ███╗   ██╗ ██████╗██╗ █████╗ ██╗          ║")
            print(
                "║      ██╔════╝██║████╗  ██║██╔══██╗████╗  ██║██╔════╝██║██╔══██╗██║          ║")
            print(
                "║      █████╗  ██║██╔██╗ ██║███████║██╔██╗ ██║██║     ██║███████║██║          ║")
            print(
                "║      ██╔══╝  ██║██║╚██╗██║██╔══██║██║╚██╗██║██║     ██║██╔══██║██║          ║")
            print(
                "║      ██║     ██║██║ ╚████║██║  ██║██║ ╚████║╚██████╗██║██║  ██║███████╗      ║")
            print(
                "║      ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚═╝╚═╝  ╚═╝╚══════╝      ║")
            print(
                "║                                                                              ║")
            print(
                "║                █████╗  ██████╗ ███████╗███╗   ██╗████████╗                  ║")
            print(
                "║               ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝                  ║")
            print(
                "║               ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║                     ║")
            print(
                "║               ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║                     ║")
            print(
                "║               ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║                     ║")
            print(
                "║               ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝                     ║")
            print(
                "║                                                                              ║")
            print("║                          🏦 金融分析智能体系统                              ║")
            print(
                "║                     Financial Analysis AI Agent System                      ║")
            print(
                "║                                                                              ║")
            print(
                "║    ┌─────────────────────────────────────────────────────────────────┐     ║")
            print("║    │  📊 基本面分析  │  📈 技术分析  │  💰 估值分析  │  🤖 智能总结  │     ║")
            print(
                "║    └─────────────────────────────────────────────────────────────────┘     ║")
            print(
                "║                                                                              ║")
            print(
                "╚══════════════════════════════════════════════════════════════════════════════╝")
            print("\n🔹 本系统可以对A股公司进行全面分析，包括：")
            print("  • 基本面分析 - 财务状况、盈利能力和行业地位")
            print("  • 技术面分析 - 价格趋势、交易量和技术指标")
            print("  • 估值分析 - 市盈率、市净率等估值水平")
            print("\n🔹 支持多种自然语言查询方式：")
            print("  • 分析嘉友国际")
            print("  • 帮我看看比亚迪这只股票怎么样")
            print("  • 我想了解一下腾讯的投资价值")
            print("  • 603871 这个股票值得买吗？")
            print("  • 给我分析一下宁德时代的财务状况")
            print("\n🔹 您可以用任何自然语言描述您的分析需求")
            print("🔹 系统会自动识别股票名称和代码，并进行全面分析")
            print("\n💡 提示：建议使用股票代码（如 000001、600036）以获得更准确的分析结果")
            print("\n" + "─" * 78 + "\n")

            user_query = input("💬 请输入您的分析需求: ")

            # 确保输入不为空
            while not user_query.strip():
                print(f"{ERROR_ICON} 输入不能为空，请重新输入！")
                user_query = input("请输入您的分析需求: ")

        # 记录用户查询
        execution_logger.log_agent_start("main", {"user_query": user_query})

        # 从查询中提取股票代码和公司名称
        stock_code = None
        company_name = None

        # 简单的提取逻辑 - 假设查询格式为"分析[公司名称]"或包含股票代码
        if "分析" in user_query:
            # 尝试提取公司名称
            parts = user_query.split("分析")
            if len(parts) > 1 and parts[1].strip():
                company_name = parts[1].strip()

                # 如果公司名称包含股票代码（如括号内的数字），则提取
                code_match = re.search(r'[（(](\d{6})[)）]', company_name)
                if code_match:
                    stock_code = code_match.group(1)
                    # 从公司名称中移除股票代码部分
                    company_name = re.sub(
                        r'[（(]\d{6}[)）]', '', company_name).strip()

        # 如果未提取到股票代码但查询中包含6位数字，则可能是股票代码
        if not stock_code:
            code_match = re.search(r'\b(\d{6})\b', user_query)
            if code_match:
                stock_code = code_match.group(1)

        # 记录提取结果
        logger.info(f"从查询中提取 - 公司名称: {company_name}, 股票代码: {stock_code}")

        # 获取当前时间信息
        current_datetime = datetime.now()
        current_date_cn = current_datetime.strftime("%Y年%m月%d日")
        current_date_en = current_datetime.strftime("%Y-%m-%d")
        current_weekday_cn = ["星期一", "星期二", "星期三", "星期四",
                              "星期五", "星期六", "星期日"][current_datetime.weekday()]
        current_time = current_datetime.strftime("%H:%M:%S")

        # 格式化完整的时间信息
        current_time_info = f"{current_date_cn} ({current_date_en}) {current_weekday_cn} {current_time}"

        logger.info(f"当前时间: {current_time_info}")

        # 准备初始状态
        initial_data = {
            "query": user_query,
            "current_date": current_date_en,
            "current_date_cn": current_date_cn,
            "current_time": current_time,
            "current_weekday_cn": current_weekday_cn,
            "current_time_info": current_time_info,
            "analysis_timestamp": current_datetime.isoformat()
        }
        if company_name:
            initial_data["company_name"] = company_name
        if stock_code:
            # 添加股票代码前缀（上交所或深交所）
            if stock_code.startswith('6'):
                initial_data["stock_code"] = f"sh.{stock_code}"
            elif stock_code.startswith('0') or stock_code.startswith('3'):
                initial_data["stock_code"] = f"sz.{stock_code}"
            else:
                initial_data["stock_code"] = stock_code

        # Prepare the initial state for the workflow
        initial_state = AgentState(
            messages=[],  # Langchain convention
            data=initial_data,  # Application-specific data with extracted info
            metadata={}  # For any other run-specific info
        )

        print(f"\n{WAIT_ICON} 正在开始对 '{user_query}' 进行金融分析...")
        if company_name:
            print(f"{WAIT_ICON} 分析公司: {company_name}")
        if stock_code:
            print(f"{WAIT_ICON} 股票代码: {stock_code}")
        logger.info(
            f"Starting financial analysis workflow for query: '{user_query}'")

        # 显示分析阶段提示
        print(f"\n{WAIT_ICON} 正在执行基本面分析...")
        print(f"{WAIT_ICON} 正在执行技术面分析...")
        print(f"{WAIT_ICON} 正在执行估值分析...")
        print(f"{WAIT_ICON} 这可能需要几分钟时间，请耐心等待...\n")

        # Invoke the workflow. This is a blocking call.
        final_state = await app.ainvoke(initial_state)
        print(f"{SUCCESS_ICON} 分析完成！")
        logger.info("Workflow execution completed successfully")

        # Extract and print the final report
        if final_state and final_state.get("data") and "final_report" in final_state["data"]:
            print("\n--- 最终分析报告 (Final Analysis Report) ---\n")
            print(final_state["data"]["final_report"])

            # Display the report file path if available
            if "report_path" in final_state["data"]:
                print(
                    f"\n{SUCCESS_ICON} 报告已保存到: {final_state['data']['report_path']}")
                logger.info(
                    f"Report saved to: {final_state['data']['report_path']}")

                # 记录最终报告到执行日志
                execution_logger.log_final_report(
                    final_state["data"]["final_report"],
                    final_state["data"]["report_path"]
                )
        else:
            print(f"\n{ERROR_ICON} 错误: 无法从工作流中检索最终报告。")
            logger.error(
                "Could not retrieve the final report from the workflow")
            print("调试信息 - 最终状态内容:", final_state)

        # 完成执行日志记录
        finalize_execution_logger(success=True)
        print(f"{SUCCESS_ICON} 执行日志已保存到: {execution_logger.execution_dir}")

    except Exception as e:
        print(f"\n{ERROR_ICON} 工作流执行期间发生错误: {e}")
        logger.error(f"Error during workflow execution: {e}", exc_info=True)

        # 记录错误并完成执行日志
        finalize_execution_logger(success=False, error=str(e))
        print(f"{ERROR_ICON} 错误日志已保存到: {get_execution_logger().execution_dir}")


async def test_chain_agents():
    """Test function for running the agent chain directly"""
    from src.utils.state_definition import AgentState

    # Sample test query
    test_query = "分析嘉友国际"

    # Initialize state
    initial_state = AgentState(
        messages=[],
        data={"query": test_query},
        metadata={}
    )

    # Execute fundamental agent
    print(f"{WAIT_ICON} Running fundamental agent...")
    fund_result = await fundamental_agent(initial_state)

    # Execute technical agent
    print(f"{WAIT_ICON} Running technical agent...")
    tech_result = await technical_agent(initial_state)

    # Execute value agent
    print(f"{WAIT_ICON} Running value agent...")
    value_result = await value_agent(initial_state)

    # Merge results
    merged_data = {
        **initial_state.get("data", {}),
        **fund_result.get("data", {}),
        **tech_result.get("data", {}),
        **value_result.get("data", {})
    }

    merged_state = AgentState(
        messages=[],
        data=merged_data,
        metadata={}
    )

    # Execute summary agent
    print(f"{WAIT_ICON} Running summary agent...")
    summary_result = await summary_agent(merged_state)

    # Print the final report
    if "final_report" in summary_result.get("data", {}):
        print("\n--- 最终分析报告 (Final Analysis Report) ---\n")
        print(summary_result["data"]["final_report"])

        # Display the report file path if available
        if "report_path" in summary_result["data"]:
            print(
                f"\n{SUCCESS_ICON} 报告已保存到: {summary_result['data']['report_path']}")
    else:
        print(f"\n{ERROR_ICON} 无法生成最终报告")

    return summary_result


if __name__ == "__main__":
    asyncio.run(main())
