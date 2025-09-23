#!/usr/bin/env python3
"""
Simple test script to verify Gitguy components can be imported and basic functionality works.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all modules can be imported"""
    try:
        from main import GitguyAssistant
        from commands import CommandHelper
        from conflicts import ConflictResolver
        from guide import TutorialGenerator
        from chat import ChatAssistant
        from utils import safe_json_parse, validate_json
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print("✅ GROQ_API_KEY found in environment")
        return True
    else:
        print("⚠️  GROQ_API_KEY not found - AI features will not work")
        print("   Please add your Groq API key to the .env file")
        return False

def test_basic_functionality():
    """Test basic functionality without AI calls"""
    try:
        # Test utility functions
        test_data = {"test": "value", "number": 42}
        parsed = safe_json_parse('{"test": "value", "number": 42}')
        assert parsed == test_data, "JSON parsing failed"

        is_valid = validate_json(test_data, ["test", "number"])
        assert is_valid, "JSON validation failed"

        print("✅ Basic utility functions working")
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_fallback_data():
    """Test fallback data structures"""
    try:
        from commands import CommandHelper
        from conflicts import ConflictResolver
        from guide import TutorialGenerator

        # Create dummy LLM object for testing
        class DummyLLM:
            pass

        dummy_llm = DummyLLM()

        # Test command helper fallback
        cmd_helper = CommandHelper(dummy_llm)
        fallback = cmd_helper._get_fallback_command_help("git init")
        assert "syntax" in fallback, "Command fallback missing syntax"
        assert "description" in fallback, "Command fallback missing description"

        # Test conflict resolver fallback
        conflict_resolver = ConflictResolver(dummy_llm)
        fallback = conflict_resolver._get_fallback_conflict_resolution("test scenario")
        assert "analysis" in fallback, "Conflict fallback missing analysis"
        assert "steps" in fallback, "Conflict fallback missing steps"

        # Test tutorial generator fallback
        tutorial_gen = TutorialGenerator(dummy_llm)
        fallback = tutorial_gen._get_fallback_tutorial("Git Setup")
        assert "title" in fallback, "Tutorial fallback missing title"
        assert "steps" in fallback, "Tutorial fallback missing steps"

        print("✅ Fallback data structures working")
        return True
    except Exception as e:
        print(f"❌ Fallback data test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Gitguy Application")
    print("=" * 40)

    tests = [
        test_environment,
        test_imports,
        test_basic_functionality,
        test_fallback_data
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Gitguy is ready to run.")
        print("\nTo start the application:")
        print("streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
