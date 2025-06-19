"""
Integration tests for the Multi-Agent Research System.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio

from src.research_system_simple import SimpleResearchSystem, ResearchError


class TestResearchWorkflowIntegration:
    """Integration tests for the complete research workflow."""
    
    @pytest.fixture
    def complete_mock_responses(self):
        """Complete set of mock responses for a full research workflow."""
        return {
            "decomposition": """1. Environmental impact of renewable energy
2. Economic benefits and cost analysis
3. Technological advancements in renewable energy
4. Policy and regulatory considerations""",
            
            "research_1": """**Key Findings**: Renewable energy significantly reduces carbon emissions.
**Supporting Evidence**: Studies show 70% reduction in CO2 emissions.
**Important Considerations**: Implementation varies by region.
**Analysis**: Critical for climate change mitigation.""",
            
            "research_2": """**Key Findings**: Long-term economic benefits outweigh initial costs.
**Supporting Evidence**: ROI typically achieved within 5-10 years.
**Important Considerations**: Initial capital investment required.
**Analysis**: Job creation and energy independence are major benefits.""",
            
            "research_3": """**Key Findings**: Rapid technological improvements in efficiency.
**Supporting Evidence**: Solar panel efficiency increased 20% in 5 years.
**Important Considerations**: Technology continues to evolve rapidly.
**Analysis**: Storage solutions are becoming more viable.""",
            
            "research_4": """**Key Findings**: Government policies crucial for adoption.
**Supporting Evidence**: Tax incentives increase adoption by 40%.
**Important Considerations**: Policy stability affects investment decisions.
**Analysis**: Regulatory framework needs to support transition.""",
            
            "synthesis": """# Renewable Energy: Comprehensive Analysis Report

## Executive Summary
This comprehensive analysis examines renewable energy across environmental, economic, technological, and policy dimensions. The research demonstrates that renewable energy offers substantial benefits in all areas examined.

## Key Findings
- **Environmental**: 70% reduction in carbon emissions compared to fossil fuels
- **Economic**: Positive ROI within 5-10 years, significant job creation
- **Technological**: Rapid efficiency improvements, viable storage solutions
- **Policy**: Government support critical, tax incentives increase adoption by 40%

## Detailed Analysis
The transition to renewable energy represents a fundamental shift that addresses climate change while providing economic opportunities. Technological advances have made renewable energy increasingly cost-competitive, while supportive policies accelerate adoption.

