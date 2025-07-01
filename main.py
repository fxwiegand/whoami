import time
import secrets

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
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

@app.get("/{game_id}")
def join_game(game_id: str, request: Request):
    if game_id not in app.games:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse(
        request, "game.html", {"game_id": game_id}
    )

@app.post("/{game_id}/join")
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
        return JSONResponse(jsonable_encoder(player))
    player_id = secrets.token_urlsafe(8)
    app.games[game_id]["players"][player_id] = name
    return JSONResponse(jsonable_encoder(player))

@app.get("/{game_id}/players")
def get_players(game_id: str, request: Request):
    if game_id in app.games:
        if "players" in app.games[game_id]:
            return JSONResponse(jsonable_encoder(app.games[game_id]["players"]))
    return JSONResponse({})

@app.post("/{game_id}/set")
async def set_character(game_id: str, request: Request):
    print('set_character called')
    data = await request.json()
    if data["for_player"] in app.games[game_id]["characters"]:
        return jsonable_encoder({
            "error": "Für diesen Spieler wurde bereits eine Figur vergeben."}
        ), 400
    print('app.games', app.games)
    print('data', data)
    app.games[game_id]["characters"][data["for_player"]] = {
        "from": data["from_player"],
        "name": data["character"]
    }
    print('app.games after', app.games)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
@app.get("/{game_id}/reveal/{player_id}")
def reveal(game_id: str, player_id: str):
    result = {}
    if game_id in app.games:
        for pid, entry in app.games[game_id]["characters"].items():
            if pid != player_id:
                result[app.games[game_id]["players"][pid]] = entry["name"]
    if game_id in app.games and 'characters' in app.games[game_id]:
        assigned = player_id in app.games[game_id]["characters"]
    else:
        assigned = None
    return jsonable_encoder({"characters": result, "assigned": assigned})

@app.get("/cleanup")
def cleanup():
    now = time.time()
    to_delete = [gid for gid, g in app.games.items() if now - g["created"] > app.TTL_SECONDS]
    for gid in to_delete:
        del app.games[gid]
    return f"Removed {len(to_delete)} app.games."
