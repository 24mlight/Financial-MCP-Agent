import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.agents.summary_agent import summary_agent
from src.utils.state_definition import AgentState


@pytest.fixture
def mock_llm_client_summary():
    llm_client = AsyncMock()
    message = MagicMock()
    message.content = "综合报告：平安银行基本面良好，技术面看涨，估值合理。建议关注。"
    llm_client.ainvoke.return_value = message
    return llm_client


@pytest.mark.asyncio
async def test_summary_agent_success(mock_llm_client_summary):
    """Test summary_agent successfully generates a final report."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析平安银行",
            "stock_code": "000001",
            "stock_name": "平安银行",
            "fundamental_analysis": {"summary": "基本面良好", "details": "..."},
            "technical_analysis": {"summary": "技术面看涨", "details": "..."},
            "value_analysis": {"summary": "估值合理", "details": "..."}
        },
        metadata={}
    )

    with patch('src.agents.summary_agent.ChatOpenAI', return_value=mock_llm_client_summary):
        result_state = await summary_agent(initial_state)

    assert "final_report" in result_state["data"]
    assert "平安银行" in result_state["data"]["final_report"]
    assert "基本面良好" in result_state["data"]["final_report"]
    assert "技术面看涨" in result_state["data"]["final_report"]
    assert "估值合理" in result_state["data"]["final_report"]
    assert "建议关注" in result_state["data"]["final_report"]
    assert "summary_error" not in result_state["data"]


@pytest.mark.asyncio
async def test_summary_agent_missing_analysis(mock_llm_client_summary):
    """Test summary_agent when some analyses are missing."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析平安银行",
            "stock_code": "000001",
            "stock_name": "平安银行",
            "fundamental_analysis": {"summary": "基本面良好", "details": "..."},
            "technical_analysis": None,  # 技术分析缺失
            "value_analysis": {"summary": "估值合理", "details": "..."}
        },
        metadata={}
    )

    message = MagicMock()
    message.content = "综合报告（部分数据缺失）：平安银行基本面良好，估值合理。"
    mock_llm_client_summary.ainvoke.return_value = message

    with patch('src.agents.summary_agent.ChatOpenAI', return_value=mock_llm_client_summary):
        result_state = await summary_agent(initial_state)

    assert "final_report" in result_state["data"]
    assert "部分数据缺失" in result_state["data"]["final_report"]
    assert "summary_error" not in result_state["data"]


@pytest.mark.asyncio
async def test_summary_agent_environment_variables_missing():
    """Test summary_agent when environment variables are missing."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析平安银行",
            "stock_code": "000001",
            "stock_name": "平安银行",
            "fundamental_analysis": {"summary": "基本面良好"},
            "technical_analysis": {"summary": "技术面看涨"},
            "value_analysis": {"summary": "估值合理"}
        },
        metadata={}
    )

    with patch('src.agents.summary_agent.os.getenv', return_value=None):
        result_state = await summary_agent(initial_state)

        assert "final_report" not in result_state["data"]
        assert "summary_error" in result_state["data"]
        assert "Missing OpenAI environment variables" in result_state["data"]["summary_error"]


@pytest.mark.asyncio
async def test_summary_agent_llm_failure(mock_llm_client_summary):
    """Test summary_agent when the LLM call fails."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析平安银行",
            "stock_code": "000001",
            "stock_name": "平安银行",
            "fundamental_analysis": {"summary": "基本面良好"},
            "technical_analysis": {"summary": "技术面看涨"},
            "value_analysis": {"summary": "估值合理"}
        },
        metadata={}
    )

    mock_llm_client_summary.ainvoke.side_effect = Exception(
        "LLM summarization failed")

    with patch('src.agents.summary_agent.ChatOpenAI', return_value=mock_llm_client_summary):
        result_state = await summary_agent(initial_state)

    assert "final_report" in result_state["data"]  # 即使失败也会创建一个最小报告
    assert "summary_error" in result_state["data"]
    assert "Error generating final report" in result_state["data"]["summary_error"]
