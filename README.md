whoami/README.md
```

# Who am I? – Flask Party Game

**"Who am I?"** is a simple, browser-based party game built with Python and Flask. Each player is assigned a famous person or character by another player and must guess who they are.

## Features

- Quickly create and share games via link
- Players can rejoin using their personal link
- Automatic updating of player and result lists
- Invitation link for friends
- Modern, responsive UI (works on desktop and mobile)

## Installation

1. **Clone the repository**

   GitHub: [https://github.com/fxwiegand/whoami](https://github.com/fxwiegand/whoami)

   ```bash
   git clone https://github.com/fxwiegand/whoami.git
   cd whoami
   ```

2. **Install dependencies**

   The easiest way is via pip:

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**

   ```bash
   python app.py
   ```

   You can control host, port, and debug mode via environment variables (optional):

   ```bash
   WHOAMI_HOST=0.0.0.0 WHOAMI_PORT=8080 WHOAMI_DEBUG=0 python app.py
   ```

   Default values are:
   - `WHOAMI_HOST=127.0.0.1`
   - `WHOAMI_PORT=5000`
   - `WHOAMI_DEBUG=1` (enables debug mode)

4. **Open in your browser**

   Go to [http://localhost:5000](http://localhost:5000)

## Files

- `app.py` – Flask backend, game logic, and API
- `static/script.js` – Frontend logic (JS)
- `templates/game.html` – HTML template for the game
- `requirements.txt` – Python dependencies

## Notes

- The game stores all data in RAM only. All games are deleted after a server restart.
- For production use, a real database backend is recommended.
- The cleanup route `/cleanup` removes expired games (TTL 1 hour).

## License

MIT License

---

Have fun playing! 🎉