## Conclusions
Renewable energy adoption is not only environmentally necessary but economically viable. Success requires continued technological innovation, supportive policy frameworks, and sustained investment in infrastructure development."""
        }
    
    def test_end_to_end_research_workflow(self, research_system_with_mocks, complete_mock_responses):
        """Test complete end-to-end research workflow."""
        # Setup mock responses in sequence
        mock_calls = [
            complete_mock_responses["decomposition"],
            complete_mock_responses["research_1"],
            complete_mock_responses["research_2"],
            complete_mock_responses["research_3"],
            complete_mock_responses["research_4"],
            complete_mock_responses["synthesis"]
        ]
        
        # Setup side effects for sequential calls
        mock_responses = []
        for response_text in mock_calls:
            mock_response = MagicMock()
            mock_response.content[0].text = response_text
            mock_responses.append(mock_response)
        
        research_system_with_mocks.client.messages.create.side_effect = mock_responses
        
        # Execute research
        query = "What are the comprehensive benefits of renewable energy?"
        result = research_system_with_mocks.conduct_research(query)
        
        # Verify overall structure
        assert result["query"] == query
        assert result["total_subtasks"] == 4
        assert len(result["subtasks"]) == 4
        assert len(result["research_results"]) == 4
        
        # Verify subtasks were correctly parsed
        expected_subtasks = [
            "Environmental impact of renewable energy",
            "Economic benefits and cost analysis", 
            "Technological advancements in renewable energy",
            "Policy and regulatory considerations"
        ]
        
        for i, expected in enumerate(expected_subtasks):
            assert expected in result["subtasks"][i]
        
        # Verify research results
        for i, research_result in enumerate(result["research_results"]):
            assert research_result["status"] == "completed"
            assert research_result["index"] == i
            assert research_result["model_used"] == "claude-3-5-sonnet-20241022"
            assert "Key Findings" in research_result["findings"]
        
        # Verify final report
        assert "Executive Summary" in result["final_report"]
        assert "Key Findings" in result["final_report"]
        assert "Detailed Analysis" in result["final_report"]
        assert "Conclusions" in result["final_report"]
        
        # Verify model usage
        assert result["orchestrator_model"] == "claude-3-opus-20240229"
        assert result["research_model"] == "claude-3-5-sonnet-20241022"
        
        # Verify API call sequence
        assert research_system_with_mocks.client.messages.create.call_count == 6
        
        # Verify model selection for each call
        calls = research_system_with_mocks.client.messages.create.call_args_list
        
        # First call should use orchestrator model (decomposition)
        assert calls[0][1]['model'] == "claude-3-opus-20240229"
        
        # Research calls should use research model
        for i in range(1, 5):
            assert calls[i][1]['model'] == "claude-3-5-sonnet-20241022"
        
        # Final call should use orchestrator model (synthesis)
        assert calls[5][1]['model'] == "claude-3-opus-20240229"
    
    def test_research_with_partial_failures(self, research_system_with_mocks, complete_mock_responses):
        """Test research workflow when some subtasks fail."""
        # Setup responses where some research tasks fail
        mock_responses = []
        
        # Successful decomposition
        decomp_response = MagicMock()
        decomp_response.content[0].text = complete_mock_responses["decomposition"]
        mock_responses.append(decomp_response)
        
        # First research succeeds
        research1_response = MagicMock()
        research1_response.content[0].text = complete_mock_responses["research_1"]
        mock_responses.append(research1_response)
        
        # Second research fails
        mock_responses.append(Exception("API Error"))
        
        # Third research succeeds
        research3_response = MagicMock()
        research3_response.content[0].text = complete_mock_responses["research_3"]
        mock_responses.append(research3_response)
        
        # Fourth research succeeds
        research4_response = MagicMock()
        research4_response.content[0].text = complete_mock_responses["research_4"]
        mock_responses.append(research4_response)
        
        # Synthesis succeeds
        synthesis_response = MagicMock()
        synthesis_response.content[0].text = complete_mock_responses["synthesis"]
        mock_responses.append(synthesis_response)
        
        research_system_with_mocks.client.messages.create.side_effect = mock_responses
        
        # Execute research
        result = research_system_with_mocks.conduct_research("Test query with failures")
        
        # Verify that research completed despite partial failures
        assert result["total_subtasks"] == 4
        assert len(result["research_results"]) == 4
        
        # Check individual results
        assert result["research_results"][0]["status"] == "completed"
        assert result["research_results"][1]["status"] == "failed"
        assert result["research_results"][2]["status"] == "completed"
        assert result["research_results"][3]["status"] == "completed"
        
        # Synthesis should still work with successful results
        assert "Executive Summary" in result["final_report"]
    
    def test_research_all_subtasks_fail(self, research_system_with_mocks):
        """Test research workflow when all subtasks fail."""
        # Setup responses where decomposition succeeds but all research fails
        decomp_response = MagicMock()
        decomp_response.content[0].text = "1. Task 1\n2. Task 2\n3. Task 3"
        
        # All research tasks fail
        mock_responses = [
            decomp_response,
            Exception("API Error 1"),
            Exception("API Error 2"),  
            Exception("API Error 3")
        ]
        
        research_system_with_mocks.client.messages.create.side_effect = mock_responses
        
        # Should raise error when synthesis attempts but has no successful results
        with pytest.raises(ResearchError, match="No successful research results"):
            research_system_with_mocks.conduct_research("Test query all failures")


class TestModelSelection:
    """Integration tests for model selection logic."""
    
    def test_orchestrator_model_usage(self, research_system_with_mocks):
        """Test that orchestrator model is used for appropriate tasks."""
        # Mock successful decomposition
        decomp_response = MagicMock()
        decomp_response.content[0].text = "1. Single task"
        
        # Mock successful research
        research_response = MagicMock()
        research_response.content[0].text = "Research findings"
        
        # Mock successful synthesis
        synthesis_response = MagicMock()
        synthesis_response.content[0].text = "Final report"
        
        research_system_with_mocks.client.messages.create.side_effect = [
            decomp_response,
            research_response,
            synthesis_response
        ]
        
        research_system_with_mocks.conduct_research("Test query")
        
        calls = research_system_with_mocks.client.messages.create.call_args_list
        
        # Decomposition should use orchestrator model
        assert calls[0][1]['model'] == "claude-3-opus-20240229"
        
        # Research should use research model
        assert calls[1][1]['model'] == "claude-3-5-sonnet-20241022"
        
        # Synthesis should use orchestrator model
        assert calls[2][1]['model'] == "claude-3-opus-20240229"
    
    def test_custom_model_configuration(self, mock_env_vars):
        """Test system with custom model configuration."""
        with patch('src.research_system_simple.anthropic.Anthropic') as mock_anthropic:
            system = SimpleResearchSystem(
                api_key="test-key",
                orchestrator_model="custom-opus",
                research_model="custom-sonnet"
            )
            
            assert system.orchestrator_model == "custom-opus"
            assert system.research_model == "custom-sonnet"
            
            info = system.get_system_info()
            assert info["orchestrator_model"] == "custom-opus"
            assert info["research_model"] == "custom-sonnet"


class TestErrorRecovery:
    """Integration tests for error recovery and resilience."""
    
    def test_network_timeout_handling(self, research_system_with_mocks):
        """Test handling of network timeouts."""
        import requests
        
        # Simulate timeout error
        research_system_with_mocks.client.messages.create.side_effect = requests.exceptions.Timeout("Request timeout")
        
        with pytest.raises(ResearchError, match="Query decomposition failed"):
            research_system_with_mocks.conduct_research("Test query")
    
    def test_api_rate_limit_handling(self, research_system_with_mocks):
        """Test handling of API rate limits."""
        # Simulate rate limit error with a generic exception
        rate_limit_error = Exception("Rate limit exceeded")
        research_system_with_mocks.client.messages.create.side_effect = rate_limit_error
        
        with pytest.raises(ResearchError, match="Query decomposition failed"):
            research_system_with_mocks.conduct_research("Test query")
    
    def test_invalid_response_format(self, research_system_with_mocks):
        """Test handling of invalid response formats."""
        # Mock response with invalid format
        invalid_response = MagicMock()
        invalid_response.content[0].text = "This is not a proper numbered list or bullet points"
        
        research_system_with_mocks.client.messages.create.return_value = invalid_response
        
        with pytest.raises(ResearchError, match="Failed to generate subtasks"):
            research_system_with_mocks.conduct_research("Test query")


class TestPerformanceAndLimits:
    """Integration tests for performance and limits."""
    
    def test_max_subtasks_limit(self, research_system_with_mocks):
        """Test that subtask limit is enforced."""
        # Mock response with many subtasks
        many_subtasks_response = MagicMock()
        many_subtasks_response.content[0].text = """1. Task 1
