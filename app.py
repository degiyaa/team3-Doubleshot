import os
import urllib.parse

import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

MAIN_API = "https://mapquestapi.com/directions/v2/route?"
STATIC_MAP_API = "https://www.mapquestapi.com/staticmap/v5/map?"
KEY = os.getenv("MAPQUEST_API_KEY")

VALID_ROUTE_TYPES = ["fastest", "shortest", "pedestrian", "bicycle"]
ASSUMED_MPG = 22  # used to estimate fuel when MapQuest doesn't return fuelUsed


def get_route(orig, dest, route_type):
    """Call the MapQuest Directions API and return a plain result dict (JSON-serializable)."""
    if not KEY:
        return {"error": "Server is missing MAPQUEST_API_KEY. Set it as an environment variable."}

    url = MAIN_API + urllib.parse.urlencode(
        {
            "key": KEY,
            "from": orig,
            "to": dest,
            "routeType": route_type,
            "highwayEfficiency": ASSUMED_MPG,
            "drivingStyle": 2,
        }
    )

    try:
        json_data = requests.get(url, timeout=15).json()
    except requests.RequestException as e:
        return {"error": f"Request to MapQuest failed: {e}"}

    status = json_data.get("info", {}).get("statuscode")

    if status == 0:
        route = json_data["route"]
        maneuvers = [
            {
                "narrative": step["narrative"],
                "km": "{:.2f}".format(step["distance"] * 1.61),
            }
            for step in route["legs"][0]["maneuvers"]
        ]

        fuel = route.get("fuelUsed")
        fuel_is_estimate = False
        if fuel is None and route_type in ("fastest", "shortest"):
            distance = route.get("distance")
            if distance:
                fuel = round(distance / ASSUMED_MPG, 2)
                fuel_is_estimate = True

        return {
            "orig": orig,
            "dest": dest,
            "route_type": route_type,
            "duration": route.get("formattedTime"),
            "miles": route.get("distance"),
            "fuel": fuel,
            "fuel_is_estimate": fuel_is_estimate,
            "maneuvers": maneuvers,
            "session_id": route.get("sessionId"),
        }
    elif status == 402:
        return {"error": f"Status {status}: Invalid user inputs for one or both locations."}
    elif status == 611:
        return {"error": f"Status {status}: Missing an entry for one or both locations."}
    else:
        return {
            "error": f"Status {status}. See "
            "https://developer.mapquest.com/documentation/directions-api/status-codes"
        }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/route", methods=["POST"])
def api_route():
    data = request.get_json(silent=True) or {}
    orig = (data.get("orig") or "").strip()
    dest = (data.get("dest") or "").strip()
    route_type = (data.get("routeType") or "").strip().lower()

    if route_type not in VALID_ROUTE_TYPES:
        route_type = "fastest"

    if not orig or not dest:
        return jsonify({"error": "Please fill in both a starting location and a destination."})

    return jsonify(get_route(orig, dest, route_type))


@app.route("/api/staticmap")
def api_staticmap():
    """Proxy a MapQuest Static Map image so the API key never reaches the browser.

    Prefers rendering the exact computed route via `session` (matches the
    chosen routeType — fastest/shortest/pedestrian/bicycle). Falls back to a
    generic start/end route if no session is available or it has expired.
    """
    session_id = (request.args.get("session") or "").strip()
    orig = (request.args.get("orig") or "").strip()
    dest = (request.args.get("dest") or "").strip()

    if not session_id and (not orig or not dest):
        return "Missing session or orig/dest", 400
    if not KEY:
        return "Server is missing MAPQUEST_API_KEY.", 500

    params = {
        "key": KEY,
        "size": "640,320@2x",
        "type": "map",
    }
    if session_id:
        params["session"] = session_id
    else:
        params["start"] = orig
        params["end"] = dest

    url = STATIC_MAP_API + urllib.parse.urlencode(params)

    try:
        upstream = requests.get(url, timeout=15)
    except requests.RequestException as e:
        return f"Request to MapQuest failed: {e}", 502

    return Response(
        upstream.content,
        status=upstream.status_code,
        content_type=upstream.headers.get("Content-Type", "image/png"),
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)