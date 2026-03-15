"""
Module 7 Test Script: Kubernetes Deployment
Tests Docker and Kubernetes deployment configurations
"""

import asyncio
import subprocess
import sys
import os
from typing import Dict, List, Tuple
import yaml
import json


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(message: str):
    """Print success message in green"""
    print(f"{Colors.GREEN}[OK] {message}{Colors.END}")


def print_error(message: str):
    """Print error message in red"""
    print(f"{Colors.RED}[FAIL] {message}{Colors.END}")


def print_warning(message: str):
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}[WARN] {message}{Colors.END}")


def print_info(message: str):
    """Print info message in blue"""
    print(f"{Colors.BLUE}[INFO] {message}{Colors.END}")


def run_command(command: List[str], check: bool = True) -> Tuple[bool, str, str]:
    """
    Run a shell command and return success status, stdout, stderr
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check
        )
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except FileNotFoundError:
        return False, "", f"Command not found: {command[0]}"


def test_docker_installed() -> bool:
    """Test if Docker is installed"""
    print_info("Testing Docker installation...")
    success, stdout, stderr = run_command(["docker", "--version"], check=False)

    if success:
        print_success(f"Docker is installed: {stdout.strip()}")
        return True
    else:
        print_error("Docker is not installed")
        return False


def test_docker_running() -> bool:
    """Test if Docker daemon is running"""
    print_info("Testing Docker daemon...")
    success, stdout, stderr = run_command(["docker", "info"], check=False)

    if success:
        print_success("Docker daemon is running")
        return True
    else:
        print_error("Docker daemon is not running")
        return False


def test_dockerfile_syntax(dockerfile: str) -> bool:
    """Test Dockerfile syntax by attempting to parse it"""
    print_info(f"Testing {dockerfile} syntax...")

    if not os.path.exists(dockerfile):
        print_error(f"{dockerfile} not found")
        return False

    try:
        with open(dockerfile, 'r') as f:
            content = f.read()

        # Basic syntax checks
        if not content.strip():
            print_error(f"{dockerfile} is empty")
            return False

        # Check if FROM instruction exists (skip comments and empty lines)
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        if not lines or not lines[0].startswith('FROM'):
            print_error(f"{dockerfile} must have FROM as first instruction (after comments)")
            return False

        required_instructions = ['FROM', 'WORKDIR', 'COPY', 'CMD']
        for instruction in required_instructions:
            if instruction not in content:
                print_error(f"{dockerfile} missing {instruction} instruction")
                return False

        print_success(f"{dockerfile} syntax looks good")
        return True

    except Exception as e:
        print_error(f"Error reading {dockerfile}: {e}")
        return False


def test_docker_compose_syntax() -> bool:
    """Test docker-compose.yml syntax"""
    print_info("Testing docker-compose.yml syntax...")

    if not os.path.exists("docker-compose.yml"):
        print_error("docker-compose.yml not found")
        return False

    try:
        with open("docker-compose.yml", 'r') as f:
            config = yaml.safe_load(f)

        # Check required sections
        if 'services' not in config:
            print_error("docker-compose.yml missing 'services' section")
            return False

        # Check required services
        required_services = ['postgres', 'kafka', 'api', 'worker']
        for service in required_services:
            if service not in config['services']:
                print_error(f"docker-compose.yml missing '{service}' service")
                return False

        print_success("docker-compose.yml syntax is valid")
        return True

    except yaml.YAMLError as e:
        print_error(f"docker-compose.yml has invalid YAML: {e}")
        return False
    except Exception as e:
        print_error(f"Error reading docker-compose.yml: {e}")
        return False


def test_kubernetes_manifests() -> bool:
    """Test Kubernetes manifest files"""
    print_info("Testing Kubernetes manifests...")

    k8s_dir = "k8s"
    if not os.path.exists(k8s_dir):
        print_error(f"{k8s_dir} directory not found")
        return False

    required_files = [
        "namespace.yaml",
        "configmap.yaml",
        "secret.yaml",
        "api-deployment.yaml",
        "api-service.yaml",
        "worker-deployment.yaml",
        "kafka-statefulset.yaml",
        "kafka-service.yaml",
        "zookeeper-statefulset.yaml",
        "zookeeper-service.yaml",
        "ingress.yaml"
    ]

    all_valid = True

    for filename in required_files:
        filepath = os.path.join(k8s_dir, filename)

        if not os.path.exists(filepath):
            print_error(f"{filepath} not found")
            all_valid = False
            continue

        try:
            with open(filepath, 'r') as f:
                # Parse all YAML documents in the file
                documents = list(yaml.safe_load_all(f))

            if not documents or all(doc is None for doc in documents):
                print_error(f"{filepath} is empty or invalid")
                all_valid = False
                continue

            # Check each document has required fields
            for doc in documents:
                if doc is None:
                    continue

                if 'apiVersion' not in doc:
                    print_error(f"{filepath} missing 'apiVersion'")
                    all_valid = False

                if 'kind' not in doc:
                    print_error(f"{filepath} missing 'kind'")
                    all_valid = False

                if 'metadata' not in doc:
                    print_error(f"{filepath} missing 'metadata'")
                    all_valid = False

            print_success(f"{filepath} is valid")

        except yaml.YAMLError as e:
            print_error(f"{filepath} has invalid YAML: {e}")
            all_valid = False
        except Exception as e:
            print_error(f"Error reading {filepath}: {e}")
            all_valid = False

    return all_valid


def test_env_example() -> bool:
    """Test .env.example file"""
    print_info("Testing .env.example...")

    if not os.path.exists(".env.example"):
        print_error(".env.example not found")
        return False

    try:
        with open(".env.example", 'r') as f:
            content = f.read()

        # Check for required environment variables
        required_vars = [
            'ENVIRONMENT',
            'POSTGRES_HOST',
            'POSTGRES_PORT',
            'POSTGRES_DB',
            'POSTGRES_USER',
            'POSTGRES_PASSWORD',
            'DATABASE_URL',
            'OPENAI_API_KEY',
            'KAFKA_ENABLED',
            'KAFKA_BOOTSTRAP_SERVERS'
        ]

        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)

        if missing_vars:
            print_error(f".env.example missing variables: {', '.join(missing_vars)}")
            return False

        print_success(".env.example contains all required variables")
        return True

    except Exception as e:
        print_error(f"Error reading .env.example: {e}")
        return False


def test_deployment_scripts() -> bool:
    """Test deployment scripts exist and are executable"""
    print_info("Testing deployment scripts...")

    scripts = [
        "scripts/deploy.sh",
        "scripts/build_and_push.sh"
    ]

    all_valid = True

    for script in scripts:
        if not os.path.exists(script):
            print_error(f"{script} not found")
            all_valid = False
            continue

        # Check if file is readable
        try:
            with open(script, 'r') as f:
                content = f.read()

            if not content.strip():
                print_error(f"{script} is empty")
                all_valid = False
                continue

            # Check for shebang
            if not content.startswith('#!/bin/bash'):
                print_warning(f"{script} missing shebang")

            print_success(f"{script} exists and is readable")

        except Exception as e:
            print_error(f"Error reading {script}: {e}")
            all_valid = False

    return all_valid


def test_kubectl_installed() -> bool:
    """Test if kubectl is installed"""
    print_info("Testing kubectl installation...")
    success, stdout, stderr = run_command(["kubectl", "version", "--client"], check=False)

    if success:
        print_success(f"kubectl is installed")
        return True
    else:
        print_warning("kubectl is not installed (optional for local testing)")
        return True  # Not a failure, just a warning


def test_resource_limits() -> bool:
    """Test that all deployments have resource limits"""
    print_info("Testing resource limits in deployments...")

    deployment_files = [
        "k8s/api-deployment.yaml",
        "k8s/worker-deployment.yaml",
        "k8s/kafka-statefulset.yaml",
        "k8s/zookeeper-statefulset.yaml"
    ]

    all_valid = True

    for filepath in deployment_files:
        if not os.path.exists(filepath):
            continue

        try:
            with open(filepath, 'r') as f:
                doc = yaml.safe_load(f)

            # Navigate to containers
            containers = doc.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])

            for container in containers:
                resources = container.get('resources', {})

                if 'requests' not in resources:
                    print_error(f"{filepath} missing resource requests")
                    all_valid = False

                if 'limits' not in resources:
                    print_error(f"{filepath} missing resource limits")
                    all_valid = False

            if all_valid:
                print_success(f"{filepath} has proper resource limits")

        except Exception as e:
            print_error(f"Error checking {filepath}: {e}")
            all_valid = False

    return all_valid


def test_health_checks() -> bool:
    """Test that API deployment has health checks"""
    print_info("Testing health checks...")

    filepath = "k8s/api-deployment.yaml"

    if not os.path.exists(filepath):
        print_error(f"{filepath} not found")
        return False

    try:
        with open(filepath, 'r') as f:
            doc = yaml.safe_load(f)

        containers = doc.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])

        for container in containers:
            if 'livenessProbe' not in container:
                print_error(f"{filepath} missing livenessProbe")
                return False

            if 'readinessProbe' not in container:
                print_error(f"{filepath} missing readinessProbe")
                return False

        print_success(f"{filepath} has proper health checks")
        return True

    except Exception as e:
        print_error(f"Error checking {filepath}: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Module 7 Test Suite: Kubernetes Deployment")
    print("=" * 60)
    print()

    tests = [
        ("Docker Installation", test_docker_installed),
        ("Docker Daemon", test_docker_running),
        ("Dockerfile.api Syntax", lambda: test_dockerfile_syntax("Dockerfile.api")),
        ("Dockerfile.worker Syntax", lambda: test_dockerfile_syntax("Dockerfile.worker")),
        ("docker-compose.yml Syntax", test_docker_compose_syntax),
        (".env.example", test_env_example),
        ("Kubernetes Manifests", test_kubernetes_manifests),
        ("Resource Limits", test_resource_limits),
        ("Health Checks", test_health_checks),
        ("Deployment Scripts", test_deployment_scripts),
        ("kubectl Installation", test_kubectl_installed),
    ]

    results = []

    for test_name, test_func in tests:
        print()
        print(f"Running: {test_name}")
        print("-" * 60)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test failed with exception: {e}")
            results.append((test_name, False))

    # Print summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - {test_name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print_success("All tests passed!")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
