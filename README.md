# MapQuest Directions App

A small Flask web app wrapping your original `mapquest_parsing.py` script in a browser UI.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root (see `.env.example`) with your key:

```
MAPQUEST_API_KEY=your_key_here
```

Then run:

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## How it works

- **`app.py`** is a Flask backend with three routes:
  - `GET /` — serves the page (`templates/index.html`).
  - `POST /api/route` — takes `{orig, dest, routeType}` as JSON, calls the MapQuest Directions API, and returns plain JSON with duration/distance/fuel/maneuvers or an error.
  - `GET /api/staticmap` — proxies MapQuest's Static Map API, so a route map image can be shown without ever exposing the API key to the browser.
- **`templates/index.html`** is plain HTML/CSS with a small amount of vanilla JavaScript (no framework). It POSTs to `/api/route`, renders the JSON response into the page, and loads the map image from `/api/staticmap`.
- Fuel: if MapQuest's response doesn't include `fuelUsed` (this varies by key/plan), the app estimates it as `distance ÷ 22 mpg` and labels it "fuel (est.)" so it's clear it's not a MapQuest-reported number. This only happens for driving routes (fastest/shortest) — pedestrian/bicycle routes correctly show no fuel stat.

## Features

- Plot a route between two locations with a chosen mode (fastest / shortest / pedestrian / bicycle).
- A styled route map image alongside the turn-by-turn directions.
- Swap button (⇄) to flip From/To.
- Searches are reflected in the URL (`?orig=...&dest=...&routeType=...`), so links are shareable/bookmarkable and reloading the page with those params re-plots automatically.
- Mobile-responsive layout below ~480px width.

## What changed vs. the original script

- Same MapQuest API call, status-code handling (0 / 402 / 611 / other), and km conversion logic.
- The `while True` / `input()` console loop is replaced by a Flask + JS form: you type start/destination/route type into a web page instead of the terminal, and hit "Plot route".
- Results (duration, miles, fuel, maneuvers) render via JavaScript instead of `print()` statements.
- Errors (bad status codes, missing API key, network issues) show in a styled error box instead of being printed.

## Files

- `app.py` — Flask backend: route-fetching logic, JSON API, static map proxy.
- `templates/index.html` — the UI (form, results, map, all client-side rendering).
- `requirements.txt` — dependencies.
- `.env.example` — template for the required environment variable (copy to `.env` and fill in your key; `.env` is gitignored).