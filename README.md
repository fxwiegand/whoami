# Wer bin ich? – Flask Partyspiel

**"Wer bin ich?"** ist ein einfaches, browserbasiertes Partyspiel, das mit Python und Flask umgesetzt ist. Jeder Spieler bekommt von einem Mitspieler eine berühmte Persönlichkeit oder Figur zugewiesen und muss erraten, wer er ist.

## Features

- Schnelles Erstellen und Teilen von Spielen per Link
- Wiedereinstieg für Spieler über persönlichen Link
- Automatische Aktualisierung der Spieler- und Ergebnislisten
- Einladungslink für Freunde
- Modernes, responsives UI (funktioniert auf Desktop und Mobile)

## Installation

1. **Repository klonen**

   GitHub: [https://github.com/fxwiegand/whoami](https://github.com/fxwiegand/whoami)

   ```bash
   git clone https://github.com/fxwiegand/whoami.git
   cd whoami
   ```

2. **Abhängigkeiten installieren**

   Am einfachsten per pip:

   ```bash
   pip install -r requirements.txt
   ```

3. **Server starten**

   ```bash
   python app.py
   ```

   Du kannst Host, Port und Debug-Modus per Umgebungsvariablen steuern (optional):

   ```bash
   WHOAMI_HOST=0.0.0.0 WHOAMI_PORT=8080 WHOAMI_DEBUG=0 python app.py
   ```

   Standardwerte sind:
   - `WHOAMI_HOST=127.0.0.1`
   - `WHOAMI_PORT=5000`
   - `WHOAMI_DEBUG=1` (aktiviert Debug-Modus)

4. **Im Browser öffnen**

   Gehe zu [http://localhost:5000](http://localhost:5000)

## Dateien

- `app.py` – Flask Backend, Spiellogik und API
- `static/script.js` – Frontend-Logik (JS)
- `templates/game.html` – HTML-Template für das Spiel
- `requirements.txt` – Python-Abhängigkeiten

## Hinweise

- Das Spiel speichert alle Daten nur im RAM. Nach einem Neustart des Servers sind alle Spiele gelöscht.
- Für produktiven Einsatz sollte ein echtes Datenbank-Backend verwendet werden.
- Die Cleanup-Route `/cleanup` entfernt abgelaufene Spiele (TTL 1 Stunde).

## Lizenz

MIT License

---

Viel Spaß beim Spielen! 🎉
