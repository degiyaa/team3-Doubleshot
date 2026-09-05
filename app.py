import os
import urllib.parse

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

MAIN_API = "https://mapquestapi.com/directions/v2/route?"
KEY = os.getenv("MAPQUEST_API_KEY")

VALID_ROUTE_TYPES = ["fastest", "shortest", "pedestrian", "bicycle"]


def get_route(orig, dest, route_type):
    """Call the MapQuest Directions API and return a plain result dict (JSON-serializable)."""
    if not KEY:
        return {"error": "Server is missing MAPQUEST_API_KEY. Set it as an environment variable."}

    url = MAIN_API + urllib.parse.urlencode(
        {"key": KEY, "from": orig, "to": dest, "routeType": route_type}
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

        return {
            "orig": orig,
            "dest": dest,
            "route_type": route_type,
            "duration": route.get("formattedTime"),
            "miles": route.get("distance"),
            "fuel": route.get("fuelUsed", "N/A"),
            "maneuvers": maneuvers,
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
