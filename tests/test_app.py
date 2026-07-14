import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app"

sys.path.insert(0, str(APP_PATH))

from app import app


def test_home_page():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"DCS Building Monitoring Simulator" in response.data


def test_health_endpoint():
    client = app.test_client()

    response = client.get("/health")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "version" in data


def test_status_endpoint():
    client = app.test_client()

    response = client.get("/api/status")
    data = response.get_json()

    assert response.status_code == 200
    assert data["system_status"] == "warning"
    assert data["controllers_online"] == 4
    assert data["devices_total"] == 125
