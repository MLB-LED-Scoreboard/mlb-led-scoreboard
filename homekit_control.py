import json
import os

CONTROL_FILE = "/tmp/scoreboard_control.json"
DEFAULT_STATE = {"on": True, "brightness": 100}


def read_control_state():
    try:
        with open(CONTROL_FILE, "r") as f:
            state = json.load(f)
        return {
            "on": bool(state.get("on", True)),
            "brightness": int(state.get("brightness", 100)),
        }
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return dict(DEFAULT_STATE)


def write_control_state(on, brightness):
    tmp = CONTROL_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"on": on, "brightness": brightness}, f)
    os.replace(tmp, CONTROL_FILE)