2. Task 2
3. Task 3
4. Task 4
5. Task 5
6. Task 6
7. Task 7"""
        
        research_system_with_mocks.client.messages.create.return_value = many_subtasks_response
        
        subtasks = research_system_with_mocks._decompose_query("Complex query")
        
        # Should be limited to MAX_SUBTASKS (4)
        assert len(subtasks) == 4
    
    def test_large_response_handling(self, research_system_with_mocks):
        """Test handling of large responses."""
        # Create a very large response
        large_response = "Very detailed research findings. " * 1000
        
        mock_response = MagicMock()
        mock_response.content[0].text = large_response
        
        research_system_with_mocks.client.messages.create.return_value = mock_response
        
        result = research_system_with_mocks._research_subtask("Test task", 0)
        
        assert result["status"] == "completed"
        assert len(result["findings"]) == len(large_response)
    
    def test_system_info_consistency(self, research_system_with_mocks):
        """Test that system info remains consistent throughout workflow."""
        initial_info = research_system_with_mocks.get_system_info()
        
        # Perform some operations
        research_system_with_mocks._parse_subtasks("1. Test task")
        research_system_with_mocks._build_research_prompt("Test task")
        
        final_info = research_system_with_mocks.get_system_info()
        
        # Info should remain consistent
        assert initial_info == final_info