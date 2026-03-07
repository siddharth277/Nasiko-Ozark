#!/usr/bin/env python3
"""
Integration Test Script
Verifies that the calendar integration is working correctly.

Usage:
    python test_integration.py
"""

import sys
import os

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_status(passed, message):
    symbol = "✅" if passed else "❌"
    print(f"{symbol}  {message}")

def test_imports():
    """Test that all required modules can be imported."""
    print_header("Testing Module Imports")
    
    tests = []
    
    # Test calendar_service imports
    try:
        from calendar_service import (
            get_calendar_service,
            find_available_slots,
            book_slot,
        )
        tests.append((True, "calendar_service module imports"))
    except ImportError as e:
        tests.append((False, f"calendar_service import failed: {e}"))
    
    # Test agents imports
    try:
        from agents.calendar_agent import (
            get_all_events,
            schedule_interview,
            add_event,
            delete_event,
        )
        tests.append((True, "agents.calendar_agent imports"))
    except ImportError as e:
        tests.append((False, f"calendar_agent import failed: {e}"))
    
    # Test other agents
    try:
        from agents.email_agent import draft_interview_email
        from agents.screening_agent import screen_resumes
        tests.append((True, "Other agents import"))
    except ImportError as e:
        tests.append((False, f"Other agents import failed: {e}"))
    
    for passed, message in tests:
        print_status(passed, message)
    
    return all(test[0] for test in tests)

def test_dependencies():
    """Test that all required dependencies are installed."""
    print_header("Testing Dependencies")
    
    required = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("groq", "Groq"),
        ("langchain", "LangChain"),
        ("google.auth", "Google Auth"),
        ("googleapiclient", "Google API Client"),
        ("dotenv", "python-dotenv"),
    ]
    
    tests = []
    for module, name in required:
        try:
            __import__(module)
            tests.append((True, f"{name} installed"))
        except ImportError:
            tests.append((False, f"{name} NOT installed"))
    
    for passed, message in tests:
        print_status(passed, message)
    
    return all(test[0] for test in tests)

def test_configuration():
    """Test that configuration files exist."""
    print_header("Testing Configuration")
    
    tests = []
    
    # Check for .env
    if os.path.exists(".env"):
        tests.append((True, ".env file exists"))
        
        # Check for required variables
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            "GROQ_API_KEY",
            "HR_EMAIL",
        ]
        
        for var in required_vars:
            value = os.getenv(var, "")
            if value and "your_" not in value.lower():
                tests.append((True, f"{var} is set"))
            else:
                tests.append((False, f"{var} not configured"))
    else:
        tests.append((False, ".env file not found"))
    
    # Check for credentials.json
    if os.path.exists("credentials.json"):
        tests.append((True, "credentials.json exists"))
    else:
        tests.append((False, "credentials.json not found (download from Google Cloud Console)"))
    
    for passed, message in tests:
        print_status(passed, message)
    
    return all(test[0] for test in tests)

def test_calendar_service():
    """Test calendar service functionality."""
    print_header("Testing Calendar Service")
    
    tests = []
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Test authentication
        try:
            from calendar_service import get_calendar_service
            svc = get_calendar_service()
            tests.append((True, "Google Calendar authentication successful"))
            
            # Test listing calendars
            try:
                result = svc.calendarList().list().execute()
                calendars = result.get("items", [])
                tests.append((True, f"Found {len(calendars)} calendar(s)"))
            except Exception as e:
                tests.append((False, f"Failed to list calendars: {e}"))
                
        except FileNotFoundError as e:
            tests.append((False, "credentials.json not found or invalid"))
        except Exception as e:
            tests.append((False, f"Authentication failed: {e}"))
            
    except Exception as e:
        tests.append((False, f"Calendar service test failed: {e}"))
    
    for passed, message in tests:
        print_status(passed, message)
    
    return all(test[0] for test in tests)

def main():
    """Run all tests."""
    print_header("HR AI Agent - Integration Test Suite")
    print("\nThis script will verify that the calendar integration is set up correctly.")
    print("Make sure you have:")
    print("  1. Installed dependencies (pip install -r requirements.txt)")
    print("  2. Created .env file with API keys")
    print("  3. Downloaded credentials.json from Google Cloud Console")
    
    input("\nPress Enter to continue...")
    
    all_passed = True
    
    # Run tests
    all_passed &= test_imports()
    all_passed &= test_dependencies()
    all_passed &= test_configuration()
    
    # Only test calendar service if previous tests passed
    if all_passed:
        all_passed &= test_calendar_service()
    else:
        print_header("Skipping Calendar Service Test")
        print("⚠️   Fix the above issues first, then run this script again.")
    
    # Final summary
    print_header("Test Results")
    
    if all_passed:
        print("\n🎉  ALL TESTS PASSED!")
        print("\nYour calendar integration is ready to use.")
        print("\nNext steps:")
        print("  1. Start the server: python main.py")
        print("  2. Open browser: http://localhost:8000")
        print("  3. Try scheduling an interview!")
    else:
        print("\n❌  SOME TESTS FAILED")
        print("\nPlease fix the issues above and run this script again.")
        print("\nCommon fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Copy .env.example to .env and fill in your API keys")
        print("  • Download credentials.json from Google Cloud Console")
        print("  • Run diagnostics: python -m calendar_service.diagnose")
    
    print("\n" + "=" * 60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
