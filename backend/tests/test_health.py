from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "CityOS"
    assert body["municipality"] == "Klina"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("ok", "degraded")
    assert "database" in body


def test_coverage_never_fakes_presence():
    r = client.get("/api/v1/coverage")
    assert r.status_code == 200
    body = r.json()
    assert body["municipality"] == "Klina"
    for item in body["items"]:
        assert item["status"] in ("present", "partial", "missing")
        if item["layer"] == "3d_buildings":
            # Until real 3D is imported, must not claim coverage
            assert item["has_3d"] is False or item["status"] != "present"


def test_empty_geo_endpoints():
    for path in ("/api/v1/geo/boundary", "/api/v1/geo/settlements", "/api/v1/geo/buildings"):
        r = client.get(path)
        assert r.status_code == 200
        body = r.json()
        assert body["type"] == "FeatureCollection"
        assert isinstance(body["features"], list)
