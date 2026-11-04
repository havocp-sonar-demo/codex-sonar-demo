import pytest

import app as app_module
import db

TEST_PASSWORD = "hunter2-admin-password"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_search(client):
    resp = client.get("/invoices/search?q=Acme", headers={"X-User": "alice"})
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_get_invoice(client):
    assert client.get("/invoices/1").status_code == 200
    assert client.get("/invoices/999").status_code == 404


def test_thumbnail(client):
    assert "cache_key" in client.get("/invoices/1/thumbnail").get_json()


def test_export(client):
    resp = client.get("/invoices/1/export")
    assert resp.data.startswith(b"%PDF")
    resp.close()
