import subprocess
import time

import pytest
import requests


@pytest.fixture(scope="module")
def docker_services():
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    time.sleep(10)
    yield
    subprocess.run(["docker-compose", "down"], check=True)


def test_docker_compose_starts_all_services(docker_services):
    result = subprocess.run(
        ["docker-compose", "ps", "--services"],
        capture_output=True,
        text=True,
        check=True,
    )
    service_names = result.stdout.strip().split("\n")
    
    assert "postgres" in service_names
    assert "redis" in service_names
    assert "api" in service_names


def test_postgres_healthcheck(docker_services):
    result = subprocess.run(
        ["docker-compose", "exec", "-T", "postgres", "pg_isready", "-U", "buscai"],
        capture_output=True,
        check=True,
    )
    assert result.returncode == 0


def test_redis_healthcheck(docker_services):
    result = subprocess.run(
        ["docker-compose", "exec", "-T", "redis", "redis-cli", "ping"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "PONG"


def test_api_healthcheck_endpoint_returns_200(docker_services):
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            assert response.status_code == 200
            return
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                time.sleep(2)
                continue
            raise
