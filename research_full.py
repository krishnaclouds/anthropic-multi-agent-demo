#!/usr/bin/env python3

import asyncio
from src.research_system_simple import SimpleResearchSystem

async def demo_research_system():
    print("🔬 Multi-Agent Research System Demo (Fixed)")
    print("=" * 50)
    
    try:
        research_system = SimpleResearchSystem()
        print("✅ System initialized successfully")
        
        demo_queries = [
            "What are the latest developments in renewable energy storage technologies?",
            "How do multi-agent AI systems compare to single-agent approaches?",
            "What are the key challenges in implementing sustainable urban transportation?"
        ]
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n🔍 Demo Query {i}: {query}")
            print("-" * 60)
            
            try:
                print("🔄 Researching...")
                # Run the synchronous method in an async context
                results = await asyncio.get_event_loop().run_in_executor(
                    None, research_system.conduct_research, query
                )
                
                print(f"📊 Research Results:")
                print(f"Subtasks completed: {results['total_subtasks']}")
                
                final_report = results.get('final_report', 'No report generated')
                print(f"\n📝 Executive Summary:")
                print(final_report[:500] + "..." if len(final_report) > 500 else final_report)
                
                print(f"\n📝 Subtasks Researched:")
                for j, subtask in enumerate(results.get('subtasks', []), 1):
                    print(f"  {j}. {subtask[:80]}...")
                
            except Exception as e:
                print(f"❌ Error during research: {str(e)}")
        
        print(f"\n📈 Demo completed successfully!")
        print(f"Processed {len(demo_queries)} research queries")
        
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        print("💡 Make sure to set your ANTHROPIC_API_KEY in .env file")
    except Exception as e:
        print(f"❌ System error: {str(e)}")

async def run_interactive_demo():
    print("🎯 Interactive Research Demo (Fixed)")
    print("Enter your research queries (type 'quit' to exit)")
    
    try:
        research_system = SimpleResearchSystem()
        
        while True:
            query = input("\n🔍 Research query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            try:
                print("🔄 Researching...")
                # Run the synchronous method in an async context
                results = await asyncio.get_event_loop().run_in_executor(
                    None, research_system.conduct_research, query
                )
                
                print(f"\n📋 Results:")
                final_report = results.get('final_report', 'No report available')
                print(final_report)
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        print("💡 Create a .env file with your ANTHROPIC_API_KEY")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(run_interactive_demo())
    else:
        asyncio.run(demo_research_system())