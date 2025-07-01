from fastapi.testclient import TestClient
from fastapi import status

from main import app

client = TestClient(app)


def test_index_no_games():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Wer bin ich?" in response.text
    assert "Keine Spiele. Start ein neues!" in response.text
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert response.headers["content-length"] == "1501"
    assert app.games == {}


def test_new_game():
    response = client.get("/new")
    assert response.status_code == status.HTTP_200_OK
    assert "Wer bin ich?" in response.text
    assert "Beitreten" in response.text
    assert "Wähle eine Figur" in response.text
    assert "Die anderen sind:" in response.text
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert response.headers["content-length"] == "1879"
    assert len(app.games) == 1


def test_join_game_not_found():
    app.games = {}
    response = client.get("/abcdefgh")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_join_game():
    app.games = {'8KwSpmQW': {
        'created': 1751375661.8583481, 'players': {'5nCADHw5eQM': 'test'}, 'characters': {}}
    }
    response = client.get("/8KwSpmQW")
    assert response.status_code == status.HTTP_200_OK
    assert "Wer bin ich?" in response.text
    assert "Beitreten" in response.text
    assert "Wähle eine Figur" in response.text
    assert "Die anderen sind:" in response.text
