#!/usr/bin/env python3
"""
Integration Test Runner
Runs tests that require real external services using credentials from .env
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.e2e.helpers.env_utils import env_manager

def print_status(message: str):
    """Print a status message with formatting."""
    print(f"\n🔍 {message}")
    print("=" * 60)

def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")

def print_warning(message: str):
    """Print a warning message."""
    print(f"⚠️  {message}")

def print_error(message: str):
    """Print an error message."""
    print(f"❌ {message}")

def check_environment():
    """Check if environment is ready for integration tests."""
    print_status("Checking Environment Configuration")
    
    # Load environment
    env_manager._load_env_file()
    
    # Check service status
    service_status = env_manager.check_integration_ready()
    
    print("Service Configuration Status:")
    for service, ready in service_status.items():
        status = "✅ READY" if ready else "❌ NOT CONFIGURED"
        print(f"  {service.upper()}: {status}")
    
    # Count ready services
    ready_services = sum(service_status.values())
    total_services = len(service_status)
    
    print(f"\nOverall Status: {ready_services}/{total_services} services configured")
    
    if ready_services == 0:
        print_error("No services are configured. Please check your .env file.")
        return False
    elif ready_services < total_services:
        print_warning(f"{total_services - ready_services} services not configured. Some tests may be skipped.")
    
    return True

def get_existing_test_directories():
    """Get list of test directories that actually exist."""
    test_dirs = [
        "tests/e2e/tier0/",
        "tests/e2e/tier1/",
        "tests/e2e/tier2/",
        "tests/e2e/tier3/",
        "tests/e2e/graph_sync/",
        "tests/e2e/zk_attestation/",
        "tests/e2e/gemini_explain/",
        "tests/e2e/action_executor/",
        "tests/e2e/voice_alerts/"
    ]
    
    existing_dirs = []
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            existing_dirs.append(test_dir)
        else:
            print_warning(f"Test directory not found: {test_dir}")
    
    return existing_dirs

def run_integration_tests(test_pattern: str = None, verbose: bool = False):
    """Run integration tests with real services."""
    print_status("Running Integration Tests")
    
    # Build pytest command
    cmd = [
        "python", "-m", "pytest",
        "-m", "integration",
        "--tb=short",
        "--disable-warnings"
    ]
    
    if verbose:
        cmd.append("-v")
    
    if test_pattern:
        cmd.append(test_pattern)
    else:
        # Get existing integration test directories
        integration_dirs = [
            "tests/e2e/tier2/",
            "tests/e2e/tier3/",
            "tests/e2e/graph_sync/",
            "tests/e2e/zk_attestation/",
            "tests/e2e/gemini_explain/",
            "tests/e2e/action_executor/",
            "tests/e2e/voice_alerts/"
        ]
        
        existing_dirs = []
        for test_dir in integration_dirs:
            if Path(test_dir).exists():
                existing_dirs.append(test_dir)
        
        if not existing_dirs:
            print_warning("No integration test directories found")
            return True
        
        cmd.extend(existing_dirs)
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print_error(f"Failed to run tests: {e}")
        return False

def run_core_tests(verbose: bool = False):
    """Run core tests (non-integration) that don't require external services."""
    print_status("Running Core Tests (Non-Integration)")
    
    cmd = [
        "python", "-m", "pytest",
        "-m", "not integration",
        "--tb=short",
        "--disable-warnings"
    ]
    
    if verbose:
        cmd.append("-v")
    
    # Get existing core test directories
    core_dirs = ["tests/e2e/tier0/", "tests/e2e/tier1/"]
    existing_dirs = []
    for test_dir in core_dirs:
        if Path(test_dir).exists():
            existing_dirs.append(test_dir)
    
    if not existing_dirs:
        print_warning("No core test directories found")
        return True
    
    cmd.extend(existing_dirs)
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print_error(f"Failed to run tests: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run E2E tests with real services")
    parser.add_argument("--mode", choices=["integration", "core", "all"], 
                       default="integration", help="Test mode to run")
    parser.add_argument("--pattern", help="Specific test pattern to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--check-env", action="store_true", help="Only check environment")
    
    args = parser.parse_args()
    
    print("🚀 Onchain Command Center - Integration Test Runner")
    print("=" * 60)
    
    # Check environment first
    if not check_environment():
        sys.exit(1)
    
    if args.check_env:
        print_success("Environment check completed")
        return
    
    success = True
    
    if args.mode in ["integration", "all"]:
        success &= run_integration_tests(args.pattern, args.verbose)
    
    if args.mode in ["core", "all"]:
        success &= run_core_tests(args.verbose)
    
    if success:
        print_success("All tests completed successfully!")
    else:
        print_error("Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 