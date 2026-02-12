#!/usr/bin/env python3
"""
Environment verification script for the Agentic AI Loan Verification System.
Checks if all dependencies are installed and configured correctly.
"""

import sys
import os
import importlib
from typing import Tuple, List


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is adequate"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        return True, f"✓ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"✗ Python {version.major}.{version.minor}.{version.micro} (3.9+ required)"


def check_module(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """Check if a Python module is installed"""
    if package_name is None:
        package_name = module_name
    
    try:
        mod = importlib.import_module(module_name)
        version = getattr(mod, '__version__', 'unknown')
        return True, f"✓ {package_name} ({version})"
    except ImportError:
        return False, f"✗ {package_name} (not installed)"


def check_env_file() -> Tuple[bool, str]:
    """Check if .env file exists"""
    if os.path.exists('.env'):
        return True, "✓ .env file exists"
    else:
        return False, "✗ .env file not found"


def check_api_key() -> Tuple[bool, str]:
    """Check if Gemini API key is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and api_key != 'your_gemini_api_key_here':
        masked_key = api_key[:8] + '...' + api_key[-4:] if len(api_key) > 12 else '***'
        return True, f"✓ GEMINI_API_KEY configured ({masked_key})"
    else:
        return False, "⚠ GEMINI_API_KEY not configured (AI features will use fallback)"


def check_files() -> List[Tuple[bool, str]]:
    """Check if all required files exist"""
    required_files = [
        'main.py',
        'models.py',
        'database.py',
        'orchestrator.py',
        'requirements.txt',
        'agents/__init__.py',
        'agents/greeting.py',
        'agents/planner.py',
        'agents/credit.py',
        'agents/employment.py',
        'agents/collateral.py',
        'agents/critique.py',
        'agents/final_decision.py',
    ]
    
    results = []
    for file in required_files:
        if os.path.exists(file):
            results.append((True, f"✓ {file}"))
        else:
            results.append((False, f"✗ {file} (missing)"))
    
    return results


def main():
    """Run all checks"""
    print("=" * 70)
    print("  Agentic AI Loan Verification System - Environment Check")
    print("=" * 70)
    print()
    
    all_ok = True
    
    # Check Python version
    print("Python Environment:")
    ok, msg = check_python_version()
    print(f"  {msg}")
    all_ok = all_ok and ok
    print()
    
    # Check required modules
    print("Required Dependencies:")
    modules = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('pydantic', 'pydantic'),
        ('dotenv', 'python-dotenv'),
        ('google.generativeai', 'google-generativeai'),
        ('aiosqlite', 'aiosqlite'),
    ]
    
    for module_name, package_name in modules:
        ok, msg = check_module(module_name, package_name)
        print(f"  {msg}")
        all_ok = all_ok and ok
    print()
    
    # Check files
    print("Project Files:")
    file_results = check_files()
    for ok, msg in file_results:
        print(f"  {msg}")
        all_ok = all_ok and ok
    print()
    
    # Check environment
    print("Environment Configuration:")
    ok, msg = check_env_file()
    print(f"  {msg}")
    if not ok:
        print("    Run: cp .env.example .env")
    
    ok, msg = check_api_key()
    print(f"  {msg}")
    if not ok:
        print("    Get API key from: https://makersuite.google.com/app/apikey")
        print("    System will work without it, but AI features will use fallback logic")
    print()
    
    # Final verdict
    print("=" * 70)
    if all_ok:
        print("✅ All checks passed! System is ready to run.")
        print()
        print("To start the server:")
        print("  uvicorn main:app --reload")
        print()
        print("Then visit: http://localhost:8000/docs")
    else:
        print("⚠️  Some checks failed. Please resolve the issues above.")
        print()
        print("To install dependencies:")
        print("  pip install -r requirements.txt")
        print()
        print("To set up environment:")
        print("  cp .env.example .env")
        print("  # Edit .env and add your GEMINI_API_KEY")
    print("=" * 70)


if __name__ == "__main__":
    main()
