#!/usr/bin/env python3
"""
Multi-Agent Research System - Main Entry Point

A fast and reliable research system that conducts comprehensive analysis
by decomposing queries into subtasks and synthesizing results.
"""

import argparse
import logging
import sys
from typing import List

from src.research_system_simple import SimpleResearchSystem, ResearchError

# Configure module logger
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def display_system_info(research_system: SimpleResearchSystem) -> None:
    """Display system information."""
    info = research_system.get_system_info()
    print("🔬 Multi-Agent Research System")
    print("=" * 50)
    print(f"Model: {info['model']}")
    print(f"Max Subtasks: {info['max_subtasks']}")
    print(f"Version: {info['version']}")
    print("✅ System initialized successfully\n")


def display_research_results(results: dict, show_details: bool = True) -> None:
    """Display research results in a formatted manner."""
    print(f"📊 Research Results:")
    print(f"Query: {results['query']}")
    print(f"Subtasks completed: {results['total_subtasks']}")
    print(f"Model used: {results['model_used']}")
    
    if show_details:
        print(f"\n📝 Subtasks Researched:")
        for i, subtask in enumerate(results['subtasks'], 1):
            print(f"  {i}. {subtask[:80]}{'...' if len(subtask) > 80 else ''}")
    
    print(f"\n📋 Final Report:")
    final_report = results.get('final_report', 'No report generated')
    
    # Display first 800 characters with proper truncation
    if len(final_report) > 800:
        print(final_report[:800] + "...")
        print(f"\n[Report truncated - Full report contains {len(final_report)} characters]")
    else:
        print(final_report)


def run_preset_queries(research_system: SimpleResearchSystem, verbose: bool = False) -> None:
    """Run research on preset demonstration queries."""
    demo_queries = [
        "What are the benefits of renewable energy adoption?",
        "How does artificial intelligence impact modern education?",
        "What are the key challenges in sustainable urban development?"
    ]
    
    successful_queries = 0
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔍 Research Query {i}: {query}")
        print("-" * 60)
        
        try:
            print("🔄 Researching...")
            results = research_system.conduct_research(query)
            display_research_results(results, show_details=verbose)
            successful_queries += 1
            
        except ResearchError as e:
            print(f"❌ Research Error: {e}")
        except KeyboardInterrupt:
            print("\n⚠️ Research interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            logging.error(f"Unexpected error during research: {e}", exc_info=True)
    
    print(f"\n📈 Session Summary:")
    print(f"Completed {successful_queries}/{len(demo_queries)} research queries successfully")


def run_interactive_mode(research_system: SimpleResearchSystem) -> None:
    """Run the system in interactive mode."""
    print("🎯 Interactive Research Mode")
    print("Enter your research queries (type 'quit', 'exit', or 'q' to stop)")
    print("Type 'help' for available commands")
    
    query_count = 0
    
    while True:
        try:
            query = input("\n🔍 Research query: ").strip()
            
            if not query:
                continue
                
            # Handle special commands
            if query.lower() in ['quit', 'exit', 'q']:
                break
            elif query.lower() == 'help':
                print_help()
                continue
            elif query.lower() == 'info':
                info = research_system.get_system_info()
                print(f"System Info: {info}")
                continue
            
            # Conduct research
            print("🔄 Researching...")
            results = research_system.conduct_research(query)
            display_research_results(results, show_details=False)
            query_count += 1
            
        except ResearchError as e:
            print(f"❌ Research Error: {e}")
        except KeyboardInterrupt:
            print("\n\n👋 Research session ended")
            break
        except EOFError:
            print("\n\n👋 Research session ended")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            logging.error(f"Unexpected error in interactive mode: {e}", exc_info=True)
    
    if query_count > 0:
        print(f"\n📈 Session completed! Processed {query_count} research queries.")
    else:
        print("\n📈 Session ended. No queries processed.")


def print_help() -> None:
    """Print help information for interactive mode."""
    print("\n📚 Available Commands:")
    print("  help  - Show this help message")
    print("  info  - Show system information")
    print("  quit  - Exit the program")
    print("\nSimply type your research question to start researching!")


def main() -> None:
    """Main entry point for the research system."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Research System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python research.py                    # Run preset demo queries
  python research.py --interactive      # Interactive research mode
  python research.py --verbose          # Show detailed logging
        """
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode for custom queries'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging and detailed output'
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        help='Specify Claude model to use (default: claude-3-5-sonnet-20241022)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        # Initialize research system
        research_system = SimpleResearchSystem(model=args.model)
        display_system_info(research_system)
        
        # Run in appropriate mode
        if args.interactive:
            run_interactive_mode(research_system)
        else:
            run_preset_queries(research_system, verbose=args.verbose)
            
    except ResearchError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Make sure to set your ANTHROPIC_API_KEY in the .env file")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()