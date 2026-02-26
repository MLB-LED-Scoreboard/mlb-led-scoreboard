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

MLB_TEAMS = [
    # AL East
    "Yankees", "Red Sox", "Blue Jays", "Rays", "Orioles",
    # AL Central
    "White Sox", "Guardians", "Tigers", "Royals", "Twins",
    # AL West
    "Astros", "Angels", "Athletics", "Mariners", "Rangers",
    # NL East
    "Braves", "Marlins", "Mets", "Phillies", "Nationals",
    # NL Central
    "Cubs", "Reds", "Brewers", "Pirates", "Cardinals",
    # NL West
    "Diamondbacks", "Rockies", "Dodgers", "Padres", "Giants",
]

MLB_TEAMS_BY_DIVISION = {
    "AL East":    ["Yankees", "Red Sox", "Blue Jays", "Rays", "Orioles"],
    "AL Central": ["White Sox", "Guardians", "Tigers", "Royals", "Twins"],
    "AL West":    ["Astros", "Angels", "Athletics", "Mariners", "Rangers"],
    "NL East":    ["Braves", "Marlins", "Mets", "Phillies", "Nationals"],
    "NL Central": ["Cubs", "Reds", "Brewers", "Pirates", "Cardinals"],
    "NL West":    ["Diamondbacks", "Rockies", "Dodgers", "Padres", "Giants"],
}

DIVISIONS = [
    "AL East", "AL Central", "AL West",
    "NL East", "NL Central", "NL West",
    "AL Wild Card", "NL Wild Card",
]


def build_team_checkboxes(selected_teams):
    selected_set = set(selected_teams)
    parts = []
    for div_name, teams in MLB_TEAMS_BY_DIVISION.items():
        parts.append(f'<div class="cb-group-label">{div_name}</div>')
        for team in teams:
            chk = "checked" if team in selected_set else ""
            parts.append(
                f'<label class="cb-item">'
                f'<input type="checkbox" name="preferred__teams" value="{team}" {chk}>'
                f'<span>{team}</span></label>'
            )
    return "\n".join(parts)


def build_division_checkboxes(selected_divs):
    selected_set = set(selected_divs)
    parts = []
    for div in DIVISIONS:
        chk = "checked" if div in selected_set else ""
        parts.append(
            f'<label class="cb-item">'
            f'<input type="checkbox" name="preferred__divisions" value="{div}" {chk}>'
            f'<span>{div}</span></label>'
        )
    return "\n".join(parts)


def build_time_format_radios(current):
    r12 = "checked" if current in ("12h", "%-I:%M") else ""
    r24 = "checked" if current in ("24h", "%H:%M") else ""
    return f"""
      <label class="radio-item">
        <input type="radio" name="time_format" value="12h" {r12}> 12h
      </label>
      <label class="radio-item">
        <input type="radio" name="time_format" value="24h" {r24}> 24h
      </label>"""


def build_scrolling_speed_slider(current):
    val = int(current) if str(current).isdigit() else 2
    return (
        f'<div class="slider-wrap">'
        f'<input type="range" name="scrolling_speed" min="0" max="6" step="1" value="{val}" '
        f'oninput="this.nextElementSibling.textContent=this.value">'
        f'<span class="slider-val">{val}</span>'
        f'</div>'
    )


