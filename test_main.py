from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_index_no_games():
    response = client.get("/")
    assert response.status_code == 200
    assert "Wer bin ich?" in response.text
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"


def test_index_with_games():
    response = client.get("/")
    assert response.status_code == 200
    assert "Wer bin ich?" in response.text
    assert 'Rr23kQwE' in response.text
