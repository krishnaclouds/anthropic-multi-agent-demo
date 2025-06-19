"""
Unit tests for the SimpleResearchSystem class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from src.research_system_simple import SimpleResearchSystem, ResearchError


class TestSimpleResearchSystemInitialization:
    """Test cases for system initialization."""
    
    def test_initialization_with_api_key(self, mock_env_vars):
        """Test successful initialization with API key."""
        with patch('src.research_system_simple.anthropic.Anthropic') as mock_anthropic:
            system = SimpleResearchSystem(api_key="test-key")
            
            assert system.api_key == "test-key"
            assert system.orchestrator_model == "claude-3-opus-20240229"
            assert system.research_model == "claude-3-5-sonnet-20241022"
            mock_anthropic.assert_called_once_with(api_key="test-key")
    
    def test_initialization_from_env(self, mock_env_vars):
        """Test initialization using environment variables."""
        with patch('src.research_system_simple.anthropic.Anthropic') as mock_anthropic:
            system = SimpleResearchSystem()
            
            assert system.api_key == "test-api-key"
            assert system.orchestrator_model == "claude-3-opus-20240229"
            assert system.research_model == "claude-3-5-sonnet-20241022"
    
    def test_initialization_custom_models(self, mock_env_vars):
        """Test initialization with custom models."""
        with patch('src.research_system_simple.anthropic.Anthropic') as mock_anthropic:
            system = SimpleResearchSystem(
                orchestrator_model="custom-opus",
                research_model="custom-sonnet"
            )
            
            assert system.orchestrator_model == "custom-opus"
            assert system.research_model == "custom-sonnet"
    
    def test_initialization_missing_api_key(self):
        """Test initialization failure with missing API key."""
        # Test that the validation logic exists by checking the error message
        with patch('src.research_system_simple.load_dotenv'):
            with patch('os.getenv', return_value=None):
                with pytest.raises(ResearchError, match="API key is required"):
                    SimpleResearchSystem()
    
    def test_initialization_empty_api_key(self):
        """Test initialization failure with empty API key."""
        # Test explicit empty API key
        with patch('src.research_system_simple.load_dotenv'):
            with patch('os.getenv', return_value=""):
                with pytest.raises(ResearchError, match="API key is required"):
                    SimpleResearchSystem()
    
    def test_initialization_anthropic_client_failure(self, mock_env_vars):
        """Test initialization failure when Anthropic client creation fails."""
        with patch('src.research_system_simple.anthropic.Anthropic', side_effect=Exception("Client error")):
            with pytest.raises(ResearchError, match="Failed to initialize Anthropic client"):
                SimpleResearchSystem(api_key="test-key")


class TestQueryDecomposition:
    """Test cases for query decomposition functionality."""
    
    def test_decompose_query_success(self, research_system_with_mocks, decomposition_response):
        """Test successful query decomposition."""
        # Setup mock response
        research_system_with_mocks.client.messages.create.return_value.content[0].text = decomposition_response
        
        result = research_system_with_mocks._decompose_query("What are the benefits of renewable energy?")
        
        assert len(result) == 4
        assert "Environmental benefits" in result[0]
        assert "Economic advantages" in result[1]
        assert "Technological developments" in result[2]
        assert "Social and community impacts" in result[3]
        
        # Verify API call
        research_system_with_mocks.client.messages.create.assert_called_once()
        call_args = research_system_with_mocks.client.messages.create.call_args
        assert call_args[1]['model'] == "claude-3-opus-20240229"  # Orchestrator model
    
    def test_decompose_query_api_error(self, research_system_with_mocks):
        """Test query decomposition with API error."""
        research_system_with_mocks.client.messages.create.side_effect = Exception("API Error")
        
        with pytest.raises(ResearchError, match="Query decomposition failed"):
            research_system_with_mocks._decompose_query("Test query")
    
    def test_parse_subtasks_numbered_list(self, research_system_with_mocks):
        """Test parsing subtasks from numbered list."""
        response = """1. First subtask
