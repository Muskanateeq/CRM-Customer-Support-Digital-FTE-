"""
TaskNest - Comprehensive Test Runner
Runs all module tests and generates summary report
"""

import subprocess
import sys
from typing import Dict, List, Tuple

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def run_test(module_name: str, test_file: str) -> Tuple[bool, str]:
    """
    Run a single test module

    Args:
        module_name: Name of the module
        test_file: Path to test file

    Returns:
        Tuple of (success, output)
    """
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}Running: {module_name}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120
        )

        output = result.stdout + result.stderr
        success = result.returncode == 0

        # Print output
        print(output)

        return success, output

    except subprocess.TimeoutExpired:
        error_msg = f"{Colors.RED}[TIMEOUT] Test exceeded 120 seconds{Colors.END}"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"{Colors.RED}[ERROR] {str(e)}{Colors.END}"
        print(error_msg)
        return False, error_msg


def main():
    """Run all module tests"""

    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*70)
    print("  TaskNest CRM Digital FTE - Comprehensive Test Suite")
    print("="*70)
    print(f"{Colors.END}\n")

    # Define all test modules
    tests = [
        ("Module 1: Core Infrastructure", "test_module1.py"),
        ("Module 2: Multi-Channel Integration", "test_module2.py"),
        ("Module 3: OpenAI Agent System", "test_module3.py"),
        ("Module 4: Kafka Event Streaming", "test_module4.py"),
        ("Module 5: Worker Service", "test_module5.py"),
        ("Module 6: Knowledge Base + Embeddings", "test_module6.py"),
        ("Module 7: Kubernetes Deployment", "test_module7.py"),
    ]

    results: Dict[str, bool] = {}

    # Run each test
    for module_name, test_file in tests:
        success, output = run_test(module_name, test_file)
        results[module_name] = success

    # Print summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print(f"{Colors.END}\n")

    passed = 0
    failed = 0

    for module_name, success in results.items():
        if success:
            status = f"{Colors.GREEN}[PASS]{Colors.END}"
            passed += 1
        else:
            status = f"{Colors.RED}[FAIL]{Colors.END}"
            failed += 1

        print(f"{status} {module_name}")

    total = passed + failed

    print(f"\n{Colors.BOLD}")
    print(f"Total: {passed}/{total} modules passed")
    print(f"{Colors.END}")

    if failed > 0:
        print(f"\n{Colors.RED}[WARN] {failed} module(s) failed{Colors.END}")
        print(f"\nNote: Some tests may fail if:")
        print(f"  - Kafka is not running (Modules 4, 5)")
        print(f"  - Missing dependencies (aiokafka, etc.)")
        print(f"  - Database connection issues")
        print(f"\nFor production deployment, use Docker/Kubernetes setup.")
        return 1
    else:
        print(f"\n{Colors.GREEN}[OK] All tests passed!{Colors.END}")
        print(f"\n{Colors.BOLD}System is ready for deployment!{Colors.END}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
