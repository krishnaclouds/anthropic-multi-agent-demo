#!/usr/bin/env python3
"""
Code Standards Validation Script

Validates that the Multi-Agent Research System follows proper coding standards:
- PEP 8 compliance
- Type hints
- Docstrings
- Error handling
- Logging
"""

import ast
import os
import re
from typing import List, Tuple, Dict, Any


def check_file_docstrings(file_path: str) -> Tuple[bool, List[str]]:
    """Check if a Python file has proper docstrings."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Check module docstring
        if not ast.get_docstring(tree):
            issues.append("Missing module docstring")
        
        # Check class and function docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):  # Public functions
                    if not ast.get_docstring(node):
                        issues.append(f"Missing docstring for function: {node.name}")
            
            elif isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    issues.append(f"Missing docstring for class: {node.name}")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Error parsing file: {e}"]


def check_type_hints(file_path: str) -> Tuple[bool, List[str]]:
    """Check if a Python file has proper type hints."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):  # Public functions
                    # Check return type annotation
                    if not node.returns:
                        issues.append(f"Missing return type hint for function: {node.name}")
                    
                    # Check parameter type annotations
                    for arg in node.args.args:
                        if arg.arg != 'self' and not arg.annotation:
                            issues.append(f"Missing type hint for parameter '{arg.arg}' in function: {node.name}")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Error parsing file: {e}"]


def check_error_handling(file_path: str) -> Tuple[bool, List[str]]:
    """Check if a Python file has proper error handling."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for basic error handling patterns
        if 'try:' not in content:
            issues.append("No try-catch blocks found")
        
        if 'except Exception' in content and 'except' not in content.replace('except Exception', ''):
            issues.append("Only catching generic Exception, consider specific exceptions")
        
        # Check for custom exceptions
        if 'Error' in os.path.basename(file_path) or 'system' in file_path:
            if 'class' in content and 'Error' in content and 'Exception' in content:
                pass  # Has custom exception
            else:
                issues.append("Consider defining custom exceptions")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Error reading file: {e}"]


def check_logging(file_path: str) -> Tuple[bool, List[str]]:
    """Check if a Python file has proper logging."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for logging import and usage
        if 'import logging' not in content:
            if 'print(' in content and ('error' in content.lower() or 'warning' in content.lower()):
                issues.append("Consider using logging instead of print for errors/warnings")
        else:
            if 'logger' not in content:
                issues.append("Logging imported but no logger instance found")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Error reading file: {e}"]


def check_code_structure(file_path: str) -> Tuple[bool, List[str]]:
    """Check general code structure and organization."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check line length (relaxed PEP 8 - 100 chars)
        for i, line in enumerate(lines, 1):
            if len(line.rstrip()) > 100:
                issues.append(f"Line {i} exceeds 100 characters")
        
        # Check for proper imports organization
        import_section_ended = False
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                if import_section_ended:
                    issues.append(f"Import on line {i} should be at the top of the file")
            elif line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""'):
                import_section_ended = True
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Error reading file: {e}"]


def validate_file(file_path: str) -> Dict[str, Any]:
    """Validate a single Python file against coding standards."""
    print(f"\n📝 Validating: {file_path}")
    
    results = {
        'file': file_path,
        'total_checks': 0,
        'passed_checks': 0,
        'issues': []
    }
    
    checks = [
        ("Docstrings", check_file_docstrings),
        ("Type Hints", check_type_hints),
        ("Error Handling", check_error_handling),
        ("Logging", check_logging),
        ("Code Structure", check_code_structure),
    ]
    
    for check_name, check_func in checks:
        results['total_checks'] += 1
        passed, issues = check_func(file_path)
        
        if passed:
            results['passed_checks'] += 1
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            for issue in issues:
                print(f"    - {issue}")
                results['issues'].append(f"{check_name}: {issue}")
    
    return results


def main() -> None:
    """Main validation function."""
    print("🔍 Multi-Agent Research System - Code Standards Validation")
    print("=" * 70)
    
    # Python files to validate
    python_files = [
        'src/research_system_simple.py',
        'research.py',
        'research_mock.py',
    ]
    
    all_results = []
    total_files = 0
    files_passed = 0
    
    for file_path in python_files:
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            continue
        
        total_files += 1
        results = validate_file(file_path)
        all_results.append(results)
        
        if results['passed_checks'] == results['total_checks']:
            files_passed += 1
            print(f"  🎉 All checks passed for {file_path}")
        else:
            print(f"  ⚠️ {results['passed_checks']}/{results['total_checks']} checks passed")
    
    # Summary
    print(f"\n📊 Validation Summary")
    print("=" * 30)
    print(f"Files validated: {total_files}")
    print(f"Files passed all checks: {files_passed}")
    print(f"Overall success rate: {files_passed/total_files:.1%}" if total_files > 0 else "No files processed")
    
    # Detailed issues
    all_issues = []
    for result in all_results:
        all_issues.extend(result['issues'])
    
    if all_issues:
        print(f"\n🔧 Issues to address ({len(all_issues)} total):")
        for issue in all_issues[:10]:  # Show first 10 issues
            print(f"  - {issue}")
        if len(all_issues) > 10:
            print(f"  ... and {len(all_issues) - 10} more issues")
    else:
        print("\n🎉 No coding standards issues found!")
    
    # Best practices recommendations
    print(f"\n💡 Best Practices Status:")
    
    practices = [
        ("Custom Exceptions", "ResearchError class defined"),
        ("Type Hints", "Function parameters and returns typed"),
        ("Logging", "Structured logging implemented"),
        ("Documentation", "Comprehensive docstrings"),
        ("Error Handling", "Specific exception handling"),
    ]
    
    for practice, description in practices:
        # Simple check if practice is implemented
        implemented = any(practice.lower() in ' '.join(result['issues']).lower() for result in all_results)
        status = "❌ Needs improvement" if implemented else "✅ Implemented"
        print(f"  {status} {practice}: {description}")
    
    return files_passed == total_files


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)