2. Second subtask
3. Third subtask"""
        
        result = research_system_with_mocks._parse_subtasks(response)
        
        assert len(result) == 3
        assert result[0] == "First subtask"
        assert result[1] == "Second subtask"
        assert result[2] == "Third subtask"
    
    def test_parse_subtasks_bullet_points(self, research_system_with_mocks):
        """Test parsing subtasks from bullet points."""
        response = """- First subtask
- Second subtask
- Third subtask"""
        
        result = research_system_with_mocks._parse_subtasks(response)
        
        assert len(result) == 3
        assert result[0] == "First subtask"
        assert result[1] == "Second subtask"
        assert result[2] == "Third subtask"
    
    def test_parse_subtasks_max_limit(self, research_system_with_mocks):
        """Test that parsing respects maximum subtask limit."""
        response = """1. First
2. Second  
3. Third
4. Fourth
5. Fifth
6. Sixth"""
        
        result = research_system_with_mocks._parse_subtasks(response)
        
        assert len(result) == 4  # Should be limited to MAX_SUBTASKS


class TestSubtaskResearch:
    """Test cases for subtask research functionality."""
    
    def test_research_subtask_success(self, research_system_with_mocks, research_response):
        """Test successful subtask research."""
        research_system_with_mocks.client.messages.create.return_value.content[0].text = research_response
        
        result = research_system_with_mocks._research_subtask("Test subtask", 0)
        
        assert result["subtask"] == "Test subtask"
        assert result["index"] == 0
        assert result["status"] == "completed"
        assert result["model_used"] == "claude-3-5-sonnet-20241022"
        assert research_response in result["findings"]
        
        # Verify API call uses research model
        call_args = research_system_with_mocks.client.messages.create.call_args
        assert call_args[1]['model'] == "claude-3-5-sonnet-20241022"
    
    def test_research_subtask_api_error(self, research_system_with_mocks):
        """Test subtask research with API error."""
        research_system_with_mocks.client.messages.create.side_effect = Exception("API Error")
        
        result = research_system_with_mocks._research_subtask("Test subtask", 0)
        
        assert result["status"] == "failed"
        assert "Research failed" in result["findings"]
        assert result["model_used"] == "claude-3-5-sonnet-20241022"
    
    def test_build_research_prompt(self, research_system_with_mocks):
        """Test research prompt building."""
        prompt = research_system_with_mocks._build_research_prompt("Test subtask")
        
        assert "Test subtask" in prompt
        assert "Key Findings" in prompt
        assert "Supporting Evidence" in prompt
        assert "Important Considerations" in prompt
        assert "Analysis" in prompt


class TestResultsSynthesis:
    """Test cases for results synthesis functionality."""
    
    def test_synthesize_results_success(self, research_system_with_mocks, sample_research_results, synthesis_response):
        """Test successful results synthesis."""
        research_system_with_mocks.client.messages.create.return_value.content[0].text = synthesis_response
        
        result = research_system_with_mocks._synthesize_results("Test query", sample_research_results)
        
        assert synthesis_response in result
        
        # Verify API call uses orchestrator model
        call_args = research_system_with_mocks.client.messages.create.call_args
        assert call_args[1]['model'] == "claude-3-opus-20240229"
    
    def test_synthesize_results_no_successful_results(self, research_system_with_mocks):
        """Test synthesis with no successful results."""
        failed_results = [
            {"status": "failed", "findings": "Failed research"}
        ]
        
        with pytest.raises(ResearchError, match="No successful research results"):
            research_system_with_mocks._synthesize_results("Test query", failed_results)
    
    def test_synthesize_results_api_error(self, research_system_with_mocks, sample_research_results):
        """Test synthesis with API error."""
        research_system_with_mocks.client.messages.create.side_effect = Exception("API Error")
        
        with pytest.raises(ResearchError, match="Result synthesis failed"):
            research_system_with_mocks._synthesize_results("Test query", sample_research_results)
    
    def test_format_findings(self, research_system_with_mocks, sample_research_results):
        """Test formatting of research findings."""
        result = research_system_with_mocks._format_findings(sample_research_results)
        
        assert "Research Area 1:" in result
        assert "Research Area 2:" in result
        assert sample_research_results[0]["subtask"] in result
        assert sample_research_results[1]["subtask"] in result


class TestFullResearchWorkflow:
    """Test cases for the complete research workflow."""
    
    def test_conduct_research_success(self, research_system_with_mocks, decomposition_response, research_response, synthesis_response):
        """Test complete successful research workflow."""
        # Setup mock responses in sequence
        mock_responses = [
            MagicMock(),  # Decomposition
            MagicMock(),  # Research 1
            MagicMock(),  # Research 2  
            MagicMock(),  # Research 3
            MagicMock(),  # Research 4
            MagicMock(),  # Synthesis
        ]
        
        mock_responses[0].content[0].text = decomposition_response
        for i in range(1, 5):
            mock_responses[i].content[0].text = research_response
        mock_responses[5].content[0].text = synthesis_response
        
        research_system_with_mocks.client.messages.create.side_effect = mock_responses
        
        result = research_system_with_mocks.conduct_research("What are the benefits of renewable energy?")
        
        assert result["query"] == "What are the benefits of renewable energy?"
        assert result["total_subtasks"] == 4
        assert len(result["subtasks"]) == 4
        assert len(result["research_results"]) == 4
        assert result["final_report"] == synthesis_response
        assert result["orchestrator_model"] == "claude-3-opus-20240229"
        assert result["research_model"] == "claude-3-5-sonnet-20241022"
        
        # Verify correct number of API calls (1 decomposition + 4 research + 1 synthesis)
        assert research_system_with_mocks.client.messages.create.call_count == 6
    
    def test_conduct_research_empty_query(self, research_system_with_mocks):
        """Test research with empty query."""
        with pytest.raises(ResearchError, match="Query cannot be empty"):
            research_system_with_mocks.conduct_research("")
    
    def test_conduct_research_whitespace_query(self, research_system_with_mocks):
        """Test research with whitespace-only query."""
        with pytest.raises(ResearchError, match="Query cannot be empty"):
            research_system_with_mocks.conduct_research("   ")
    
    def test_conduct_research_decomposition_failure(self, research_system_with_mocks):
        """Test research workflow when decomposition fails."""
        research_system_with_mocks.client.messages.create.side_effect = Exception("Decomposition failed")
        
        with pytest.raises(ResearchError, match="Research process failed"):
            research_system_with_mocks.conduct_research("Test query")


class TestSystemInfo:
    """Test cases for system information functionality."""
    
    def test_get_system_info(self, research_system_with_mocks):
        """Test getting system information."""
        info = research_system_with_mocks.get_system_info()
        
        expected_keys = ["orchestrator_model", "research_model", "max_subtasks", "api_configured", "version", "architecture"]
        
        for key in expected_keys:
            assert key in info
        
        assert info["orchestrator_model"] == "claude-3-opus-20240229"
        assert info["research_model"] == "claude-3-5-sonnet-20241022"
        assert info["max_subtasks"] == 4
        assert info["api_configured"] is True
        assert info["version"] == "1.0.0"
        assert "Anthropic-inspired" in info["architecture"]


class TestValidationAndErrorHandling:
    """Test cases for validation and error handling."""
    
    def test_research_error_creation(self):
        """Test ResearchError exception creation."""
        error = ResearchError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_build_decomposition_prompt(self, research_system_with_mocks):
        """Test decomposition prompt building."""
        query = "Test research query"
        prompt = research_system_with_mocks._build_decomposition_prompt(query)
        
        assert query in prompt
        assert "3-4 specific subtasks" in prompt
        assert "numbered list" in prompt
        assert "Format your response" in prompt
    
    def test_build_synthesis_prompt(self, research_system_with_mocks):
        """Test synthesis prompt building."""
        query = "Test query"
        findings = "Test findings"
        prompt = research_system_with_mocks._build_synthesis_prompt(query, findings)
        
        assert query in prompt
        assert findings in prompt
        assert "Executive Summary" in prompt
        assert "Key Findings" in prompt
        assert "Detailed Analysis" in prompt
        assert "Conclusions" in prompt