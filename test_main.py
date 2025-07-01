from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_index_no_games():
    response = client.get("/")
    assert response.status_code == 200
    assert "Wer bin ich?" in response.text
    assert "Keine Spiele. Start ein neues!" in response.text
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert response.headers["content-length"] == "1501"
    assert app.games == {}


def test_new_game():
    response = client.get("/new")
    assert response.status_code == 200
    assert "Wer bin ich?" in response.text
    assert "Beitreten" in response.text
    assert "Wähle eine Figur" in response.text
    assert "Die anderen sind:" in response.text
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert response.headers["content-length"] == "1879"
    assert len(app.games) == 1


def test_join_game_not_found():
    response = client.post("/join/abcdefgh")
    assert response.status_code == 404


def test_join_game():
    app.games = {'G0LqkhMX': {'characters': {}, 'created': 1751375113.527828, 'players': {}}}
    response = client.get("/joinG0LqkhMX")
    assert response.status_code == 200