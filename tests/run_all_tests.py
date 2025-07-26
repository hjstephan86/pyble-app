#!/usr/bin/env python3
"""
Test runner for the Bible API application.

This script runs all unit tests for the Bible API modules and provides
a comprehensive test coverage report.

Usage:
    python run_all_tests.py
    python run_all_tests.py --verbose
    python run_all_tests.py --coverage
"""

import sys
import os
import unittest
import argparse
from io import StringIO

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def discover_and_run_tests(verbosity=1, pattern='*_test.py'):
    """
    Discover and run all test modules.
    
    Args:
        verbosity (int): Test output verbosity level (0-2)
        pattern (str): Pattern to match test files
    
    Returns:
        unittest.TestResult: Test results
    """
    # Create test loader
    loader = unittest.TestLoader()
    
    # Discover tests in current directory
    test_suite = loader.discover(
        start_dir='.',  # Current directory
        pattern=pattern,
        top_level_dir='.'
    )
    
    # Create test runner
    stream = StringIO() if verbosity == 0 else sys.stderr
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=verbosity,
        buffer=True,
        warnings='ignore'
    )
    
    # Run tests
    result = runner.run(test_suite)
    
    return result

def print_test_summary(result):
    """
    Print a summary of test results.
    
    Args:
        result (unittest.TestResult): Test results
    """
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    
    print(f"Total tests run: {total_tests}")
    print(f"Successes: {total_tests - failures - errors - skipped}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("="*70)

def run_coverage_analysis():
    """
    Run tests with coverage analysis if coverage.py is available.
    """
    try:
        import coverage
        
        # Create coverage instance
        cov = coverage.Coverage()
        cov.start()
        
        # Run tests
        result = discover_and_run_tests(verbosity=1)
        
        # Stop coverage and save
        cov.stop()
        cov.save()
        
        print("\n" + "="*70)
        print("COVERAGE REPORT")
        print("="*70)
        
        # Generate coverage report
        cov.report(show_missing=True)
        
        return result
        
    except ImportError:
        print("Coverage.py not installed. Install with: pip install coverage")
        print("Running tests without coverage analysis...\n")
        return discover_and_run_tests(verbosity=2)

def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description='Run Bible API unit tests')
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Run tests with verbose output'
    )
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Run tests with coverage analysis'
    )
    parser.add_argument(
        '--pattern', '-p',
        default='*_test.py',
        help='Pattern to match test files (default: *_test.py)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Run tests with minimal output'
    )
    
    args = parser.parse_args()
    
    # Determine verbosity level
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1
    
    print("Bible API Test Suite")
    print("="*70)
    
    # Run tests with or without coverage
    if args.coverage:
        result = run_coverage_analysis()
    else:
        result = discover_and_run_tests(verbosity=verbosity, pattern=args.pattern)
    
    # Print summary
    print_test_summary(result)
    
    # Exit with appropriate code
    if result.failures or result.errors:
        sys.exit(1)
    else:
        print("All tests passed! ✅")
        sys.exit(0)

def run_specific_test_module(module_name):
    """
    Run tests from a specific module.
    
    Args:
        module_name (str): Name of the test module to run
    """
    try:
        # Import the test module
        test_module = __import__(module_name)
        
        # Create test suite from module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result
        
    except ImportError as e:
        print(f"Error importing test module '{module_name}': {e}")
        return None

def list_available_tests():
    """List all available test modules."""
    import glob
    
    test_files = glob.glob('*_test.py')
    
    print("Available test modules:")
    print("-" * 30)
    
    for test_file in sorted(test_files):
        module_name = test_file[:-3]  # Remove .py extension
        print(f"  - {module_name}")
    
    print(f"\nTotal: {len(test_files)} test modules found")

if __name__ == '__main__':
    # Check if specific module was requested
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_available_tests()
    elif len(sys.argv) > 1 and sys.argv[1].endswith('_test'):
        # Run specific test module
        module_name = sys.argv[1]
        result = run_specific_test_module(module_name)
        if result:
            print_test_summary(result)
    else:
        # Run main test suite
        main()