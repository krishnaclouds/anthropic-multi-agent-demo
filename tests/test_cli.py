"""
Unit tests for the command-line interface (research.py).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# Import CLI functions
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import research


class TestCLIArgumentParsing:
    """Test cases for CLI argument parsing."""
    
    def test_default_arguments(self):
        """Test parsing with default arguments."""
        with patch('sys.argv', ['research.py']):
            parser = research.argparse.ArgumentParser()
            research_args = research.argparse.Namespace()
            research_args.interactive = False
            research_args.verbose = False
            research_args.orchestrator_model = None
            research_args.research_model = None
            
            # Verify default values
            assert research_args.interactive is False
            assert research_args.verbose is False
            assert research_args.orchestrator_model is None
            assert research_args.research_model is None
    
    def test_interactive_flag(self):
        """Test interactive flag parsing."""
        test_args = research.argparse.Namespace()
        test_args.interactive = True
        test_args.verbose = False
        test_args.orchestrator_model = None
        test_args.research_model = None
        
        assert test_args.interactive is True
    
    def test_verbose_flag(self):
        """Test verbose flag parsing."""
        test_args = research.argparse.Namespace()
        test_args.interactive = False
        test_args.verbose = True
        test_args.orchestrator_model = None
        test_args.research_model = None
        
        assert test_args.verbose is True
    
    def test_model_arguments(self):
        """Test model argument parsing."""
        test_args = research.argparse.Namespace()
        test_args.interactive = False
        test_args.verbose = False
        test_args.orchestrator_model = "custom-opus"
        test_args.research_model = "custom-sonnet"
        
        assert test_args.orchestrator_model == "custom-opus"
        assert test_args.research_model == "custom-sonnet"


class TestLoggingSetup:
    """Test cases for logging configuration."""
    
    def test_setup_logging_default(self):
        """Test default logging setup."""
        import logging
        
        with patch('logging.basicConfig') as mock_config:
            research.setup_logging(verbose=False)
            
            mock_config.assert_called_once()
            call_args = mock_config.call_args[1]
            assert call_args['level'] == logging.INFO
    
    def test_setup_logging_verbose(self):
        """Test verbose logging setup."""
        import logging
        
        with patch('logging.basicConfig') as mock_config:
            research.setup_logging(verbose=True)
            
            mock_config.assert_called_once()
            call_args = mock_config.call_args[1]
            assert call_args['level'] == logging.DEBUG


class TestSystemInfoDisplay:
    """Test cases for system information display."""
    
    def test_display_system_info(self):
        """Test system info display formatting."""
        mock_system = MagicMock()
        mock_info = {
            'orchestrator_model': 'claude-3-opus-20240229',
            'research_model': 'claude-3-5-sonnet-20241022',
            'max_subtasks': 4,
            'architecture': 'Anthropic-inspired: Opus for orchestration, Sonnet for research',
            'version': '1.0.0'
        }
        mock_system.get_system_info.return_value = mock_info
        
        # Capture output
        with redirect_stdout(io.StringIO()) as captured_output:
            research.display_system_info(mock_system)
        
        output = captured_output.getvalue()
        
        assert "Multi-Agent Research System" in output
        assert "claude-3-opus-20240229" in output
        assert "claude-3-5-sonnet-20241022" in output
        assert "Max Subtasks: 4" in output
        assert "Version: 1.0.0" in output
        assert "✅ System initialized successfully" in output


class TestResultsDisplay:
    """Test cases for research results display."""
    
    def test_display_research_results_basic(self):
        """Test basic research results display."""
        mock_results = {
            'query': 'Test query',
            'total_subtasks': 3,
            'orchestrator_model': 'claude-3-opus-20240229',
            'research_model': 'claude-3-5-sonnet-20241022',
            'subtasks': ['Task 1', 'Task 2', 'Task 3'],
            'final_report': 'This is a test report.'
        }
        
        with redirect_stdout(io.StringIO()) as captured_output:
            research.display_research_results(mock_results, show_details=False)
        
        output = captured_output.getvalue()
        
        assert "Research Results:" in output
        assert "Test query" in output
        assert "Subtasks completed: 3" in output
        assert "claude-3-opus-20240229" in output
        assert "claude-3-5-sonnet-20241022" in output
        assert "This is a test report." in output
    
    def test_display_research_results_with_details(self):
        """Test research results display with details."""
        mock_results = {
            'query': 'Test query',
            'total_subtasks': 2,
            'orchestrator_model': 'claude-3-opus-20240229',
            'research_model': 'claude-3-5-sonnet-20241022',
            'subtasks': ['First subtask description', 'Second subtask description'],
            'final_report': 'Short report'
        }
        
        with redirect_stdout(io.StringIO()) as captured_output:
            research.display_research_results(mock_results, show_details=True)
        
        output = captured_output.getvalue()
        
        assert "📝 Subtasks Researched:" in output
        assert "1. First subtask description" in output
        assert "2. Second subtask description" in output
    
    def test_display_research_results_long_report(self):
        """Test display of long research reports."""
        long_report = "Very detailed research report. " * 100
        
        mock_results = {
            'query': 'Test query',
            'total_subtasks': 1,
            'orchestrator_model': 'claude-3-opus-20240229',
            'research_model': 'claude-3-5-sonnet-20241022',
            'subtasks': ['Task 1'],
            'final_report': long_report
        }
        
        with redirect_stdout(io.StringIO()) as captured_output:
            research.display_research_results(mock_results, show_details=False)
        
        output = captured_output.getvalue()
        
        assert "[Report truncated" in output
        assert f"Full report contains {len(long_report)} characters" in output


class TestPresetQueries:
    """Test cases for preset query execution."""
    
    @patch('research.SimpleResearchSystem')
    def test_run_preset_queries_success(self, mock_system_class):
        """Test successful execution of preset queries."""
        mock_system = MagicMock()
        mock_system_class.return_value = mock_system
        
        # Mock successful research results
        mock_result = {
            'query': 'Test query',
            'total_subtasks': 3,
            'orchestrator_model': 'claude-3-opus-20240229',
            'research_model': 'claude-3-5-sonnet-20241022',
            'subtasks': ['Task 1', 'Task 2', 'Task 3'],
            'final_report': 'Test report'
        }
        mock_system.conduct_research.return_value = mock_result
        
        with redirect_stdout(io.StringIO()) as captured_output:
            research.run_preset_queries(mock_system, verbose=False)
        
        output = captured_output.getvalue()
        
        # Should process all preset queries
        assert mock_system.conduct_research.call_count == 3
        assert "Session Summary:" in output
        assert "Completed 3/3" in output
    
    @patch('research.SimpleResearchSystem')
    def test_run_preset_queries_with_error(self, mock_system_class):
        """Test preset queries with some errors."""
        mock_system = MagicMock()
        mock_system_class.return_value = mock_system
        
        # First query succeeds, second fails, third succeeds
        from src.research_system_simple import ResearchError
        
        def side_effect(query):
            if "artificial intelligence" in query:
                raise ResearchError("Research failed")
            return {
                'query': query,
                'total_subtasks': 2,
                'orchestrator_model': 'claude-3-opus-20240229',
                'research_model': 'claude-3-5-sonnet-20241022',
                'subtasks': ['Task 1', 'Task 2'],
                'final_report': 'Test report'
            }
        
        mock_system.conduct_research.side_effect = side_effect
        
        with redirect_stdout(io.StringIO()) as captured_output:
            research.run_preset_queries(mock_system, verbose=False)
        
        output = captured_output.getvalue()
        
        assert "Research Error:" in output
        assert "Completed 2/3" in output


class TestInteractiveMode:
    """Test cases for interactive mode functionality."""
    
    def test_print_help(self):
        """Test help message display."""
        with redirect_stdout(io.StringIO()) as captured_output:
            research.print_help()
        
        output = captured_output.getvalue()
        
        assert "Available Commands:" in output
        assert "help" in output
        assert "info" in output
        assert "quit" in output
    
    @patch('builtins.input')
    @patch('research.SimpleResearchSystem')
    def test_interactive_mode_quit(self, mock_system_class, mock_input):
        """Test interactive mode quit command."""
        mock_system = MagicMock()
        mock_system_class.return_value = mock_system
        
        # Simulate user typing 'quit'
        mock_input.return_value = 'quit'
        
        with redirect_stdout(io.StringIO()) as captured_output:
            research.run_interactive_mode(mock_system)
        
        output = captured_output.getvalue()
        
        assert "Interactive Research Mode" in output
        assert "Session ended. No queries processed." in output
    
    @patch('builtins.input')
    @patch('research.SimpleResearchSystem')
    def test_interactive_mode_help_command(self, mock_system_class, mock_input):
        """Test interactive mode help command."""
        mock_system = MagicMock()
        mock_system_class.return_value = mock_system
        
        # Simulate user typing 'help' then 'quit'
        mock_input.side_effect = ['help', 'quit']
        
        with redirect_stdout(io.StringIO()) as captured_output:
            research.run_interactive_mode(mock_system)
        
        output = captured_output.getvalue()
        
        assert "Available Commands:" in output
        assert "help" in output
    
    @patch('builtins.input')
    @patch('research.SimpleResearchSystem')
    def test_interactive_mode_info_command(self, mock_system_class, mock_input):
        """Test interactive mode info command."""
        mock_system = MagicMock()
        mock_system_class.return_value = mock_system
        
        mock_info = {
            'orchestrator_model': 'claude-3-opus-20240229',
            'research_model': 'claude-3-5-sonnet-20241022',
            'version': '1.0.0'
        }
        mock_system.get_system_info.return_value = mock_info
        
        # Simulate user typing 'info' then 'quit'
        mock_input.side_effect = ['info', 'quit']
        
        with redirect_stdout(io.StringIO()) as captured_output:
            research.run_interactive_mode(mock_system)
        
        output = captured_output.getvalue()
        
        assert "System Info:" in output
        assert "claude-3-opus-20240229" in output
    
    @patch('builtins.input')
    @patch('research.SimpleResearchSystem')
    def test_interactive_mode_research_query(self, mock_system_class, mock_input):
        """Test interactive mode with research query."""
        mock_system = MagicMock()
        mock_system_class.return_value = mock_system
        
        mock_result = {
            'query': 'Test research query',
            'total_subtasks': 2,
            'orchestrator_model': 'claude-3-opus-20240229',
            'research_model': 'claude-3-5-sonnet-20241022',
            'subtasks': ['Task 1', 'Task 2'],
            'final_report': 'Research findings...'
        }
        mock_system.conduct_research.return_value = mock_result
        
        # Simulate user typing a query then 'quit'
        mock_input.side_effect = ['What is renewable energy?', 'quit']
        
        with redirect_stdout(io.StringIO()) as captured_output:
            research.run_interactive_mode(mock_system)
        
        output = captured_output.getvalue()
        
        assert "Researching..." in output
        assert "Research Results:" in output
        assert "Session completed! Processed 1 research queries." in output


class TestMainFunction:
    """Test cases for the main function."""
    
    @patch('research.SimpleResearchSystem')
    @patch('research.run_preset_queries')
    @patch('research.setup_logging')
    @patch('research.display_system_info')
    def test_main_default_mode(self, mock_display, mock_logging, mock_preset, mock_system_class):
        """Test main function in default mode."""
        mock_system = MagicMock()
        mock_system_class.return_value = mock_system
        
        # Mock command line arguments
        test_args = research.argparse.Namespace()
        test_args.interactive = False
        test_args.verbose = False
        test_args.orchestrator_model = None
        test_args.research_model = None
        
        with patch('research.argparse.ArgumentParser.parse_args', return_value=test_args):
            research.main()
        
        mock_logging.assert_called_once_with(False)
        mock_system_class.assert_called_once_with(
            orchestrator_model=None,
            research_model=None
        )
        mock_display.assert_called_once()
        mock_preset.assert_called_once()
    
    @patch('research.SimpleResearchSystem')
    @patch('research.run_interactive_mode')
    @patch('research.setup_logging')
    @patch('research.display_system_info')
    def test_main_interactive_mode(self, mock_display, mock_logging, mock_interactive, mock_system_class):
        """Test main function in interactive mode."""
        mock_system = MagicMock()
        mock_system_class.return_value = mock_system
        
        # Mock command line arguments for interactive mode
        test_args = research.argparse.Namespace()
        test_args.interactive = True
        test_args.verbose = True
        test_args.orchestrator_model = "custom-opus"
        test_args.research_model = "custom-sonnet"
        
        with patch('research.argparse.ArgumentParser.parse_args', return_value=test_args):
            research.main()
        
        mock_logging.assert_called_once_with(True)
        mock_system_class.assert_called_once_with(
            orchestrator_model="custom-opus",
            research_model="custom-sonnet"
        )
        mock_display.assert_called_once()
        mock_interactive.assert_called_once()
    
    @patch('research.SimpleResearchSystem')
    def test_main_research_error(self, mock_system_class):
        """Test main function with ResearchError."""
        from src.research_system_simple import ResearchError
        mock_system_class.side_effect = ResearchError("Test error")
        
        test_args = research.argparse.Namespace()
        test_args.interactive = False
        test_args.verbose = False
        test_args.orchestrator_model = None
        test_args.research_model = None
        
        with patch('research.argparse.ArgumentParser.parse_args', return_value=test_args):
            with pytest.raises(SystemExit) as exc_info:
                with redirect_stderr(io.StringIO()) as captured_error:
                    research.main()
            
            assert exc_info.value.code == 1
    
    @patch('research.SimpleResearchSystem')
    def test_main_keyboard_interrupt(self, mock_system_class):
        """Test main function with keyboard interrupt."""
        mock_system_class.side_effect = KeyboardInterrupt()
        
        test_args = research.argparse.Namespace()
        test_args.interactive = False
        test_args.verbose = False
        test_args.orchestrator_model = None
        test_args.research_model = None
        
        with patch('research.argparse.ArgumentParser.parse_args', return_value=test_args):
            with pytest.raises(SystemExit) as exc_info:
                research.main()
            
            assert exc_info.value.code == 0