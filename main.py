import time
import secrets

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.games = {}
app.TTL_SECONDS = 3600

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request):
    now = time.time()
    # Only show games that are not expired
    ongoing_games = []
    for gid, g in app.games.items():
        if now - g["created"] <= app.TTL_SECONDS:
            ongoing_games.append({
                "game_id": gid,
                "players": list(g["players"].values())
            })
    return templates.TemplateResponse(
        request, "home.html", context={"ongoing_games": ongoing_games}
    )


@app.get("/new")
def new_game(request: Request):
    game_id = secrets.token_urlsafe(6)
    app.games[game_id] = {"created": time.time(), "players": {}, "characters": {}}
    return RedirectResponse(request.url_for("join_game", game_id=game_id))


@app.get("/join_game/{game_id}")
def join_game(game_id: str, request: Request):
    if game_id not in app.games:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse(
        request, "game.html", {"game_id": game_id}
    )


@app.post("/rejoin/{game_id}")
async def join(game_id: str, request: Request):
    player = await request.json()
    name = player_id = None
    if 'name' in player:
        name = player['name']
    if 'player_id' in player:
        player_id = player['player_id']
    if player_id and player_id in app.games[game_id]["players"]:
        if name:
            app.games[game_id]["players"][player_id] = name
        else:
            name = app.games[game_id]["players"][player_id]
        return JSONResponse(player)
    player_id = secrets.token_urlsafe(8)
    app.games[game_id]["players"][player_id] = name
    return JSONResponse(player)


@app.get("/players/{game_id}")
def get_players(game_id: str, request: Request):
    if game_id in app.games:
        if "players" in app.games[game_id]:
            return JSONResponse(app.games[game_id]["players"])
    return JSONResponse({})


@app.post("/set/{game_id}")
async def set_character(game_id: str, request: Request):
    data = await request.json()
    if data["for_player"] in app.games[game_id]["characters"]:
        return JSONResponse({
            "error": "Für diesen Spieler wurde bereits eine Figur vergeben."}
        ), 400
    for_player = data["for_player"]
    app.games[game_id]["characters"][for_player] = {
        "from": for_player,
        "name": data["character"]
    }
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/reveal/{game_id}/{player_id}")
def reveal(game_id: str, player_id: str):
    result = {}
    for pid, entry in app.games[game_id]["characters"].items():
        if pid != player_id:
            result[app.games[game_id]["players"][pid]] = entry["name"]
    assigned = player_id in app.games[game_id]["characters"]
    return JSONResponse({"characters": result, "assigned": assigned})


@app.get("/cleanup")
def cleanup(request: Request):
    now = time.time()
    to_delete = [gid for gid, g in app.games.items() if now - g["created"] > app.TTL_SECONDS]
    message = f"Removed {len(to_delete)} app.games."
    for gid in to_delete:
        del app.games[gid]
    return JSONResponse({"message": message})
