from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid, time, secrets

app = Flask(__name__)
games = {}
TTL_SECONDS = 3600

@app.route("/")
def index():
    return redirect("/new")

@app.route("/new")
def new_game():
    game_id = secrets.token_urlsafe(6)
    games[game_id] = {"created": time.time(), "players": {}, "characters": {}}
    return redirect(url_for("join_game", game_id=game_id))

@app.route("/<game_id>")
def join_game(game_id):
    if game_id not in games:
        return "Spiel nicht gefunden", 404
    return render_template("game.html", game_id=game_id)

@app.route("/<game_id>/join", methods=["POST"])
def join(game_id):
    name = request.json.get("name")
    player_id = request.json.get("player_id")
    if player_id and player_id in games[game_id]["players"]:
        if name:
            games[game_id]["players"][player_id] = name
        else:
            name = games[game_id]["players"][player_id]
        return jsonify({"player_id": player_id, "name": name})
    else:
        player_id = secrets.token_urlsafe(8)
        games[game_id]["players"][player_id] = name
        return jsonify({"player_id": player_id, "name": name})

@app.route("/<game_id>/players")
def get_players(game_id):
    return jsonify(games[game_id]["players"])

@app.route("/<game_id>/set", methods=["POST"])
def set_character(game_id):
    data = request.json
    if data["for_player"] in games[game_id]["characters"]:
        return jsonify({"error": "Für diesen Spieler wurde bereits eine Figur vergeben."}), 400
    games[game_id]["characters"][data["for_player"]] = {
        "from": data["from_player"],
        "name": data["character"]
    }
    return "", 204

@app.route("/<game_id>/reveal/<player_id>")
def reveal(game_id, player_id):
    result = {}
    for pid, entry in games[game_id]["characters"].items():
        if pid != player_id:
            result[games[game_id]["players"][pid]] = entry["name"]
    assigned = player_id in games[game_id]["characters"]
    return jsonify({"characters": result, "assigned": assigned})

@app.route("/cleanup")
def cleanup():
    now = time.time()
    to_delete = [gid for gid, g in games.items() if now - g["created"] > TTL_SECONDS]
    for gid in to_delete:
        del games[gid]
    return f"Removed {len(to_delete)} games."

if __name__ == "__main__":
    app.run(debug=True)
