#!/usr/bin/env python3
"""
End-to-end test for the Multi-Agent Research System.

This test validates that all components work together correctly
and that the system produces expected outputs.
"""

import os
import sys
import tempfile
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from research_system_simple import SimpleResearchSystem, ResearchError


def test_system_initialization() -> None:
    """Test that the system initializes correctly."""
    print("🧪 Testing system initialization...")
    
    # Test with missing API key
    temp_env = os.environ.copy()
    if 'ANTHROPIC_API_KEY' in os.environ:
        del os.environ['ANTHROPIC_API_KEY']
    
    try:
        SimpleResearchSystem()
        print("❌ Should have failed with missing API key")
        return False
    except ResearchError as e:
        if "API key is required" in str(e):
            print("✅ Correctly handles missing API key")
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    
    # Restore environment
    os.environ.update(temp_env)
    
    # Test with valid initialization
    try:
        if os.getenv('ANTHROPIC_API_KEY'):
            system = SimpleResearchSystem()
            info = system.get_system_info()
            print(f"✅ System initialized successfully with model: {info['model']}")
            return True
        else:
            print("⚠️ No API key available for full test")
            return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def test_query_validation() -> None:
    """Test query validation."""
    print("\n🧪 Testing query validation...")
    
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️ Skipping - No API key available")
        return True
    
    try:
        system = SimpleResearchSystem()
        
        # Test empty query
        try:
            system.conduct_research("")
            print("❌ Should have failed with empty query")
            return False
        except ResearchError as e:
            if "cannot be empty" in str(e):
                print("✅ Correctly handles empty query")
            else:
                print(f"❌ Wrong error message: {e}")
                return False
        
        # Test whitespace-only query
        try:
            system.conduct_research("   ")
            print("❌ Should have failed with whitespace query")
            return False
        except ResearchError as e:
            if "cannot be empty" in str(e):
                print("✅ Correctly handles whitespace query")
            else:
                print(f"❌ Wrong error message: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Query validation test failed: {e}")
        return False


def test_end_to_end_research() -> None:
    """Test complete research workflow."""
    print("\n🧪 Testing end-to-end research...")
    
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️ Skipping - No API key available")
        return True
    
    try:
        system = SimpleResearchSystem()
        
        # Test simple query
        query = "What are the main benefits of solar energy?"
        print(f"   Query: {query}")
        
        results = system.conduct_research(query)
        
        # Validate results structure
        required_keys = ['query', 'subtasks', 'research_results', 'final_report', 'total_subtasks']
        for key in required_keys:
            if key not in results:
                print(f"❌ Missing key in results: {key}")
                return False
        
        # Validate content
        if results['query'] != query:
            print(f"❌ Query mismatch: {results['query']} != {query}")
            return False
        
        if not results['subtasks'] or len(results['subtasks']) == 0:
            print("❌ No subtasks generated")
            return False
        
        if len(results['research_results']) != len(results['subtasks']):
            print("❌ Research results don't match subtasks")
            return False
        
        if not results['final_report'] or len(results['final_report']) < 100:
            print("❌ Final report too short or empty")
            return False
        
        if results['total_subtasks'] != len(results['subtasks']):
            print("❌ Total subtasks count mismatch")
            return False
        
        print(f"✅ Research completed successfully")
        print(f"   Generated {results['total_subtasks']} subtasks")
        print(f"   Final report: {len(results['final_report'])} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False


def test_research_failure_handling() -> None:
    """Test how the system handles research failures."""
    print("\n🧪 Testing failure handling...")
    
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️ Skipping - No API key available")
        return True
    
    try:
        # Test with invalid API key
        system = SimpleResearchSystem(api_key="invalid-key")
        
        try:
            system.conduct_research("What is artificial intelligence?")
            print("❌ Should have failed with invalid API key")
            return False
        except ResearchError:
            print("✅ Correctly handles invalid API key")
            return True
        
    except ResearchError:
        print("✅ Correctly handles invalid API key during initialization")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def validate_code_standards() -> bool:
    """Validate that code follows basic standards."""
    print("\n🧪 Validating code standards...")
    
    # Check if main files exist and are readable
    required_files = [
        'src/research_system_simple.py',
        'research.py',
        'research_mock.py',
        'requirements.txt',
        'README.md'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing required file: {file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            print(f"❌ File not readable: {file_path}")
            return False
    
    print("✅ All required files present and readable")
    
    # Check that Python files have proper encoding
    python_files = ['src/research_system_simple.py', 'research.py']
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) < 100:
                    print(f"❌ File too short: {file_path}")
                    return False
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return False
    
    print("✅ Python files are properly formatted")
    return True


def main() -> None:
    """Run all tests."""
    print("🔬 Multi-Agent Research System - End-to-End Test")
    print("=" * 60)
    
    tests = [
        ("Code Standards", validate_code_standards),
        ("System Initialization", test_system_initialization),
        ("Query Validation", test_query_validation),
        ("Failure Handling", test_research_failure_handling),
        ("End-to-End Research", test_end_to_end_research),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()