import uvicorn
import time
import secrets
import os

from fastapi import FastAPI
from fastapi.openapi.models import Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status


class Settings(BaseSettings):
    message: str

app = FastAPI()
games = {}
TTL_SECONDS = 3600

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class Player(BaseModel):
    player_id: int
    name: str


@app.get("/")
def index(request: Request):
    now = time.time()
    # Only show games that are not expired
    ongoing_games = []
    for gid, g in games.items():
        if now - g["created"] <= TTL_SECONDS:
            ongoing_games.append({
                "game_id": gid,
                "players": list(g["players"].values())
            })
    return templates.TemplateResponse("home.html", {
        "games": ongoing_games, "request": request
    })

@app.get("/new")
def new_game(request: Request):
    game_id = secrets.token_urlsafe(6)
    games[game_id] = {"created": time.time(), "players": {}, "characters": {}}
    return RedirectResponse(request.url_for("join_game", game_id=game_id))

@app.get("/{game_id}")
def join_game(game_id: str, request: Request):
    if game_id not in games:
        return "Spiel nicht gefunden", 404
    return templates.TemplateResponse("game.html", {
        "game_id": game_id, "request": request,
    })

@app.post("/{game_id}/join")
async def join(game_id: str, request: Request):
    player = await request.json()
    print(player)
    if 'name' in player:
        name = player['name']
    else:
        name = None
    if 'player_id' in player:
        player_id = player['player_id']
    else:
        player_id = None
    if player_id and player_id in games[game_id]["players"]:
        if name:
            games[game_id]["players"][player_id] = name
        else:
            name = games[game_id]["players"][player_id]
        return JSONResponse(jsonable_encoder(player))
    else:
        player_id = secrets.token_urlsafe(8)
        games[game_id]["players"][player_id] = name
        return JSONResponse(jsonable_encoder(player))

@app.get("/{game_id}/players")
def get_players(game_id: int):
    return JSONResponse(jsonable_encoder(games[game_id]["players"]))

@app.post("/{game_id}/set")
def set_character(game_id: int, request: Request):
    data = request.json
    if data["for_player"] in games[game_id]["characters"]:
        return jsonable_encoder({
            "error": "Für diesen Spieler wurde bereits eine Figur vergeben."}
        ), 400
    games[game_id]["characters"][data["for_player"]] = {
        "from": data["from_player"],
        "name": data["character"]
    }
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# @app.get("/{game_id}/reveal/{player_id}")
# def reveal(game_id: id, player_id: id, request: Request):
#     result = {}
#     for pid, entry in games[game_id]["characters"].items():
#         if pid != player_id:
#             result[games[game_id]["players"][pid]] = entry["name"]
#     assigned = player_id in games[game_id]["characters"]
#     return jsonable_encoder({"characters": result, "assigned": assigned})

@app.get("/cleanup")
def cleanup():
    now = time.time()
    to_delete = [gid for gid, g in games.items() if now - g["created"] > TTL_SECONDS]
    for gid in to_delete:
        del games[gid]
    return f"Removed {len(to_delete)} games."
