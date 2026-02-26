#!/usr/bin/env python3
"""
MLB LED Scoreboard - Web Config Server
Serves a local web page to view/edit config.json and restart the service.
Usage: python3 config_server.py [--port 8080]
"""

import argparse
import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
EXAMPLE_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.example.json")
SERVICE_NAME = "mlb-scoreboard"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MLB LED Scoreboard Config</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0f1117;
    color: #e2e8f0;
    min-height: 100vh;
    padding: 24px 16px;
  }}
  .container {{ max-width: 760px; margin: 0 auto; }}
  header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid #2d3748;
  }}
  header h1 {{ font-size: 1.4rem; font-weight: 700; color: #f7fafc; }}
  header span {{ font-size: 0.8rem; color: #718096; margin-left: auto; }}
  .alert {{
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 0.9rem;
    font-weight: 500;
  }}
  .alert-success {{ background: #1a3a2a; border: 1px solid #276749; color: #68d391; }}
  .alert-error   {{ background: #3b1a1a; border: 1px solid #c53030; color: #fc8181; }}
  .section {{
    background: #1a202c;
    border: 1px solid #2d3748;
    border-radius: 10px;
    margin-bottom: 16px;
    overflow: hidden;
  }}
  .section-header {{
    padding: 14px 18px;
    background: #2d3748;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #90cdf4;
  }}
  .field-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    border-bottom: 1px solid #2d3748;
  }}
  .field-row:last-child {{ border-bottom: none; }}
  .field-label {{
    padding: 12px 18px;
    font-size: 0.85rem;
    color: #a0aec0;
    display: flex;
    align-items: center;
    border-right: 1px solid #2d3748;
    word-break: break-word;
  }}
  .field-value {{ padding: 8px 12px; display: flex; align-items: center; }}
  input[type="text"],
  input[type="number"],
  input[type="password"] {{
    width: 100%;
    background: #2d3748;
    border: 1px solid #4a5568;
    border-radius: 6px;
    color: #e2e8f0;
    padding: 7px 10px;
    font-size: 0.85rem;
    transition: border-color 0.15s;
    outline: none;
  }}
  input:focus {{ border-color: #63b3ed; }}
  .toggle {{
    position: relative;
    width: 44px;
    height: 24px;
    flex-shrink: 0;
  }}
  .toggle input {{ opacity: 0; width: 0; height: 0; }}
  .toggle-slider {{
    position: absolute;
    inset: 0;
    background: #4a5568;
    border-radius: 24px;
    cursor: pointer;
    transition: background 0.2s;
  }}
  .toggle-slider:before {{
    content: "";
    position: absolute;
    width: 18px;
    height: 18px;
    left: 3px;
    top: 3px;
    background: white;
    border-radius: 50%;
    transition: transform 0.2s;
  }}
  .toggle input:checked + .toggle-slider {{ background: #3182ce; }}
  .toggle input:checked + .toggle-slider:before {{ transform: translateX(20px); }}
  .actions {{
    display: flex;
    gap: 12px;
    margin-top: 24px;
    flex-wrap: wrap;
  }}
  button {{
    padding: 11px 24px;
    border: none;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s, transform 0.1s;
  }}
  button:active {{ transform: scale(0.98); }}
  .btn-primary {{ background: #3182ce; color: white; }}
  .btn-primary:hover {{ opacity: 0.85; }}
  .btn-restart {{ background: #276749; color: white; }}
  .btn-restart:hover {{ opacity: 0.85; }}
  .btn-danger {{ background: #c53030; color: white; }}
  .btn-danger:hover {{ opacity: 0.85; }}
  .note {{ font-size: 0.78rem; color: #718096; margin-top: 12px; }}
  @media (max-width: 500px) {{
    .field-row {{ grid-template-columns: 1fr; }}
    .field-label {{ border-right: none; border-bottom: 1px solid #2d3748; }}
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>MLB LED Scoreboard</h1>
    <span>Config Editor</span>
  </header>

  {alert_html}

  <form method="POST" action="/save">

    <div class="section">
      <div class="section-header">Preferred Teams &amp; Divisions</div>
      <div class="field-row">
        <div class="field-label">Teams (comma-separated)</div>
        <div class="field-value">
          <input type="text" name="preferred__teams" value="{preferred__teams}">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Divisions (comma-separated)</div>
        <div class="field-value">
          <input type="text" name="preferred__divisions" value="{preferred__divisions}">
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">News Ticker</div>
      <div class="field-row">
        <div class="field-label">Show on team off-day</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="news_ticker__team_offday" {news_ticker__team_offday}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Always display</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="news_ticker__always_display" {news_ticker__always_display}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Show preferred teams news</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="news_ticker__preferred_teams" {news_ticker__preferred_teams}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Show when no games live</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="news_ticker__display_no_games_live" {news_ticker__display_no_games_live}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Trade rumors</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="news_ticker__traderumors" {news_ticker__traderumors}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">MLB news</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="news_ticker__mlb_news" {news_ticker__mlb_news}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Countdowns</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="news_ticker__countdowns" {news_ticker__countdowns}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Show date</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="news_ticker__date" {news_ticker__date}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Date format</div>
        <div class="field-value">
          <input type="text" name="news_ticker__date_format" value="{news_ticker__date_format}">
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">Standings</div>
      <div class="field-row">
        <div class="field-label">Show on team off-day</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="standings__team_offday" {standings__team_offday}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Show on MLB off-day</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="standings__mlb_offday" {standings__mlb_offday}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Always display</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="standings__always_display" {standings__always_display}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Show when no games live</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="standings__display_no_games_live" {standings__display_no_games_live}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">Rotation</div>
      <div class="field-row">
        <div class="field-label">Enabled</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="rotation__enabled" {rotation__enabled}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Scroll until finished</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="rotation__scroll_until_finished" {rotation__scroll_until_finished}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Only preferred teams</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="rotation__only_preferred" {rotation__only_preferred}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Only live games</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="rotation__only_live" {rotation__only_live}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Rate: live (seconds)</div>
        <div class="field-value">
          <input type="number" name="rotation__rates__live" value="{rotation__rates__live}" min="2" step="0.5">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Rate: final (seconds)</div>
        <div class="field-value">
          <input type="number" name="rotation__rates__final" value="{rotation__rates__final}" min="2" step="0.5">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Rate: pregame (seconds)</div>
        <div class="field-value">
          <input type="number" name="rotation__rates__pregame" value="{rotation__rates__pregame}" min="2" step="0.5">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Preferred team live: enabled</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="rotation__while_preferred_team_live__enabled" {rotation__while_preferred_team_live__enabled}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Preferred team live: during inning breaks</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="rotation__while_preferred_team_live__during_inning_breaks" {rotation__while_preferred_team_live__during_inning_breaks}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">Weather</div>
      <div class="field-row">
        <div class="field-label">API Key</div>
        <div class="field-value">
          <input type="text" name="weather__apikey" value="{weather__apikey}" placeholder="OpenWeatherMap API key">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Location</div>
        <div class="field-value">
          <input type="text" name="weather__location" value="{weather__location}" placeholder="e.g. Chicago,il,us">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Metric units</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="weather__metric_units" {weather__metric_units}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">General</div>
      <div class="field-row">
        <div class="field-label">Time format</div>
        <div class="field-value">
          <input type="text" name="time_format" value="{time_format}" placeholder="12h or 24h">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">End of day (HH:MM)</div>
        <div class="field-value">
          <input type="text" name="end_of_day" value="{end_of_day}" placeholder="00:00">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Full team names</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="full_team_names" {full_team_names}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Short names for runs/hits</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="short_team_names_for_runs_hits" {short_team_names_for_runs_hits}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Pregame weather</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="pregame_weather" {pregame_weather}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Preferred game delay multiplier</div>
        <div class="field-value">
          <input type="number" name="preferred_game_delay_multiplier" value="{preferred_game_delay_multiplier}" min="0" step="1">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">API refresh rate (seconds)</div>
        <div class="field-value">
          <input type="number" name="api_refresh_rate" value="{api_refresh_rate}" min="3" step="1">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Scrolling speed (0-6)</div>
        <div class="field-value">
          <input type="number" name="scrolling_speed" value="{scrolling_speed}" min="0" max="6" step="1">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Debug mode</div>
        <div class="field-value">
          <label class="toggle">
            <input type="checkbox" name="debug" {debug}>
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Demo date (YYYY-MM-DD or false)</div>
        <div class="field-value">
          <input type="text" name="demo_date" value="{demo_date}" placeholder="false or 2024-04-01">
        </div>
      </div>
    </div>

    <div class="actions">
      <button type="submit" name="action" value="save" class="btn-primary">Save</button>
      <button type="submit" name="action" value="save_restart" class="btn-restart">Save &amp; Restart Service</button>
    </div>
    <p class="note">Config is saved to <code>config.json</code> in the project directory. Restart applies to the <code>{service_name}</code> systemd service.</p>
  </form>
</div>
</body>
</html>"""


def load_config():
    """Load the merged config (example as base, config.json as overrides)."""
    config = {}
    if os.path.isfile(EXAMPLE_CONFIG_FILE):
        with open(EXAMPLE_CONFIG_FILE) as f:
            config = json.load(f)
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            user_config = json.load(f)
        config = deep_update(config, user_config)
    return config


def deep_update(base, overrides):
    result = dict(base)
    for k, v in overrides.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_update(result[k], v)
        else:
            result[k] = v
    return result


def config_to_form_values(config):
    """Flatten config into form field values."""
    def checked(val):
        return "checked" if val else ""

    c = config
    return {
        "preferred__teams": ", ".join(c["preferred"]["teams"]) if isinstance(c["preferred"]["teams"], list) else c["preferred"]["teams"],
        "preferred__divisions": ", ".join(c["preferred"]["divisions"]) if isinstance(c["preferred"]["divisions"], list) else c["preferred"]["divisions"],
        "news_ticker__team_offday": checked(c["news_ticker"]["team_offday"]),
        "news_ticker__always_display": checked(c["news_ticker"]["always_display"]),
        "news_ticker__preferred_teams": checked(c["news_ticker"]["preferred_teams"]),
        "news_ticker__display_no_games_live": checked(c["news_ticker"]["display_no_games_live"]),
        "news_ticker__traderumors": checked(c["news_ticker"]["traderumors"]),
        "news_ticker__mlb_news": checked(c["news_ticker"]["mlb_news"]),
        "news_ticker__countdowns": checked(c["news_ticker"]["countdowns"]),
        "news_ticker__date": checked(c["news_ticker"]["date"]),
        "news_ticker__date_format": c["news_ticker"]["date_format"],
        "standings__team_offday": checked(c["standings"]["team_offday"]),
        "standings__mlb_offday": checked(c["standings"]["mlb_offday"]),
        "standings__always_display": checked(c["standings"]["always_display"]),
        "standings__display_no_games_live": checked(c["standings"]["display_no_games_live"]),
        "rotation__enabled": checked(c["rotation"]["enabled"]),
        "rotation__scroll_until_finished": checked(c["rotation"]["scroll_until_finished"]),
        "rotation__only_preferred": checked(c["rotation"]["only_preferred"]),
        "rotation__only_live": checked(c["rotation"]["only_live"]),
        "rotation__rates__live": c["rotation"]["rates"]["live"],
        "rotation__rates__final": c["rotation"]["rates"]["final"],
        "rotation__rates__pregame": c["rotation"]["rates"]["pregame"],
        "rotation__while_preferred_team_live__enabled": checked(c["rotation"]["while_preferred_team_live"]["enabled"]),
        "rotation__while_preferred_team_live__during_inning_breaks": checked(c["rotation"]["while_preferred_team_live"]["during_inning_breaks"]),
        "weather__apikey": c["weather"]["apikey"],
        "weather__location": c["weather"]["location"],
        "weather__metric_units": checked(c["weather"]["metric_units"]),
        "time_format": c["time_format"],
        "end_of_day": c["end_of_day"],
        "full_team_names": checked(c["full_team_names"]),
        "short_team_names_for_runs_hits": checked(c["short_team_names_for_runs_hits"]),
        "pregame_weather": checked(c["pregame_weather"]),
        "preferred_game_delay_multiplier": c["preferred_game_delay_multiplier"],
        "api_refresh_rate": c["api_refresh_rate"],
        "scrolling_speed": c["scrolling_speed"],
        "debug": checked(c["debug"]),
        "demo_date": str(c["demo_date"]) if c["demo_date"] else "false",
        "service_name": SERVICE_NAME,
        "alert_html": "",
    }


def form_data_to_config(fields):
    """Convert flat form POST fields back to nested config dict."""
    def get(key, default=""):
        vals = fields.get(key, [default])
        return vals[0] if vals else default

    def checkbox(key):
        return key in fields

    def split_list(val):
        return [x.strip() for x in val.split(",") if x.strip()]

    demo_raw = get("demo_date", "false").strip()
    demo_val = False if demo_raw.lower() in ("false", "") else demo_raw

    return {
        "preferred": {
            "teams": split_list(get("preferred__teams")),
            "divisions": split_list(get("preferred__divisions")),
        },
        "news_ticker": {
            "team_offday": checkbox("news_ticker__team_offday"),
            "always_display": checkbox("news_ticker__always_display"),
            "preferred_teams": checkbox("news_ticker__preferred_teams"),
            "display_no_games_live": checkbox("news_ticker__display_no_games_live"),
            "traderumors": checkbox("news_ticker__traderumors"),
            "mlb_news": checkbox("news_ticker__mlb_news"),
            "countdowns": checkbox("news_ticker__countdowns"),
            "date": checkbox("news_ticker__date"),
            "date_format": get("news_ticker__date_format"),
        },
        "standings": {
            "team_offday": checkbox("standings__team_offday"),
            "mlb_offday": checkbox("standings__mlb_offday"),
            "always_display": checkbox("standings__always_display"),
            "display_no_games_live": checkbox("standings__display_no_games_live"),
        },
        "rotation": {
            "enabled": checkbox("rotation__enabled"),
            "scroll_until_finished": checkbox("rotation__scroll_until_finished"),
            "only_preferred": checkbox("rotation__only_preferred"),
            "only_live": checkbox("rotation__only_live"),
            "rates": {
                "live": float(get("rotation__rates__live", "15.0")),
                "final": float(get("rotation__rates__final", "15.0")),
                "pregame": float(get("rotation__rates__pregame", "15.0")),
            },
            "while_preferred_team_live": {
                "enabled": checkbox("rotation__while_preferred_team_live__enabled"),
                "during_inning_breaks": checkbox("rotation__while_preferred_team_live__during_inning_breaks"),
            },
        },
        "weather": {
            "apikey": get("weather__apikey"),
            "location": get("weather__location"),
            "metric_units": checkbox("weather__metric_units"),
        },
        "time_format": get("time_format", "12h"),
        "end_of_day": get("end_of_day", "00:00"),
        "full_team_names": checkbox("full_team_names"),
        "short_team_names_for_runs_hits": checkbox("short_team_names_for_runs_hits"),
        "pregame_weather": checkbox("pregame_weather"),
        "preferred_game_delay_multiplier": int(float(get("preferred_game_delay_multiplier", "0"))),
        "api_refresh_rate": int(float(get("api_refresh_rate", "5"))),
        "scrolling_speed": int(float(get("scrolling_speed", "2"))),
        "debug": checkbox("debug"),
        "demo_date": demo_val,
    }


def restart_service():
    """Attempt to restart the systemd service. Returns (success, message)."""
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "restart", SERVICE_NAME],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return True, f"Service '{SERVICE_NAME}' restarted successfully."
        return False, f"Failed to restart service: {result.stderr.strip() or 'unknown error'}"
    except FileNotFoundError:
        return False, "systemctl not found — are you running on a Pi with systemd?"
    except subprocess.TimeoutExpired:
        return False, "Service restart timed out."
    except Exception as e:
        return False, f"Error restarting service: {e}"


class ConfigHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

    def send_html(self, html, status=200):
        encoded = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if urlparse(self.path).path not in ("/", "/index.html"):
            self.send_response(404)
            self.end_headers()
            return
        try:
            config = load_config()
            values = config_to_form_values(config)
            html = HTML_TEMPLATE.format(**values)
            self.send_html(html)
        except Exception as e:
            self.send_html(f"<pre>Error loading config: {e}</pre>", 500)

    def do_POST(self):
        if urlparse(self.path).path != "/save":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        fields = parse_qs(body, keep_blank_values=True)

        action = fields.get("action", ["save"])[0]

        try:
            new_config = form_data_to_config(fields)
            with open(CONFIG_FILE, "w") as f:
                json.dump(new_config, f, indent="\t")

            alert = ""
            if action == "save_restart":
                ok, msg = restart_service()
                if ok:
                    alert = f'<div class="alert alert-success">Saved. {msg}</div>'
                else:
                    alert = f'<div class="alert alert-error">Saved, but restart failed: {msg}</div>'
            else:
                alert = '<div class="alert alert-success">Config saved successfully.</div>'

        except Exception as e:
            alert = f'<div class="alert alert-error">Error saving config: {e}</div>'

        try:
            config = load_config()
            values = config_to_form_values(config)
            values["alert_html"] = alert
            html = HTML_TEMPLATE.format(**values)
        except Exception as e:
            html = f"<pre>{alert}\n\nError reloading config: {e}</pre>"

        self.send_html(html)


def main():
    parser = argparse.ArgumentParser(description="MLB LED Scoreboard web config server")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), ConfigHandler)
    print(f"Config server running at http://{args.host}:{args.port}")
    print(f"Config file: {CONFIG_FILE}")
    print(f"Service name: {SERVICE_NAME}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
