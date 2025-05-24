import pytest
from unittest.mock import AsyncMock, patch
import json

from src.agents.value_agent import value_agent
from src.utils.state_definition import AgentState


@pytest.fixture
def mock_llm_client_value():
    llm_client = AsyncMock()
    llm_client.invoke.return_value.content = json.dumps({
        "valuation_summary": "基于DCF和可比公司分析，当前股价合理。",
        "dcf_analysis": {"fair_value": 150, "assumptions": "增长率5%，折现率10%"},
        "comparables_analysis": {"median_pe": 25, "implied_value": 155},
        "investment_rating": "持有"
    })
    return llm_client


@pytest.fixture
def mock_mcp_client_value():
    mcp_client = AsyncMock()
    mcp_client.get_financial_data.return_value = {
        "eps": 5.0,
        "bps": 60.0,
        "analyst_ratings_summary": {"buy": 10, "hold": 5, "sell": 1}
    }
    mcp_client.get_market_data.return_value = {
        "current_price": 145.0
    }
    return mcp_client


@pytest.mark.asyncio
async def test_value_agent_success(mock_llm_client_value, mock_mcp_client_value):
    """Test the value_agent successfully processes and provides valuation analysis."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "评估一下贵州茅台的价值",
            "stock_code": "600519",
            "company_name": "贵州茅台",
            "fundamental_analysis": "公司业绩稳定增长，利润率高",
            "technical_analysis": "短期上升趋势，成交量增加"
        },
        metadata={}
    )

    # Create a mock for create_react_agent and AgentExecutor
    mock_agent = AsyncMock()
    mock_agent_executor = AsyncMock()
    mock_agent_executor.ainvoke.return_value = {
        "output": "This is a valuation analysis of Kweichow Moutai"}

    with patch('src.agents.value_agent.ChatOpenAI', return_value=mock_llm_client_value), \
            patch('src.agents.value_agent.get_mcp_tools', return_value=mock_mcp_client_value), \
            patch('src.agents.value_agent.create_react_agent', return_value=mock_agent), \
            patch('src.agents.value_agent.AgentExecutor', return_value=mock_agent_executor):

        result_state = await value_agent(initial_state)

        # Should remain unchanged
        assert result_state["data"]["stock_code"] == "600519"
        assert "value_analysis" in result_state["data"]
        assert "value_analysis_error" not in result_state["data"]


@pytest.mark.asyncio
async def test_value_agent_missing_query(mock_llm_client_value):
    """Test value_agent when query is missing in state."""
    initial_state = AgentState(
        messages=[],
        data={
            "stock_code": "600519",
            "company_name": "贵州茅台",
            # No query provided
        },
        metadata={}
    )

    result_state = await value_agent(initial_state)

    assert "value_analysis" not in result_state["data"]
    assert "value_analysis_error" in result_state["data"]
    assert "User query is missing" in result_state["data"]["value_analysis_error"]


@pytest.mark.asyncio
async def test_value_agent_environment_variables_missing():
    """Test value_agent when environment variables are missing."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "评估贵州茅台的价值",
            "stock_code": "600519",
            "company_name": "贵州茅台",
        },
        metadata={}
    )

    with patch('src.agents.value_agent.os.getenv', return_value=None):
        result_state = await value_agent(initial_state)

        assert "value_analysis" not in result_state["data"]
        assert "value_analysis_error" in result_state["data"]
        assert "Missing OpenAI environment variables" in result_state[
            "data"]["value_analysis_error"]


@pytest.mark.asyncio
async def test_value_agent_mcp_tools_unavailable(mock_llm_client_value):
    """Test value_agent when MCP tools are unavailable."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "评估贵州茅台的价值",
            "stock_code": "600519",
            "company_name": "贵州茅台",
        },
        metadata={}
    )

    with patch('src.agents.value_agent.ChatOpenAI', return_value=mock_llm_client_value), \
            patch('src.agents.value_agent.get_mcp_tools', return_value=None):

        result_state = await value_agent(initial_state)

        assert "value_analysis" not in result_state["data"]
        assert "value_analysis_error" in result_state["data"]
        assert "No MCP tools available" in result_state["data"]["value_analysis_error"]


@pytest.mark.asyncio
async def test_value_agent_execution_error(mock_llm_client_value, mock_mcp_client_value):
    """Test value_agent when agent execution fails."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "评估贵州茅台的价值",
            "stock_code": "600519",
            "company_name": "贵州茅台",
        },
        metadata={}
    )

    # Setup mocks to raise an exception
    agent_executor_mock = AsyncMock()
    agent_executor_mock.ainvoke.side_effect = Exception(
        "Agent execution error")

    with patch('src.agents.value_agent.ChatOpenAI', return_value=mock_llm_client_value), \
            patch('src.agents.value_agent.get_mcp_tools', return_value=mock_mcp_client_value), \
            patch('src.agents.value_agent.AgentExecutor', return_value=agent_executor_mock):

        result_state = await value_agent(initial_state)

        assert "value_analysis" not in result_state["data"]
        assert "value_analysis_error" in result_state["data"]
        assert "Error during execution" in result_state["data"]["value_analysis_error"]
