import pytest

# Assuming AgentState is defined in src.utils.state_definition
# If not, adjust the import path accordingly
from src.utils.state_definition import AgentState

def test_agent_state_creation_empty():
    """Test creating an AgentState with minimal required fields (empty messages)."""
    state: AgentState = {
        "messages": [],
        "user_query": None,
        "stock_code": None,
        "stock_name": None,
        "fundamental_analysis": None,
        "technical_analysis": None,
        "value_analysis": None,
        "summary_report": None,
        "final_report": None,
        "error_message": None,
        "current_step": None,
    }
    assert state["messages"] == []
    assert state["user_query"] is None
    assert state["final_report"] is None

def test_agent_state_creation_with_data():
    """Test creating an AgentState with some data."""
    state: AgentState = {
        "messages": [{"role": "user", "content": "Analyze AAPL"}],
        "user_query": "Analyze AAPL",
        "stock_code": "AAPL",
        "stock_name": "Apple Inc.",
        "fundamental_analysis": {"pe_ratio": 25},
        "technical_analysis": {"sma_50": 170.0},
        "value_analysis": {"fair_value": 180.0},
        "summary_report": "A summary of AAPL.",
        "final_report": "Final report for AAPL.",
        "error_message": None,
        "current_step": "summary_agent",
    }
    assert len(state["messages"]) == 1
    assert state["messages"][0]["content"] == "Analyze AAPL"
    assert state["user_query"] == "Analyze AAPL"
    assert state["stock_code"] == "AAPL"
    assert state["stock_name"] == "Apple Inc."
    assert state["fundamental_analysis"]["pe_ratio"] == 25
    assert state["technical_analysis"]["sma_50"] == 170.0
    assert state["value_analysis"]["fair_value"] == 180.0
    assert state["summary_report"] == "A summary of AAPL."
    assert state["final_report"] == "Final report for AAPL."
    assert state["error_message"] is None
    assert state["current_step"] == "summary_agent"

def test_agent_state_partial_update_simulation():
    """Simulate how an agent might update the state."""
    initial_state: AgentState = {
        "messages": [],
        "user_query": "Analyze MSFT",
        "stock_code": None,
        "stock_name": None,
        "fundamental_analysis": None,
        "technical_analysis": None,
        "value_analysis": None,
        "summary_report": None,
        "final_report": None,
        "error_message": None,
        "current_step": "initialization",
    }

    # Simulate fundamental_agent update
    updated_state_after_fundamental = initial_state.copy() # Shallow copy is fine for TypedDict
    updated_state_after_fundamental["fundamental_analysis"] = {"revenue_growth": "15%"}
    updated_state_after_fundamental["stock_code"] = "MSFT"
    updated_state_after_fundamental["stock_name"] = "Microsoft Corp."
    updated_state_after_fundamental["current_step"] = "fundamental_analysis_complete"

    assert updated_state_after_fundamental["user_query"] == "Analyze MSFT"
    assert updated_state_after_fundamental["fundamental_analysis"]["revenue_growth"] == "15%"
    assert updated_state_after_fundamental["technical_analysis"] is None # Unchanged
    assert updated_state_after_fundamental["current_step"] == "fundamental_analysis_complete"

# Example of how you might use pytest.mark.parametrize for more complex states if needed
# For now, the above tests cover the basic structure.
