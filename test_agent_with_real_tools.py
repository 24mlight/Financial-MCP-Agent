"""
测试修正后的technical_agent是否能正确调用工具
"""
from dotenv import load_dotenv
from src.utils.execution_logger import initialize_execution_logger, finalize_execution_logger
from src.utils.logging_config import setup_logger
from src.utils.state_definition import AgentState
from src.agents.technical_agent import technical_agent
import asyncio
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


# 加载环境变量
load_dotenv(override=True)

logger = setup_logger(__name__)


async def test_technical_agent_with_tools():
    """测试technical_agent是否能正确调用工具"""

    # 初始化执行日志系统
    execution_logger = initialize_execution_logger()

    try:
        # 准备测试数据 - 模拟main.py中的时间信息设置
        current_datetime = datetime.now()
        current_date_cn = current_datetime.strftime("%Y年%m月%d日")
        current_date_en = current_datetime.strftime("%Y-%m-%d")
        current_weekday_cn = ["星期一", "星期二", "星期三", "星期四",
                              "星期五", "星期六", "星期日"][current_datetime.weekday()]
        current_time = current_datetime.strftime("%H:%M:%S")
        current_time_info = f"{current_date_cn} ({current_date_en}) {current_weekday_cn} {current_time}"

        print(f"当前时间: {current_time_info}")

        # 准备测试状态
        test_state = AgentState(
            messages=[],
            data={
                "query": "分析嘉友国际 603871的技术指标",
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

        print("开始测试technical_agent...")
        print(f"测试查询: {test_state['data']['query']}")
        print(f"股票代码: {test_state['data']['stock_code']}")
        print(f"公司名称: {test_state['data']['company_name']}")

        # 运行technical_agent
        result = await technical_agent(test_state)

        print("\n=== 测试结果 ===")

        # 检查是否有技术分析结果
        if "technical_analysis" in result.get("data", {}):
            analysis = result["data"]["technical_analysis"]
            print(f"✅ 技术分析成功生成，长度: {len(analysis)} 字符")
            print(f"分析预览: {analysis[:200]}...")

            if len(analysis) > 100:  # 如果分析内容足够长，说明可能成功调用了工具
                print("✅ 分析内容充实，可能成功调用了工具")
            else:
                print("⚠️ 分析内容较短，可能未成功调用工具")
        else:
            print("❌ 未生成技术分析结果")

        # 检查是否有错误
        if "technical_analysis_error" in result.get("data", {}):
            error = result["data"]["technical_analysis_error"]
            print(f"❌ 技术分析错误: {error}")

        # 检查元数据
        metadata = result.get("metadata", {})
        if "technical_agent_executed" in metadata:
            print(f"✅ Agent执行状态: {metadata['technical_agent_executed']}")
        if "technical_agent_execution_time" in metadata:
            print(f"⏱️ 执行时间: {metadata['technical_agent_execution_time']}")

        # 完成执行日志记录
        finalize_execution_logger(success=True)
        print(f"📝 执行日志已保存到: {execution_logger.execution_dir}")

        return result

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        finalize_execution_logger(success=False, error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(test_technical_agent_with_tools())
