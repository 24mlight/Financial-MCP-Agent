import pytest
from unittest.mock import AsyncMock, patch
import json

from src.agents.fundamental_agent import fundamental_agent
from src.utils.state_definition import AgentState


@pytest.fixture
def mock_llm_client_fundamental():
    llm_client = AsyncMock()
    llm_client.invoke.return_value.content = json.dumps({
        "financial_health": "良好",
        "revenue_growth": "稳定增长",
        "profit_margins": "行业领先",
        "debt_levels": "较低",
        "competitive_position": "市场领导者"
    })
    return llm_client


@pytest.fixture
def mock_mcp_client_fundamental():
    mcp_client = AsyncMock()
    mcp_client.get_financial_statements.return_value = {
        "income_statement": {"revenue": 10000, "net_income": 2000},
        "balance_sheet": {"total_assets": 50000, "total_liabilities": 20000},
        "cash_flow": {"operating_cash_flow": 3000}
    }
    return mcp_client


@pytest.mark.asyncio
async def test_fundamental_agent_success(mock_llm_client_fundamental, mock_mcp_client_fundamental):
    """Test the fundamental_agent successfully processes and provides fundamental analysis."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析一下贵州茅台的基本面",
            "stock_code": "600519",
            "company_name": "贵州茅台",
        },
        metadata={}
    )

    # Create a mock for create_react_agent and AgentExecutor
    mock_agent = AsyncMock()
    mock_agent_executor = AsyncMock()
    mock_agent_executor.ainvoke.return_value = {
        "output": "This is a fundamental analysis of Kweichow Moutai"}

    with patch('src.agents.fundamental_agent.ChatOpenAI', return_value=mock_llm_client_fundamental), \
            patch('src.agents.fundamental_agent.get_mcp_tools', return_value=mock_mcp_client_fundamental), \
            patch('src.agents.fundamental_agent.create_react_agent', return_value=mock_agent), \
            patch('src.agents.fundamental_agent.AgentExecutor', return_value=mock_agent_executor):

        result_state = await fundamental_agent(initial_state)

        # Should remain unchanged
        assert result_state["data"]["stock_code"] == "600519"
        assert "fundamental_analysis" in result_state["data"]
        assert "fundamental_analysis_error" not in result_state["data"]


@pytest.mark.asyncio
async def test_fundamental_agent_missing_query(mock_llm_client_fundamental):
    """Test fundamental_agent when query is missing in state."""
    initial_state = AgentState(
        messages=[],
        data={
            "stock_code": "600519",
            "company_name": "贵州茅台",
            # No query provided
        },
        metadata={}
    )

    result_state = await fundamental_agent(initial_state)

    assert "fundamental_analysis" not in result_state["data"]
    assert "fundamental_analysis_error" in result_state["data"]
    assert "User query is missing" in result_state["data"]["fundamental_analysis_error"]


@pytest.mark.asyncio
async def test_fundamental_agent_environment_variables_missing():
    """Test fundamental_agent when environment variables are missing."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析贵州茅台的基本面",
            "stock_code": "600519",
            "company_name": "贵州茅台",
        },
        metadata={}
    )

    with patch('src.agents.fundamental_agent.os.getenv', return_value=None):
        result_state = await fundamental_agent(initial_state)

        assert "fundamental_analysis" not in result_state["data"]
        assert "fundamental_analysis_error" in result_state["data"]
        assert "Missing OpenAI environment variables" in result_state[
            "data"]["fundamental_analysis_error"]


@pytest.mark.asyncio
async def test_fundamental_agent_mcp_tools_unavailable(mock_llm_client_fundamental):
    """Test fundamental_agent when MCP tools are unavailable."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析贵州茅台的基本面",
            "stock_code": "600519",
            "company_name": "贵州茅台",
        },
        metadata={}
    )

    with patch('src.agents.fundamental_agent.ChatOpenAI', return_value=mock_llm_client_fundamental), \
            patch('src.agents.fundamental_agent.get_mcp_tools', return_value=None):

        result_state = await fundamental_agent(initial_state)

        assert "fundamental_analysis" not in result_state["data"]
        assert "fundamental_analysis_error" in result_state["data"]
        assert "No MCP tools available" in result_state["data"]["fundamental_analysis_error"]


@pytest.mark.asyncio
async def test_fundamental_agent_execution_error(mock_llm_client_fundamental, mock_mcp_client_fundamental):
    """Test fundamental_agent when agent execution fails."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析贵州茅台的基本面",
            "stock_code": "600519",
            "company_name": "贵州茅台",
        },
        metadata={}
    )

    # Setup mocks to raise an exception
    agent_executor_mock = AsyncMock()
    agent_executor_mock.ainvoke.side_effect = Exception(
        "Agent execution error")

    with patch('src.agents.fundamental_agent.ChatOpenAI', return_value=mock_llm_client_fundamental), \
            patch('src.agents.fundamental_agent.get_mcp_tools', return_value=mock_mcp_client_fundamental), \
            patch('src.agents.fundamental_agent.AgentExecutor', return_value=agent_executor_mock):

        result_state = await fundamental_agent(initial_state)

        assert "fundamental_analysis" not in result_state["data"]
        assert "fundamental_analysis_error" in result_state["data"]
        assert "Error during execution" in result_state["data"]["fundamental_analysis_error"]
