import pytest
from unittest.mock import AsyncMock, patch
import json

from src.agents.technical_agent import technical_agent
from src.utils.state_definition import AgentState

@pytest.fixture
def mock_llm_client_technical(): 
    llm_client = AsyncMock()
    llm_client.invoke.return_value.content = json.dumps({
        "trend_analysis": "短期上升趋势，中期震荡",
        "support_resistance_levels": {"support": [90, 85], "resistance": [100, 105]},
        "technical_indicators_summary": "MACD金叉，RSI超买",
        "chart_patterns": "出现头肩底形态"
    })
    return llm_client

@pytest.fixture
def mock_mcp_client_technical(): 
    mcp_client = AsyncMock()
    mcp_client.get_market_data.return_value = {
        "kline_data_daily": [{"date": "2023-01-01", "open": 100, "close": 102, "high": 103, "low": 99, "volume": 10000}],
        "moving_averages": {"ma5": 101, "ma10": 100, "ma20": 98},
        "rsi": 75,
        "macd": {"diff": 0.5, "dea": 0.3, "macd": 0.2}
    }
    return mcp_client

@pytest.mark.asyncio
async def test_technical_agent_success(mock_llm_client_technical, mock_mcp_client_technical):
    """Test the technical_agent successfully processes and provides technical analysis."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析一下贵州茅台的技术面",
            "stock_code": "600519", 
            "company_name": "贵州茅台",
        },
        metadata={}
    )

    # Create a mock for create_react_agent and AgentExecutor
    mock_agent = AsyncMock()
    mock_agent_executor = AsyncMock()
    mock_agent_executor.ainvoke.return_value = {"output": "This is a technical analysis of Kweichow Moutai"}
    
    with patch('src.agents.technical_agent.ChatOpenAI', return_value=mock_llm_client_technical), \
         patch('src.agents.technical_agent.get_mcp_tools', return_value=mock_mcp_client_technical), \
         patch('src.agents.technical_agent.create_react_agent', return_value=mock_agent), \
         patch('src.agents.technical_agent.AgentExecutor', return_value=mock_agent_executor):
        
        result_state = await technical_agent(initial_state)

        assert result_state["data"]["stock_code"] == "600519"  # Should remain unchanged
        assert "technical_analysis" in result_state["data"]
        assert "technical_analysis_error" not in result_state["data"]

@pytest.mark.asyncio
async def test_technical_agent_missing_query(mock_llm_client_technical):
    """Test technical_agent when query is missing in state."""
    initial_state = AgentState(
        messages=[],
        data={
            "stock_code": "600519",
            "company_name": "贵州茅台",
            # No query provided
        },
        metadata={}
    )

    result_state = await technical_agent(initial_state)

    assert "technical_analysis" not in result_state["data"]
    assert "technical_analysis_error" in result_state["data"]
    assert "User query is missing" in result_state["data"]["technical_analysis_error"]

@pytest.mark.asyncio
async def test_technical_agent_environment_variables_missing():
    """Test technical_agent when environment variables are missing."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析贵州茅台的技术面",
            "stock_code": "600519",
            "company_name": "贵州茅台",
        },
        metadata={}
    )

    with patch('src.agents.technical_agent.os.getenv', return_value=None):
        result_state = await technical_agent(initial_state)

        assert "technical_analysis" not in result_state["data"]
        assert "technical_analysis_error" in result_state["data"]
        assert "Missing OpenAI environment variables" in result_state["data"]["technical_analysis_error"]

@pytest.mark.asyncio
async def test_technical_agent_mcp_tools_unavailable(mock_llm_client_technical):
    """Test technical_agent when MCP tools are unavailable."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析贵州茅台的技术面",
            "stock_code": "600519",
            "company_name": "贵州茅台",
        },
        metadata={}
    )
    
    with patch('src.agents.technical_agent.ChatOpenAI', return_value=mock_llm_client_technical), \
         patch('src.agents.technical_agent.get_mcp_tools', return_value=None):
        
        result_state = await technical_agent(initial_state)

        assert "technical_analysis" not in result_state["data"]
        assert "technical_analysis_error" in result_state["data"]
        assert "No MCP tools available" in result_state["data"]["technical_analysis_error"]

@pytest.mark.asyncio
async def test_technical_agent_execution_error(mock_llm_client_technical, mock_mcp_client_technical):
    """Test technical_agent when agent execution fails."""
    initial_state = AgentState(
        messages=[],
        data={
            "query": "分析贵州茅台的技术面",
            "stock_code": "600519",
            "company_name": "贵州茅台",
        },
        metadata={}
    )
    
    # Setup mocks to raise an exception
    agent_executor_mock = AsyncMock()
    agent_executor_mock.ainvoke.side_effect = Exception("Agent execution error")
    
    with patch('src.agents.technical_agent.ChatOpenAI', return_value=mock_llm_client_technical), \
         patch('src.agents.technical_agent.get_mcp_tools', return_value=mock_mcp_client_technical), \
         patch('src.agents.technical_agent.AgentExecutor', return_value=agent_executor_mock):
        
        result_state = await technical_agent(initial_state)

        assert "technical_analysis" not in result_state["data"]
        assert "technical_analysis_error" in result_state["data"]
        assert "Error during execution" in result_state["data"]["technical_analysis_error"]