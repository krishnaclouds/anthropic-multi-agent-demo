"""
Pytest configuration and shared fixtures for the Multi-Agent Research System tests.
"""

import os
import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.research_system_simple import SimpleResearchSystem, ResearchError


@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client for testing."""
    client = MagicMock()
    
    # Mock the messages.create method
    client.messages.create = Mock()
    
    # Default mock response
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = "Mock response text"
    
    client.messages.create.return_value = mock_response
    
    return client


@pytest.fixture
def sample_query():
    """Sample research query for testing."""
    return "What are the benefits of renewable energy?"


@pytest.fixture
def sample_subtasks():
    """Sample subtasks for testing."""
    return [
        "Environmental benefits of renewable energy",
        "Economic advantages of renewable energy",
        "Technological aspects of renewable energy",
        "Social impact of renewable energy adoption"
    ]


@pytest.fixture
def sample_research_results():
    """Sample research results for testing."""
    return [
        {
            "subtask": "Environmental benefits of renewable energy",
            "index": 0,
            "findings": "Renewable energy significantly reduces greenhouse gas emissions...",
            "status": "completed",
            "model_used": "claude-3-5-sonnet-20241022"
        },
        {
            "subtask": "Economic advantages of renewable energy",
            "index": 1,
            "findings": "Long-term cost savings and job creation are key economic benefits...",
            "status": "completed",
            "model_used": "claude-3-5-sonnet-20241022"
        }
    ]


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key")
    monkeypatch.setenv("ORCHESTRATOR_MODEL", "claude-3-opus-20240229")
    monkeypatch.setenv("RESEARCH_MODEL", "claude-3-5-sonnet-20241022")


@pytest.fixture
def research_system_with_mocks(mock_anthropic_client, mock_env_vars, monkeypatch):
    """Create a research system with mocked dependencies."""
    # Mock the anthropic module
    mock_anthropic = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_anthropic_client
    monkeypatch.setattr("src.research_system_simple.anthropic", mock_anthropic)
    
    # Create the research system
    system = SimpleResearchSystem(api_key="test-api-key")
    system.client = mock_anthropic_client
    
    return system


@pytest.fixture
def decomposition_response():
    """Sample query decomposition response."""
    return """1. Environmental benefits of renewable energy sources
2. Economic advantages and cost-effectiveness
3. Technological developments and efficiency improvements
4. Social and community impacts"""


@pytest.fixture
def research_response():
    """Sample research response for a subtask."""
    return """
**Key Findings**: Renewable energy sources provide significant environmental benefits.

**Supporting Evidence**: Studies show a 60-80% reduction in carbon emissions compared to fossil fuels.

**Important Considerations**: Implementation varies by geographic location and existing infrastructure.

**Analysis**: The transition to renewable energy is crucial for meeting climate goals.
"""


@pytest.fixture
def synthesis_response():
    """Sample synthesis response for final report."""
    return """
# Renewable Energy Benefits: Comprehensive Analysis

## Executive Summary
This research examines the multifaceted benefits of renewable energy adoption...

## Key Findings
- Environmental: Significant reduction in greenhouse gas emissions
- Economic: Long-term cost savings and job creation
- Technological: Rapid improvements in efficiency and storage

## Detailed Analysis
The analysis reveals that renewable energy offers substantial advantages across multiple dimensions...

## Conclusions
Renewable energy adoption is essential for sustainable development and climate goals.
"""