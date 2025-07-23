#!/usr/bin/env python3
"""
Test Runner for E2E Test Suite
Executes tests by tier with proper reporting and error handling
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

class TestRunner:
    """Manages execution of tiered E2E tests"""
    
    def __init__(self, workspace_root: str = "/Users/jadenfix/eth"):
        self.workspace_root = Path(workspace_root)
        self.test_root = self.workspace_root / "tests" / "e2e"
        self.results = {
            "start_time": None,
            "end_time": None,
            "total_duration": 0,
            "tiers": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "error_tests": []
            }
        }
    
    def run_tier_tests(self, tier: str, max_duration: Optional[int] = None) -> Dict:
        """Run tests for a specific tier"""
        print(f"\n{'='*60}")
        print(f"RUNNING TIER {tier.upper()} TESTS")
        print(f"{'='*60}")
        
        tier_path = self.test_root / f"tier{tier}"
        if not tier_path.exists():
            print(f"⚠️  Tier {tier} test directory not found: {tier_path}")
            return {"status": "skipped", "reason": "directory_not_found"}
        
        tier_start = time.time()
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(tier_path),
            f"-m", f"tier{tier}",
            "-v",
            "--tb=short",
            "--capture=no",
            f"--junit-xml={self.workspace_root}/test_results_tier{tier}.xml"
        ]
        
        if max_duration:
            cmd.extend(["--timeout", str(max_duration)])
        
        print(f"Executing: {' '.join(cmd)}")
        print(f"Working directory: {self.workspace_root}")
        print()
        
        try:
            # Run tests with timeout
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=max_duration * 60 if max_duration else None  # Convert to seconds
            )
            
            tier_end = time.time()
            tier_duration = tier_end - tier_start
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            
            tier_result = {
                "status": "completed",
                "duration": tier_duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "tests": self._parse_pytest_output(output_lines),
                "success": result.returncode == 0
            }
            
            # Print summary for this tier
            print(f"\n📊 TIER {tier.upper()} RESULTS:")
            print(f"   Duration: {tier_duration:.2f}s")
            print(f"   Return Code: {result.returncode}")
            print(f"   Tests: {tier_result['tests']}")
            
            if result.returncode != 0:
                print(f"❌ Tier {tier} had failures:")
                if result.stderr:
                    print("STDERR:")
                    print(result.stderr)
                if "FAILED" in result.stdout:
                    print("Failed tests in STDOUT:")
                    for line in output_lines:
                        if "FAILED" in line:
                            print(f"   {line}")
            else:
                print(f"✅ Tier {tier} passed successfully!")
            
            return tier_result
            
        except subprocess.TimeoutExpired:
            tier_end = time.time()
            tier_duration = tier_end - tier_start
            
            print(f"⏰ Tier {tier} tests timed out after {max_duration} minutes")
            
            return {
                "status": "timeout",
                "duration": tier_duration,
                "max_duration": max_duration,
                "success": False
            }
            
        except Exception as e:
            tier_end = time.time()
            tier_duration = tier_end - tier_start
            
            print(f"💥 Error running tier {tier} tests: {e}")
            
            return {
                "status": "error",
                "duration": tier_duration,
                "error": str(e),
                "success": False
            }
    
    def _parse_pytest_output(self, lines: List[str]) -> Dict:
        """Parse pytest output to extract test results"""
        tests = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
        
        for line in lines:
            if "passed" in line and "failed" in line:
                # Summary line like "5 passed, 2 failed in 10.20s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        tests["passed"] = int(parts[i-1])
                    elif part == "failed":
                        tests["failed"] = int(parts[i-1])
                    elif part == "skipped":
                        tests["skipped"] = int(parts[i-1])
                break
        
        tests["total"] = tests["passed"] + tests["failed"] + tests["skipped"]
        return tests
    
    def run_all_tiers(self, tiers: List[str] = ["0", "1"], max_duration_per_tier: int = 15) -> Dict:
        """Run tests for all specified tiers"""
        print("🚀 Starting E2E Test Suite Execution")
        print(f"Tiers to run: {tiers}")
        print(f"Max duration per tier: {max_duration_per_tier} minutes")
        print(f"Workspace: {self.workspace_root}")
        
        self.results["start_time"] = time.time()
        
        for tier in tiers:
            print(f"\n⏱️  Starting Tier {tier} tests...")
            tier_result = self.run_tier_tests(tier, max_duration_per_tier)
            self.results["tiers"][f"tier{tier}"] = tier_result
            
            # Update summary
            if tier_result.get("tests"):
                tier_tests = tier_result["tests"]
                self.results["summary"]["total_tests"] += tier_tests.get("total", 0)
                self.results["summary"]["passed"] += tier_tests.get("passed", 0)
                self.results["summary"]["failed"] += tier_tests.get("failed", 0)
                self.results["summary"]["skipped"] += tier_tests.get("skipped", 0)
            
            if not tier_result.get("success", False):
                self.results["summary"]["error_tests"].append(f"tier{tier}")
            
            # Stop on major failures unless continuing
            if tier_result.get("status") == "error":
                print(f"🛑 Stopping due to error in Tier {tier}")
                break
        
        self.results["end_time"] = time.time()
        self.results["total_duration"] = self.results["end_time"] - self.results["start_time"]
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("=" * 80)
        report.append("E2E TEST SUITE EXECUTION REPORT")
        report.append("=" * 80)
        
        # Overall summary
        report.append(f"\n📊 OVERALL SUMMARY:")
        report.append(f"   Total Duration: {self.results['total_duration']:.2f}s")
        report.append(f"   Total Tests: {self.results['summary']['total_tests']}")
        report.append(f"   Passed: {self.results['summary']['passed']}")
        report.append(f"   Failed: {self.results['summary']['failed']}")
        report.append(f"   Skipped: {self.results['summary']['skipped']}")
        
        if self.results['summary']['failed'] == 0:
            report.append("\n✅ ALL TESTS PASSED!")
        else:
            report.append(f"\n❌ {self.results['summary']['failed']} TESTS FAILED")
        
        # Tier-by-tier breakdown
        report.append(f"\n📋 TIER BREAKDOWN:")
        for tier_name, tier_result in self.results["tiers"].items():
            report.append(f"\n   {tier_name.upper()}:")
            report.append(f"      Status: {tier_result.get('status', 'unknown')}")
            report.append(f"      Duration: {tier_result.get('duration', 0):.2f}s")
            report.append(f"      Success: {tier_result.get('success', False)}")
            
            if tier_result.get("tests"):
                tests = tier_result["tests"]
                report.append(f"      Tests: {tests.get('passed', 0)} passed, {tests.get('failed', 0)} failed, {tests.get('skipped', 0)} skipped")
        
        # Recommendations
        report.append(f"\n🎯 RECOMMENDATIONS:")
        
        if self.results['summary']['failed'] == 0:
            report.append("   • All tests passing - system ready for next phase")
            report.append("   • Consider running Tier 2 (governance) tests")
            report.append("   • Review performance metrics for optimization")
        else:
            report.append("   • Fix failing tests before proceeding")
            report.append("   • Review error logs for specific issues")
            report.append("   • Ensure test environment is properly configured")
        
        if any(tier.get('status') == 'timeout' for tier in self.results['tiers'].values()):
            report.append("   • Some tests timed out - consider increasing timeout or optimizing")
        
        return "\n".join(report)
    
    def save_results(self, filename: str = "e2e_test_results.json") -> None:
        """Save test results to JSON file"""
        output_path = self.workspace_root / filename
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {output_path}")

def main():
    """Main test runner execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="E2E Test Suite Runner")
    parser.add_argument("--tiers", nargs="+", default=["0", "1"], 
                       help="Tiers to run (default: 0 1)")
    parser.add_argument("--timeout", type=int, default=15, 
                       help="Timeout per tier in minutes (default: 15)")
    parser.add_argument("--workspace", default="/Users/jadenfix/eth",
                       help="Workspace root directory")
    parser.add_argument("--report-only", action="store_true",
                       help="Only generate report from existing results")
    
    args = parser.parse_args()
    
    runner = TestRunner(args.workspace)
    
    if args.report_only:
        # Load existing results
        results_file = Path(args.workspace) / "e2e_test_results.json"
        if results_file.exists():
            with open(results_file) as f:
                runner.results = json.load(f)
            print(runner.generate_report())
        else:
            print("No existing results found. Run tests first.")
        return
    
    try:
        # Run tests
        results = runner.run_all_tiers(args.tiers, args.timeout)
        
        # Generate and print report
        report = runner.generate_report()
        print(report)
        
        # Save results
        runner.save_results()
        
        # Exit with appropriate code
        if results["summary"]["failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        runner.results["end_time"] = time.time()
        runner.results["total_duration"] = runner.results["end_time"] - runner.results.get("start_time", time.time())
        
        print(runner.generate_report())
        runner.save_results("e2e_test_results_interrupted.json")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n💥 Fatal error in test runner: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
