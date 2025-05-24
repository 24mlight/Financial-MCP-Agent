"""
Summary Agent: Consolidates analyses from other agents into a final report.
"""
import os
import time
from typing import Dict, Any
from langchain_openai import ChatOpenAI

from src.utils.state_definition import AgentState
from src.utils.logging_config import setup_logger, ERROR_ICON, SUCCESS_ICON, WAIT_ICON
from src.utils.execution_logger import get_execution_logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

logger = setup_logger(__name__)


async def summary_agent(state: AgentState) -> Dict[str, Any]:
    """
    Consolidates analyses from fundamental, technical, and value agents.
    Uses LLM to generate a final comprehensive report.
    """
    logger.info(f"{WAIT_ICON} SummaryAgent: Starting to consolidate analyses.")

    # 获取执行日志记录器
    execution_logger = get_execution_logger()
    agent_name = "summary_agent"

    current_data = state.get("data", {})
    messages = state.get("messages", [])
    user_query = current_data.get("query", "")

    # 记录agent开始执行
    execution_logger.log_agent_start(agent_name, {
        "user_query": user_query,
        "available_analyses": {
            "fundamental": "fundamental_analysis" in current_data,
            "technical": "technical_analysis" in current_data,
            "value": "value_analysis" in current_data
        },
        "input_data_keys": list(current_data.keys())
    })

    agent_start_time = time.time()

    # Get analyses from previous agents
    fundamental_analysis = current_data.get(
        "fundamental_analysis", "Not available")
    technical_analysis = current_data.get(
        "technical_analysis", "Not available")
    value_analysis = current_data.get("value_analysis", "Not available")

    # Error handling for individual analyses
    errors = []
    if "fundamental_analysis_error" in current_data:
        errors.append(
            f"Fundamental Analysis Error: {current_data['fundamental_analysis_error']}")
    if "technical_analysis_error" in current_data:
        errors.append(
            f"Technical Analysis Error: {current_data['technical_analysis_error']}")
    if "value_analysis_error" in current_data:
        errors.append(
            f"Value Analysis Error: {current_data['value_analysis_error']}")

    # Basic stock identifier
    stock_code = current_data.get("stock_code", "Unknown Stock")
    company_name = current_data.get("company_name", "Unknown Company")

    try:
        # Create OpenAI model (we're using direct API calls, not ReAct framework for summarization)
        api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")
        base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL")
        model_name = os.getenv("OPENAI_COMPATIBLE_MODEL")

        if not all([api_key, base_url, model_name]):
            logger.error(
                f"{ERROR_ICON} SummaryAgent: Missing OpenAI environment variables.")
            current_data["summary_error"] = "Missing OpenAI environment variables."

            # 记录agent执行失败
            execution_logger.log_agent_complete(agent_name, current_data, time.time(
            ) - agent_start_time, False, "Missing OpenAI environment variables")

            return {"data": current_data, "messages": messages}

            # 获取当前时间信息
        current_time_info = current_data.get("current_time_info", "未知时间")
        current_date = current_data.get("current_date", "未知日期")

        # Prepare the system prompt for summarization
        system_prompt = f"""
        你是一个专业金融分析师，负责创建全面、深入的股票分析报告。
        
        **重要时间信息：当前实际时间是 {current_time_info}**
        **分析基准日期：{current_date}**
        
        这是真实的当前时间，不是你的训练数据截止时间。请在生成报告时：
        - 基于实际当前时间来判断数据的时效性
        - 正确标注"最新"、"近期"、"历史"等时间概念
        - 在报告中明确标注分析的时间基准点为：{current_date}
        - 所有时间相关的描述都要基于这个实际日期
        
        你的任务是综合三种不同的分析结果：
        1. 基本面分析 - 关注财务报表、商业模式和公司基本面
        2. 技术分析 - 关注价格趋势、交易量模式和技术指标
        3. 估值分析 - 关注估值指标和相对价值

        请创建一份结构清晰、内容连贯的报告，整合所有三种分析的见解。
        即使某些分析数据不完整或缺失，也请基于可用信息提供最佳的综合分析。

        报告应包含以下部分：
        
        # [公司名称]([股票代码]) 综合分析报告
        
        ## 执行摘要
        [提供简明扼要的总体分析和投资建议，包括风险等级和预期回报]
        
        ## 公司概况
        [简要介绍公司的业务、行业地位、主要产品或服务]
        
        ## 基本面分析
        [详细分析公司财务状况、盈利能力、成长性、资产负债情况等]
        
        ## 技术分析
        [详细分析价格趋势、技术指标、支撑位和阻力位、交易量等]
        
        ## 估值分析
        [详细分析估值指标、与行业平均水平比较、历史估值水平、股息收益率等]
        
        ## 综合评估
        [分析不同分析方法之间的一致点和分歧点，提供更全面的投资视角]
        
        ## 风险因素
        [详细分析潜在的风险因素，包括市场风险、行业风险、公司特定风险等]
        
        ## 投资建议
        [提供明确的投资建议，包括目标价格、投资时间范围、适合的投资者类型等]
        
        ## 附录：数据来源与限制
        [说明数据来源，以及分析过程中遇到的任何数据限制或缺失]

        输出必须是有效的Markdown格式，使用适当的标题、项目符号和格式。
        不要包含任何代码块标记，如```markdown或```，直接输出纯Markdown内容。
        
        使用专业的金融语言，但保持可读性。报告应该全面且深入，包含足够的细节和数据支持，
        同时聚焦于最重要的见解，帮助投资者做出决策。
        
        **重要提醒：**
        - 请在报告末尾明确标注分析基准时间：{current_time_info}
        - 基于这个实际时间来判断所有数据的时效性
        - 避免使用模糊的时间概念，要基于实际当前时间进行判断
        
        如果某些分析数据不完整或有错误，请在报告中明确说明，并尽可能基于可用信息提供有价值的分析。
        """

        # Prepare the summary prompt
        summary_prompt_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
            Please create a comprehensive analysis report for {company_name} ({stock_code}) based on the following analyses.
            
            Original user query: {user_query}
            
            FUNDAMENTAL ANALYSIS:
            {fundamental_analysis}
            
            TECHNICAL ANALYSIS:
            {technical_analysis}
            
            VALUE ANALYSIS:
            {value_analysis}
            
            {"ANALYSIS ISSUES:" if errors else ""}
            {". ".join(errors) if errors else ""}
            
            IMPORTANT: Your output MUST be in valid Markdown format with proper headings, bullet points, 
            and formatting. Include a clear recommendation section at the end.
            
            DO NOT include any code block markers like ```markdown or ``` in your output.
            Just write pure Markdown content directly.
            """}
        ]

        logger.info(
            f"{WAIT_ICON} SummaryAgent: Generating final report using LLM for {company_name} ({stock_code})...")

        # 记录模型配置
        model_config = {
            "model": model_name,
            "temperature": 0.5,
            "max_tokens": 10000,
            "api_base": base_url
        }

        # Use either the ChatOpenAI model or the existing get_chat_completion utility
        # Option 1: Using ChatOpenAI
        llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.5,  # 提高温度以增加创造性和更自然的表达
            max_tokens=10000   # 增大输出长度以生成更详细的综合报告
        )

        # 记录LLM交互开始时间
        llm_start_time = time.time()

        llm_message = await llm.ainvoke(summary_prompt_messages)
        final_report = llm_message.content

        # 记录LLM交互执行时间
        llm_execution_time = time.time() - llm_start_time

        # 记录LLM交互详情
        execution_logger.log_llm_interaction(
            agent_name=agent_name,
            interaction_type="summary_generation",
            input_messages=summary_prompt_messages,
            output_content=final_report,
            model_config=model_config,
            execution_time=llm_execution_time
        )

        # Remove any markdown code block markers if they still appear
        final_report = final_report.replace(
            "```markdown", "").replace("```", "").strip()

        # Option 2: Using existing get_chat_completion (alternative approach)
        # final_report = await get_chat_completion(messages=summary_prompt_messages)

        logger.info(
            f"{SUCCESS_ICON} SummaryAgent: Final report generated for {company_name} ({stock_code}).")
        logger.debug(f"Final report preview: {final_report[:300]}...")

        # Save the report to a Markdown file
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # 处理公司名称和股票代码，确保文件名有意义
        if stock_code == "Unknown Stock" or stock_code == "Extracted from analysis":
            # 从用户查询中提取更有意义的名称
            query_based_name = user_query.replace(
                " ", "_").replace("分析", "").strip()
            if not query_based_name:
                query_based_name = "financial_analysis"
            safe_file_prefix = f"report_{query_based_name}"
        else:
            # 正常情况下使用公司名称和股票代码
            safe_company_name = company_name.replace(" ", "_").replace(".", "")
            if safe_company_name == "Unknown_Company" or safe_company_name == "Extracted_from_analysis":
                safe_company_name = user_query.replace(
                    " ", "_").replace("分析", "").strip()
                if not safe_company_name:
                    safe_company_name = "company"

            # 清理股票代码（移除可能的前缀）
            clean_stock_code = stock_code.replace("sh.", "").replace("sz.", "")
            safe_file_prefix = f"report_{safe_company_name}_{clean_stock_code}"

        report_filename = f"{safe_file_prefix}_{timestamp}.md"

        # Ensure the reports directory exists
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), "reports")
        os.makedirs(reports_dir, exist_ok=True)

        report_path = os.path.join(reports_dir, report_filename)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(final_report)

        logger.info(
            f"{SUCCESS_ICON} SummaryAgent: Report saved to {report_path}")

        # Return the updated state with the final report
        current_data["final_report"] = final_report
        current_data["report_path"] = report_path

        # 记录agent执行成功
        total_execution_time = time.time() - agent_start_time
        execution_logger.log_agent_complete(agent_name, {
            "final_report_length": len(final_report),
            "report_path": report_path,
            "report_preview": final_report,
            "llm_execution_time": llm_execution_time,
            "total_execution_time": total_execution_time
        }, total_execution_time, True)

        return {"data": current_data, "messages": messages}

    except Exception as e:
        logger.error(
            f"{ERROR_ICON} SummaryAgent: Error generating final report: {e}", exc_info=True)
        current_data["summary_error"] = f"Error generating final report: {e}"

        # Create a minimal report even if there was an error
        error_report = f"""
        # Analysis Report for {company_name} ({stock_code})
        
        **Error encountered during report generation**: {e}
        
        ## Available Analysis Fragments:
        
        - Fundamental Analysis: {"Available" if fundamental_analysis != "Not available" else "Not available"}
        - Technical Analysis: {"Available" if technical_analysis != "Not available" else "Not available"}
        - Value Analysis: {"Available" if value_analysis != "Not available" else "Not available"}
        
        Please review the individual analyses directly for more information.
        """
        current_data["final_report"] = error_report

        # Save the error report to a file as well
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # 处理公司名称和股票代码，确保文件名有意义
        if stock_code == "Unknown Stock" or stock_code == "Extracted from analysis":
            # 从用户查询中提取更有意义的名称
            query_based_name = user_query.replace(
                " ", "_").replace("分析", "").strip()
            if not query_based_name:
                query_based_name = "financial_analysis"
            safe_file_prefix = f"error_report_{query_based_name}"
        else:
            # 正常情况下使用公司名称和股票代码
            safe_company_name = company_name.replace(" ", "_").replace(".", "")
            if safe_company_name == "Unknown_Company" or safe_company_name == "Extracted_from_analysis":
                safe_company_name = user_query.replace(
                    " ", "_").replace("分析", "").strip()
                if not safe_company_name:
                    safe_company_name = "company"

            # 清理股票代码（移除可能的前缀）
            clean_stock_code = stock_code.replace("sh.", "").replace("sz.", "")
            safe_file_prefix = f"error_report_{safe_company_name}_{clean_stock_code}"

        report_filename = f"{safe_file_prefix}_{timestamp}.md"

        # Ensure the reports directory exists
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), "reports")
        os.makedirs(reports_dir, exist_ok=True)

        report_path = os.path.join(reports_dir, report_filename)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(error_report)

        logger.info(
            f"{ERROR_ICON} SummaryAgent: Error report saved to {report_path}")
        current_data["report_path"] = report_path

        # 记录agent执行失败
        execution_logger.log_agent_complete(
            agent_name, current_data, time.time() - agent_start_time, False, str(e))

        return {"data": current_data, "messages": messages}


# For local testing
async def test_summary_agent():
    """Test function for the summary agent"""
    from src.utils.state_definition import AgentState

    # Sample state for testing with mock analyses
    test_state = AgentState(
        messages=[],
        data={
            "query": "分析嘉友国际",
            "stock_code": "603871",
            "company_name": "嘉友国际",
            "fundamental_analysis": "嘉友国际基本面分析：公司主营业务为跨境物流、供应链贸易以及供应链增值服务。财务状况良好，负债率较低，现金流充裕。近年来业绩稳步增长，毛利率保持在行业较高水平。",
            "technical_analysis": "嘉友国际技术分析：短期内股价处于上升通道，突破了200日均线。RSI指标显示股票尚未达到超买区域。MACD指标呈现多头形态，成交量有所放大，支持价格继续上行。",
            "value_analysis": "嘉友国际估值分析：当前市盈率为15倍，低于行业平均水平。市净率为1.8倍，处于合理区间。与同行业公司相比，嘉友国际的估值较为合理，具有一定的投资价值。"
        },
        metadata={}
    )

    # Run the agent
    result = await summary_agent(test_state)
    print("Summary Report:")
    print(result.get("data", {}).get("final_report", "No report generated"))
    print(
        f"Report saved to: {result.get('data', {}).get('report_path', 'Not saved')}")

    return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_summary_agent())
