import pytest
from unittest.mock import patch, AsyncMock

from src.tools.mcp_client import MCPClient

@pytest.fixture
def mcp_client():
    """Fixture to create an MCPClient instance."""
    return MCPClient()

@pytest.mark.asyncio
async def test_mcp_client_get_stock_basic_info_success(mcp_client: MCPClient):
    """Test successful retrieval of stock basic info."""
    mock_response = {
        "code": "600000",
        "name": "浦发银行",
        "market": "SH",
        "industry": "银行",
        # ... other fields
    }
    with patch('src.tools.mcp_client.get_client', new_callable=AsyncMock) as mock_get_client:
        mock_mcp = AsyncMock()
        mock_mcp.get_stock_basic_info.return_value = mock_response
        mock_get_client.return_value = mock_mcp

        result = await mcp_client.get_stock_basic_info("600000")
        assert result == mock_response
        mock_mcp.get_stock_basic_info.assert_called_once_with(stock_code="600000")

@pytest.mark.asyncio
async def test_mcp_client_get_stock_basic_info_failure(mcp_client: MCPClient):
    """Test failure scenario for retrieving stock basic info."""
    with patch('src.tools.mcp_client.get_client', new_callable=AsyncMock) as mock_get_client:
        mock_mcp = AsyncMock()
        mock_mcp.get_stock_basic_info.side_effect = Exception("MCP API Error")
        mock_get_client.return_value = mock_mcp

        with pytest.raises(Exception, match="MCP API Error"):
            await mcp_client.get_stock_basic_info("000001")

@pytest.mark.asyncio
async def test_mcp_client_get_financial_data_success(mcp_client: MCPClient):
    """Test successful retrieval of financial data."""
    mock_response = {
        "pe_ratio": 10.5,
        "pb_ratio": 1.2,
        # ... other financial indicators
    }
    with patch('src.tools.mcp_client.get_client', new_callable=AsyncMock) as mock_get_client:
        mock_mcp = AsyncMock()
        mock_mcp.get_financial_data.return_value = mock_response
        mock_get_client.return_value = mock_mcp

        result = await mcp_client.get_financial_data("600000", ["pe_ratio", "pb_ratio"])
        assert result == mock_response
        mock_mcp.get_financial_data.assert_called_once_with(stock_code="600000", indicators=["pe_ratio", "pb_ratio"])

@pytest.mark.asyncio
async def test_mcp_client_get_financial_data_failure(mcp_client: MCPClient):
    """Test failure scenario for retrieving financial data."""
    with patch('src.tools.mcp_client.get_client', new_callable=AsyncMock) as mock_get_client:
        mock_mcp = AsyncMock()
        mock_mcp.get_financial_data.side_effect = Exception("MCP Data Error")
        mock_get_client.return_value = mock_mcp

        with pytest.raises(Exception, match="MCP Data Error"):
            await mcp_client.get_financial_data("000001", ["non_existent_indicator"])


@pytest.mark.asyncio
async def test_mcp_client_get_market_data_success(mcp_client: MCPClient):
    """Test successful retrieval of market data."""
    mock_response = {
        "current_price": 100.0,
        "volume": 1000000,
        # ... other market data
    }
    with patch('src.tools.mcp_client.get_client', new_callable=AsyncMock) as mock_get_client:
        mock_mcp = AsyncMock()
        mock_mcp.get_market_data.return_value = mock_response
        mock_get_client.return_value = mock_mcp

        result = await mcp_client.get_market_data("600000", ["current_price", "volume"])
        assert result == mock_response
        mock_mcp.get_market_data.assert_called_once_with(stock_code="600000", indicators=["current_price", "volume"])

@pytest.mark.asyncio
async def test_mcp_client_get_market_data_failure(mcp_client: MCPClient):
    """Test failure scenario for retrieving market data."""
    with patch('src.tools.mcp_client.get_client', new_callable=AsyncMock) as mock_get_client:
        mock_mcp = AsyncMock()
        mock_mcp.get_market_data.side_effect = Exception("MCP Market Error")
        mock_get_client.return_value = mock_mcp

        with pytest.raises(Exception, match="MCP Market Error"):
            await mcp_client.get_market_data("000001", ["price"])

# Add more tests for other MCPClient methods (e.g., get_news, get_analyst_ratings) if they exist
# and are used by the agents, following the same pattern of mocking 'get_client'
# and the specific MCP method call.