HTML_PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MLB LED Scoreboard Config</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0f1117;color:#e2e8f0;min-height:100vh;padding:24px 16px}}
  .container{{max-width:800px;margin:0 auto}}
  header{{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid #2d3748}}
  header h1{{font-size:1.4rem;font-weight:700;color:#f7fafc}}
  header span{{font-size:0.8rem;color:#718096;margin-left:auto}}
  .alert{{padding:12px 16px;border-radius:8px;margin-bottom:20px;font-size:.9rem;font-weight:500}}
  .alert-success{{background:#1a3a2a;border:1px solid #276749;color:#68d391}}
  .alert-error{{background:#3b1a1a;border:1px solid #c53030;color:#fc8181}}
  .section{{background:#1a202c;border:1px solid #2d3748;border-radius:10px;margin-bottom:16px;overflow:hidden}}
  .section-header{{padding:14px 18px;background:#2d3748;font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#90cdf4}}
  .field-row{{display:grid;grid-template-columns:220px 1fr;border-bottom:1px solid #2d3748}}
  .field-row:last-child{{border-bottom:none}}
  .field-label{{padding:12px 18px;font-size:.85rem;color:#a0aec0;display:flex;align-items:flex-start;padding-top:14px;border-right:1px solid #2d3748;word-break:break-word}}
  .field-value{{padding:10px 14px;display:flex;align-items:center;flex-wrap:wrap;gap:6px}}
  input[type="text"],input[type="number"]{{width:100%;background:#2d3748;border:1px solid #4a5568;border-radius:6px;color:#e2e8f0;padding:7px 10px;font-size:.85rem;transition:border-color .15s;outline:none}}
  input:focus{{border-color:#63b3ed}}
  /* toggle */
  .toggle{{position:relative;width:44px;height:24px;flex-shrink:0}}
  .toggle input{{opacity:0;width:0;height:0}}
  .toggle-slider{{position:absolute;inset:0;background:#4a5568;border-radius:24px;cursor:pointer;transition:background .2s}}
  .toggle-slider:before{{content:"";position:absolute;width:18px;height:18px;left:3px;top:3px;background:white;border-radius:50%;transition:transform .2s}}
  .toggle input:checked+.toggle-slider{{background:#3182ce}}
  .toggle input:checked+.toggle-slider:before{{transform:translateX(20px)}}
  /* checkbox grid */
  .cb-grid{{display:flex;flex-wrap:wrap;gap:6px 10px;padding:10px 14px}}
  .cb-group-label{{width:100%;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#4a5568;margin-top:8px;padding-top:6px;border-top:1px solid #2d3748}}
  .cb-group-label:first-child{{margin-top:0;padding-top:0;border-top:none}}
  .cb-item{{display:flex;align-items:center;gap:5px;font-size:.85rem;color:#cbd5e0;cursor:pointer;white-space:nowrap}}
  .cb-item input[type="checkbox"]{{width:15px;height:15px;accent-color:#3182ce;cursor:pointer;flex-shrink:0}}
  /* radio */
  .radio-group{{display:flex;gap:18px;padding:10px 14px;align-items:center}}
  .radio-item{{display:flex;align-items:center;gap:6px;font-size:.9rem;color:#cbd5e0;cursor:pointer}}
  .radio-item input[type="radio"]{{width:16px;height:16px;accent-color:#3182ce;cursor:pointer}}
  /* slider */
  .slider-wrap{{display:flex;align-items:center;gap:10px;width:100%}}
  input[type="range"]{{flex:1;accent-color:#3182ce;height:4px}}
  .slider-val{{min-width:20px;text-align:center;font-size:.9rem;font-weight:600;color:#90cdf4}}
  /* buttons */
  .actions{{display:flex;gap:12px;margin-top:24px;flex-wrap:wrap}}
  button{{padding:11px 24px;border:none;border-radius:8px;font-size:.9rem;font-weight:600;cursor:pointer;transition:opacity .15s,transform .1s}}
  button:active{{transform:scale(.98)}}
  .btn-primary{{background:#3182ce;color:white}}
  .btn-primary:hover{{opacity:.85}}
  .btn-restart{{background:#276749;color:white}}
  .btn-restart:hover{{opacity:.85}}
  .note{{font-size:.78rem;color:#718096;margin-top:12px}}
  @media(max-width:540px){{
    .field-row{{grid-template-columns:1fr}}
    .field-label{{border-right:none;border-bottom:1px solid #2d3748;padding-bottom:6px}}
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

    <!-- ── Preferred Teams & Divisions ───────────────────────── -->
    <div class="section">
      <div class="section-header">Preferred Teams &amp; Divisions</div>
      <div class="field-row" style="grid-template-columns:1fr">
        <div class="field-label" style="border-right:none;border-bottom:1px solid #2d3748;padding-bottom:10px">
          Teams &mdash; <span style="font-size:.75rem;color:#718096">First team is your &ldquo;favorite&rdquo; shown by default</span>
        </div>
        <div class="cb-grid">
          {team_checkboxes}
        </div>
      </div>
      <div class="field-row" style="grid-template-columns:1fr">
        <div class="field-label" style="border-right:none;border-bottom:1px solid #2d3748;padding-bottom:10px">
          Divisions &mdash; <span style="font-size:.75rem;color:#718096">Shown in standings rotation</span>
        </div>
        <div class="cb-grid" style="gap:8px 16px">
          {division_checkboxes}
        </div>
      </div>
    </div>

    <!-- ── News Ticker ────────────────────────────────────────── -->
    <div class="section">
      <div class="section-header">News Ticker</div>
      <div class="field-row">
        <div class="field-label">Show on team off-day</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="news_ticker__team_offday" {news_ticker__team_offday}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Always display</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="news_ticker__always_display" {news_ticker__always_display}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Show preferred teams news</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="news_ticker__preferred_teams" {news_ticker__preferred_teams}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Show when no games live</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="news_ticker__display_no_games_live" {news_ticker__display_no_games_live}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Trade rumors</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="news_ticker__traderumors" {news_ticker__traderumors}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">MLB news</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="news_ticker__mlb_news" {news_ticker__mlb_news}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Countdowns</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="news_ticker__countdowns" {news_ticker__countdowns}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Show date</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="news_ticker__date" {news_ticker__date}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Date format</div>
        <div class="field-value">
          <input type="text" name="news_ticker__date_format" value="{news_ticker__date_format}" placeholder="%A, %B %-d">
        </div>
      </div>
    </div>

    <!-- ── Standings ──────────────────────────────────────────── -->
    <div class="section">
      <div class="section-header">Standings</div>
      <div class="field-row">
        <div class="field-label">Show on team off-day</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="standings__team_offday" {standings__team_offday}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Show on MLB off-day</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="standings__mlb_offday" {standings__mlb_offday}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Always display</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="standings__always_display" {standings__always_display}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Show when no games live</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="standings__display_no_games_live" {standings__display_no_games_live}><span class="toggle-slider"></span></label>
        </div>
      </div>
    </div>

    <!-- ── Rotation ───────────────────────────────────────────── -->
    <div class="section">
      <div class="section-header">Rotation</div>
      <div class="field-row">
        <div class="field-label">Enabled</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="rotation__enabled" {rotation__enabled}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Scroll until finished</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="rotation__scroll_until_finished" {rotation__scroll_until_finished}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Only preferred teams</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="rotation__only_preferred" {rotation__only_preferred}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Only live games</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="rotation__only_live" {rotation__only_live}><span class="toggle-slider"></span></label>
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
          <label class="toggle"><input type="checkbox" name="rotation__while_preferred_team_live__enabled" {rotation__while_preferred_team_live__enabled}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Preferred team live: inning breaks</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="rotation__while_preferred_team_live__during_inning_breaks" {rotation__while_preferred_team_live__during_inning_breaks}><span class="toggle-slider"></span></label>
        </div>
      </div>
    </div>

    <!-- ── Weather ────────────────────────────────────────────── -->
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
          <label class="toggle"><input type="checkbox" name="weather__metric_units" {weather__metric_units}><span class="toggle-slider"></span></label>
        </div>
      </div>
    </div>

    <!-- ── General ────────────────────────────────────────────── -->
    <div class="section">
      <div class="section-header">General</div>
      <div class="field-row">
        <div class="field-label">Time format</div>
        <div class="radio-group">
          {time_format_radios}
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">End of day (HH:MM)</div>
        <div class="field-value">
          <input type="text" name="end_of_day" value="{end_of_day}" placeholder="00:00" style="max-width:120px">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Full team names</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="full_team_names" {full_team_names}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Short names for runs/hits</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="short_team_names_for_runs_hits" {short_team_names_for_runs_hits}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Pregame weather</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="pregame_weather" {pregame_weather}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Scrolling speed (0–6)</div>
        <div class="field-value" style="padding:10px 14px">
          {scrolling_speed_slider}
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Preferred game delay multiplier</div>
        <div class="field-value">
          <input type="number" name="preferred_game_delay_multiplier" value="{preferred_game_delay_multiplier}" min="0" step="1" style="max-width:120px">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">API refresh rate (seconds)</div>
        <div class="field-value">
          <input type="number" name="api_refresh_rate" value="{api_refresh_rate}" min="3" step="1" style="max-width:120px">
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Debug mode</div>
        <div class="field-value">
          <label class="toggle"><input type="checkbox" name="debug" {debug}><span class="toggle-slider"></span></label>
        </div>
      </div>
      <div class="field-row">
        <div class="field-label">Demo date</div>
        <div class="field-value">
          <input type="text" name="demo_date" value="{demo_date}" placeholder="false or 2024-04-01" style="max-width:180px">
        </div>
      </div>
    </div>

    <div class="actions">
      <button type="submit" name="action" value="save" class="btn-primary">Save</button>
      <button type="submit" name="action" value="save_restart" class="btn-restart">Save &amp; Restart Service</button>
    </div>
    <p class="note">Config saved to <code>config.json</code>. Restart applies to the <code>{service_name}</code> systemd service.</p>
  </form>
</div>
</body>
</html>"""


def load_config():
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


def config_to_template_vars(config):
    def checked(val):
        return "checked" if val else ""

    c = config
    teams = c["preferred"]["teams"]
    if isinstance(teams, str):
        teams = [teams]

    divs = c["preferred"]["divisions"]
    if isinstance(divs, str):
        divs = [divs]

    return {
        "team_checkboxes": build_team_checkboxes(teams),
        "division_checkboxes": build_division_checkboxes(divs),
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
        "time_format_radios": build_time_format_radios(c["time_format"]),
        "end_of_day": c["end_of_day"],
        "full_team_names": checked(c["full_team_names"]),
        "short_team_names_for_runs_hits": checked(c["short_team_names_for_runs_hits"]),
        "pregame_weather": checked(c["pregame_weather"]),
        "scrolling_speed_slider": build_scrolling_speed_slider(c["scrolling_speed"]),
        "preferred_game_delay_multiplier": c["preferred_game_delay_multiplier"],
        "api_refresh_rate": c["api_refresh_rate"],
        "debug": checked(c["debug"]),
        "demo_date": str(c["demo_date"]) if c["demo_date"] else "false",
        "service_name": SERVICE_NAME,
        "alert_html": "",
    }


def form_data_to_config(fields):
    def get(key, default=""):
        vals = fields.get(key, [default])
        return vals[0] if vals else default

    def get_list(key):
        return fields.get(key, [])

    def checkbox(key):
        return key in fields

    demo_raw = get("demo_date", "false").strip()
    demo_val = False if demo_raw.lower() in ("false", "") else demo_raw

    return {
        "preferred": {
            "teams": get_list("preferred__teams"),
            "divisions": get_list("preferred__divisions"),
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
        "scrolling_speed": int(get("scrolling_speed", "2")),
        "debug": checkbox("debug"),
        "demo_date": demo_val,
    }


def run_validator():
    """Run validate_config.py as a subprocess and return (success, output_text)."""
    validator = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_config.py")
    if not os.path.isfile(validator):
        return False, "validate_config.py not found."
    try:
        result = subprocess.run(
            [sys.executable, validator],
            capture_output=True, text=True, timeout=30,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Validator timed out."
    except Exception as e:
        return False, f"Error running validator: {e}"


def restart_service():
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "restart", SERVICE_NAME],
            capture_output=True, text=True, timeout=15,
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
    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}")

    def send_html(self, html, status=200):
        encoded = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def render(self, config, alert_html=""):
        tvars = config_to_template_vars(config)
        tvars["alert_html"] = alert_html
        return HTML_PAGE.format(**tvars)

    def do_GET(self):
        if urlparse(self.path).path not in ("/", "/index.html"):
            self.send_response(404)
            self.end_headers()
            return
        try:
            self.send_html(self.render(load_config()))
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

        alert = ""
        try:
            new_config = form_data_to_config(fields)
            with open(CONFIG_FILE, "w") as f:
                json.dump(new_config, f, indent="\t")

            # Always run the validator after saving
            val_ok, val_output = run_validator()
            val_detail = ""
            if val_output:
                escaped = val_output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                val_detail = f'<pre style="margin-top:8px;font-size:.75rem;color:#a0aec0;white-space:pre-wrap">{escaped}</pre>'

            if action == "save_restart":
                ok, msg = restart_service()
                status_cls = "alert-success" if ok else "alert-error"
                alert = f'<div class="alert {status_cls}">Saved. {msg}{val_detail}</div>'
            else:
                val_cls = "alert-success" if val_ok else "alert-error"
                alert = f'<div class="alert {val_cls}">Config saved.{val_detail}</div>'

        except Exception as e:
            alert = f'<div class="alert alert-error">Error saving config: {e}</div>'

        try:
            html = self.render(load_config(), alert)
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
