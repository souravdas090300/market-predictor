"""Offline tests for the API health, cache stats, and cached price routes.

These tests use FastAPI's TestClient with a fake Redis cache and fake quote
provider, so the full suite can run with no server, Redis instance, or network.
"""

<<<<<<< Updated upstream
import requests
import time
import json
=======
import pytest

from app import database
from app.api import app
from app.core import background_tasks, config
import app.api as api_module
>>>>>>> Stashed changes


class FakeRedisCache:
    def __init__(self, prices=None, available=True):
        self._prices = list(prices) if prices else None
        self._available = available
        self.set_calls = 0

    def get_prices(self):
        return list(self._prices) if self._prices is not None else None

    def set_prices(self, prices, ttl=300):
        self._prices = list(prices)
        self.set_calls += 1

    def get_stats(self):
        return {
            "memory_usage_mb": 1.5,
            "connected_clients": 2,
            "total_commands": 100,
            "hit_rate": 0.75,
        }

    def _is_available(self):
        return self._available


class FakeSession:
    def execute(self, statement):
        return None

    def close(self):
        return None


@pytest.fixture
def client(monkeypatch):
    from fastapi.testclient import TestClient

    monkeypatch.setattr(config, "WATCHLIST", [
        {"symbol": f"SYM{i}", "name": f"Symbol {i}", "class": "stock", "query": f"SYM{i}"}
        for i in range(12)
    ])
    monkeypatch.setattr(database, "SessionLocal", lambda: FakeSession())
    return TestClient(app)


def test_health(monkeypatch, client):
    monkeypatch.setattr(api_module, "redis_cache", FakeRedisCache(available=True))

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["cache"] == "Redis active"
    assert payload["database"] == "Database connected"


def test_cache_stats(monkeypatch, client):
    monkeypatch.setattr(api_module, "redis_cache", FakeRedisCache(available=True))

    response = client.get("/api/cache/stats")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "active"
    assert payload["memory_mb"] == 1.5
    assert payload["hit_rate"] == 0.75


def test_live_prices_caching(monkeypatch, client):
    fake_cache = FakeRedisCache()
    monkeypatch.setattr(api_module, "redis_cache", fake_cache)

    calls = []

    async def fake_fetch_prices_batch(symbols, batch_size=30):
        calls.append(list(symbols))
        return {
            symbol: {
                "price": 100.0 + index,
                "change": 1.0,
                "change_pct": 0.01,
                "volume": 1000,
                "source": "fake",
            }
            for index, symbol in enumerate(symbols)
        }

    monkeypatch.setattr(background_tasks, "fetch_prices_batch", fake_fetch_prices_batch)

    first = client.get("/api/assets/live-prices?limit=10")
    second = client.get("/api/assets/live-prices?limit=10")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["source"] == "database"
    assert second.json()["source"] == "cache"
    assert fake_cache.set_calls == 1
    assert len(calls) == 2  # paginated fetch + full-dataset cache fill


def test_pagination(monkeypatch, client):
    cached_assets = [
        {"symbol": f"SYM{i}", "name": f"Symbol {i}", "class": "stock", "price": 100 + i}
        for i in range(12)
    ]
    monkeypatch.setattr(api_module, "redis_cache", FakeRedisCache(prices=cached_assets))

    page_one = client.get("/api/assets/live-prices?page=1&limit=5")
    page_two = client.get("/api/assets/live-prices?page=2&limit=5")

    assert page_one.status_code == 200
    assert page_two.status_code == 200
    first = page_one.json()
    second = page_two.json()

    assert first["page"] == 1
    assert first["limit"] == 5
    assert first["total"] == 12
    assert first["pages"] == 3
    assert len(first["assets"]) == 5
    assert second["page"] == 2
    assert [asset["symbol"] for asset in second["assets"]] == ["SYM5", "SYM6", "SYM7", "SYM8", "SYM9"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
