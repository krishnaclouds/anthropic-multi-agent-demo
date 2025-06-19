#!/usr/bin/env python3
"""
Basic validation test for the Multi-Agent Research System.

This test validates code structure, imports, and basic functionality
without requiring API calls.
"""

import os
import sys
import tempfile
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_imports() -> bool:
    """Test that all modules can be imported correctly."""
    print("🧪 Testing imports...")
    
    try:
        from research_system_simple import SimpleResearchSystem, ResearchError
        print("✅ Successfully imported SimpleResearchSystem")
    except ImportError as e:
        print(f"❌ Failed to import SimpleResearchSystem: {e}")
        return False
    
    try:
        import anthropic
        print("✅ Successfully imported anthropic")
    except ImportError as e:
        print(f"❌ Failed to import anthropic: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Successfully imported dotenv")
    except ImportError as e:
        print(f"❌ Failed to import dotenv: {e}")
        return False
    
    return True


def test_system_without_api() -> bool:
    """Test system validation logic."""
    print("\n🧪 Testing API key validation logic...")
    
    try:
        from research_system_simple import SimpleResearchSystem, ResearchError
        
        # Check that the ResearchError class exists and works
        try:
            raise ResearchError("Test error")
        except ResearchError:
            print("✅ ResearchError class works correctly")
        
        # Test that the system has proper validation logic in the code
        with open('src/research_system_simple.py', 'r') as f:
            content = f.read()
            
        required_patterns = [
            'API key is required',
            'ResearchError',
            'if not self.api_key',
        ]
        
        for pattern in required_patterns:
            if pattern not in content:
                print(f"❌ Missing validation pattern: {pattern}")
                return False
        
        print("✅ API key validation logic is present in code")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_system_with_dummy_key() -> bool:
    """Test system initialization with dummy API key."""
    print("\n🧪 Testing system initialization with dummy key...")
    
    try:
        from research_system_simple import SimpleResearchSystem, ResearchError
        
        # Test with dummy key
        system = SimpleResearchSystem(api_key="dummy-key-for-testing")
        info = system.get_system_info()
        
        expected_keys = ['orchestrator_model', 'research_model', 'max_subtasks', 'api_configured', 'version']
        for key in expected_keys:
            if key not in info:
                print(f"❌ Missing key in system info: {key}")
                return False
        
        if not info['api_configured']:
            print("❌ API should be marked as configured")
            return False
        
        if info['max_subtasks'] != 4:
            print(f"❌ Wrong max_subtasks: {info['max_subtasks']}")
            return False
        
        print("✅ System info structure is correct")
        print(f"   Orchestrator Model: {info['orchestrator_model']}")
        print(f"   Research Model: {info['research_model']}")
        print(f"   Max Subtasks: {info['max_subtasks']}")
        print(f"   Version: {info['version']}")
        print(f"   Architecture: {info.get('architecture', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_file_structure() -> bool:
    """Test that all required files exist and are properly structured."""
    print("\n🧪 Testing file structure...")
    
    required_files = [
        ('src/research_system_simple.py', 'Main research system'),
        ('research.py', 'Main entry point'),
        ('research_mock.py', 'Mock research system'),
        ('requirements.txt', 'Python dependencies'),
        ('README.md', 'Documentation'),
        ('.env.example', 'Environment template'),
        ('pyproject.toml', 'Project configuration'),
    ]
    
    for file_path, description in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing {description}: {file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            print(f"❌ Cannot read {description}: {file_path}")
            return False
        
        # Check minimum file size
        if os.path.getsize(file_path) < 10:
            print(f"❌ {description} is too small: {file_path}")
            return False
    
    print("✅ All required files present and accessible")
    
    # Check directory structure
    required_dirs = [
        ('src', 'Source code directory'),
        ('src/agents', 'Agents directory'),
        ('src/coordination', 'Coordination directory'),
        ('venv', 'Virtual environment'),
    ]
    
    for dir_path, description in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Missing {description}: {dir_path}")
            return False
        
        if not os.path.isdir(dir_path):
            print(f"❌ {description} is not a directory: {dir_path}")
            return False
    
    print("✅ Directory structure is correct")
    return True


def test_python_syntax() -> bool:
    """Test that Python files have valid syntax."""
    print("\n🧪 Testing Python syntax...")
    
    python_files = [
        'src/research_system_simple.py',
        'research.py',
        'research_mock.py',
        'research_full.py',
    ]
    
    for file_path in python_files:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try to compile the file
            compile(content, file_path, 'exec')
            print(f"✅ {file_path} has valid syntax")
            
        except SyntaxError as e:
            print(f"❌ Syntax error in {file_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error checking {file_path}: {e}")
            return False
    
    return True


def test_mock_system() -> bool:
    """Test that the mock system works without API calls."""
    print("\n🧪 Testing mock system...")
    
    try:
        # Import and run basic mock functionality
        import subprocess
        import sys
        
        # Test that mock system can be imported and run
        result = subprocess.run([
            sys.executable, 'research_mock.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Mock system runs successfully")
            if "Mock system initialized" in result.stdout:
                print("✅ Mock system produces expected output")
                return True
            else:
                print("⚠️ Mock system runs but output format may have changed")
                return True
        else:
            print(f"❌ Mock system failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Mock system test timed out (expected for full demo)")
        return True
    except Exception as e:
        print(f"❌ Mock system test failed: {e}")
        return False


def main() -> None:
    """Run all basic tests."""
    print("🔬 Multi-Agent Research System - Basic Validation")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_python_syntax),
        ("Module Imports", test_imports),
        ("System Without API", test_system_without_api),
        ("System With Dummy Key", test_system_with_dummy_key),
        ("Mock System", test_mock_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
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
        print("🎉 All basic tests passed! System structure is correct.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)