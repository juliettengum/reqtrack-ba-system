
import pytest
import app as reqtrack


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_database = tmp_path / "test_reqtrack.db"

    monkeypatch.setattr(reqtrack, "DATABASE", test_database)
    reqtrack.init_db()

    reqtrack.app.config.update(TESTING=True)

    with reqtrack.app.test_client() as client:
        yield client


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ReqTrack" in response.data


def test_create_requirement(client):
    response = client.post("/add", data={
        "title": "User Authentication",
        "description": "Users must be able to log in.",
        "type": "Functional",
        "priority": "High"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"User Authentication" in response.data
    assert b"REQ-001" in response.data


def test_missing_title(client):
    response = client.post("/add", data={
        "title": "",
        "description": "A requirement without a title",
        "type": "Functional",
        "priority": "High"
    })

    assert response.status_code == 400


def test_update_status(client):
    client.post("/add", data={
        "title": "Export Reports",
        "description": "Users can export reports.",
        "type": "Functional",
        "priority": "Medium"
    })

    response = client.post(
        "/status/1",
        data={"status": "Approved"},
        follow_redirects=True
    )

    assert response.status_code == 200

    with reqtrack.get_db() as db:
        requirement = db.execute(
            "SELECT status FROM requirements WHERE id = 1"
        ).fetchone()

    assert requirement["status"] == "Approved"


def test_invalid_status(client):
    response = client.post(
        "/status/1",
        data={"status": "Unknown"}
    )

    assert response.status_code == 400


def test_nonexistent_requirement(client):
    response = client.post(
        "/status/999",
        data={"status": "Approved"}
    )

    assert response.status_code == 404
