"""Tests for the Ops Monitor detailed health endpoint (GET /api/health/details)."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

TEST_TOKEN = "test-health-details-token"


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def _health_details_test_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set a known token and avoid real outbound calls to the frontend origin."""
    monkeypatch.setattr(settings, "health_details_token", TEST_TOKEN)
    monkeypatch.setattr(settings, "frontend_url", "http://127.0.0.1:9")


def test_health_details_requires_token(client: TestClient) -> None:
    response = client.get("/api/health/details")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_health_details_rejects_wrong_token(client: TestClient) -> None:
    response = client.get(
        "/api/health/details",
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_health_details_returns_schema_with_valid_token(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.health_details._check_database", lambda: {"status": "ok"})
    monkeypatch.setattr("app.health_details._check_cache", lambda: {"status": "ok"})
    monkeypatch.setattr("app.health_details._check_regon", lambda: {"status": "ok"})
    monkeypatch.setattr("app.health_details._check_iban", lambda: {"status": "ok"})

    async def _frontend_ok() -> dict:
        return {"status": "ok"}

    monkeypatch.setattr("app.health_details._check_frontend", _frontend_ok)

    response = client.get(
        "/api/health/details",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["schema_version"] == 1
    assert data["status"] == "ok"
    assert data["version"] == settings.app_version
    assert data["environment"] == settings.environment

    components = data["components"]
    for name in ("database", "cache", "frontend", "regon", "iban"):
        assert name in components
        assert components[name]["status"] == "ok"
