#!/usr/bin/env python3
"""
Master Test Script
Run all tests in sequence
"""
import sys
import subprocess
from pathlib import Path

def run_test(script_name, description):
    """Run a test script"""
    print("\n" + "🔷"*30)
    print(f"Running: {description}")
    print("🔷"*30 + "\n")
    
    result = subprocess.run(
        [sys.executable, script_name],
        cwd=Path(__file__).parent,
        capture_output=False
    )
    
    if result.returncode == 0:
        print(f"\n✅ {description} - PASSED\n")
        return True
    else:
        print(f"\n❌ {description} - FAILED\n")
        return False

def main():
    print("="*60)
    print("Master Test Suite - Report Generator")
    print("="*60)
    
    tests = [
        ("test_1_imports.py", "Test 1: Import Test"),
        ("test_2_generate.py", "Test 2: Report Generation Test"),
        ("test_3_compare.py", "Test 3: Comparison Test"),
    ]
    
    results = []
    
    for script, desc in tests:
        success = run_test(script, desc)
        results.append((desc, success))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for desc, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {desc}")
    
    print("\n" + "="*60)
    print(f"Result: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\nThe new modular architecture is working correctly!")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("\nPlease review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
