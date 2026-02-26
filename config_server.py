#!/usr/bin/env python3
"""
MLB LED Scoreboard - Web Config Server
Serves a local web page to view/edit config.json, colors, and HomeKit status.
Usage: python3 config_server.py [--port 8080]
"""

import argparse
import base64
import io
import json
import os
import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.resolve()
CONFIG_FILE         = ROOT / "config.json"
EXAMPLE_CONFIG_FILE = ROOT / "config.example.json"
SCOREBOARD_COLORS_FILE         = ROOT / "colors" / "scoreboard.json"
SCOREBOARD_COLORS_EXAMPLE_FILE = ROOT / "colors" / "scoreboard.example.json"
TEAMS_COLORS_FILE         = ROOT / "colors" / "teams.json"
TEAMS_COLORS_EXAMPLE_FILE = ROOT / "colors" / "teams.example.json"
HOMEKIT_PERSIST_FILE = Path.home() / ".homekit-scoreboard" / "accessory.state"

SERVICE_NAME = "mlb-scoreboard"

# Pin and category as defined in homekit_bridge.py
HOMEKIT_PINCODE  = "123-45-678"
HOMEKIT_CATEGORY = 5  # CATEGORY_LIGHTBULB

# ── MLB data ───────────────────────────────────────────────────────────────────
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

# ── Helpers ────────────────────────────────────────────────────────────────────

def deep_update(base, overrides):
    result = dict(base)
    for k, v in overrides.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_update(result[k], v)
        else:
            result[k] = v
    return result


def load_json_with_example(custom_path, example_path):
    """Load example as base, merge custom on top."""
    data = {}
    if example_path.is_file():
        data = json.loads(example_path.read_text())
    if custom_path.is_file():
        data = deep_update(data, json.loads(custom_path.read_text()))
    return data


def load_config():
    return load_json_with_example(CONFIG_FILE, EXAMPLE_CONFIG_FILE)


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))


def hex_to_rgb(h):
    h = h.lstrip("#")
    return {"r": int(h[0:2], 16), "g": int(h[2:4], 16), "b": int(h[4:6], 16)}


def flatten_colors(d, prefix=""):
    """Walk a color dict; yield (dotted_key, hex_string) for every {r,g,b} leaf."""
    if set(d.keys()) <= {"r", "g", "b"} and len(d) >= 3:
        yield prefix, rgb_to_hex(d["r"], d["g"], d["b"])
        return
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            yield from flatten_colors(v, full_key)


def unflatten_colors(flat):
    """Reconstruct nested color dict from {dotted_key: hex} flat dict."""
    result = {}
    for dotted_key, hex_val in flat.items():
        parts = dotted_key.split(".")
        node = result
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = hex_to_rgb(hex_val)
    return result


# ── HomeKit helpers ────────────────────────────────────────────────────────────

def homekit_state():
    """Return dict with pairing info. Keys: paired (bool), client_count (int), clients (list)."""
    if not HOMEKIT_PERSIST_FILE.is_file():
        return {"paired": False, "client_count": 0, "clients": []}
    try:
        data = json.loads(HOMEKIT_PERSIST_FILE.read_text())
        paired_clients = data.get("paired_clients", {})
        count = len(paired_clients)
        return {"paired": count > 0, "client_count": count, "clients": list(paired_clients.keys())}
    except Exception:
        return {"paired": False, "client_count": 0, "clients": []}


def homekit_qr_data_uri():
    """
    Build the X-HM:// pairing URI and return a PNG data URI, or None if qrcode unavailable.
    URI format per HAP spec:
      X-HM://00{9 uppercase hex digits}
      payload = (category << 31) | (2 << 27) | setup_code_int
      flag 2 = IP support
    """
    try:
        import qrcode
        digits = HOMEKIT_PINCODE.replace("-", "")
        code_int = int(digits)
        payload = (HOMEKIT_CATEGORY << 31) | (2 << 27) | code_int
        uri = f"X-HM://00{payload:09X}"
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{b64}", uri
    except ImportError:
        return None, None


# ── HTML builders ──────────────────────────────────────────────────────────────

def build_team_checkboxes(selected_teams):
    sel = set(selected_teams)
    parts = []
    for div_name, teams in MLB_TEAMS_BY_DIVISION.items():
        parts.append(f'<div class="cb-group-label">{div_name}</div>')
        for team in teams:
            chk = "checked" if team in sel else ""
            parts.append(
                f'<label class="cb-item">'
                f'<input type="checkbox" name="preferred__teams" value="{team}" {chk}>'
                f'<span>{team}</span></label>'
            )
    return "\n".join(parts)


def build_division_checkboxes(selected_divs):
    sel = set(selected_divs)
    parts = []
    for div in DIVISIONS:
        chk = "checked" if div in sel else ""
        parts.append(
            f'<label class="cb-item">'
            f'<input type="checkbox" name="preferred__divisions" value="{div}" {chk}>'
            f'<span>{div}</span></label>'
        )
    return "\n".join(parts)


def build_time_format_radios(current):
    r12 = "checked" if current in ("12h", "%-I:%M") else ""
    r24 = "checked" if current in ("24h", "%H:%M") else ""
    return (
        f'<label class="radio-item"><input type="radio" name="time_format" value="12h" {r12}> 12h</label>'
        f'<label class="radio-item"><input type="radio" name="time_format" value="24h" {r24}> 24h</label>'
    )


def build_scrolling_speed_slider(current):
    val = int(current) if str(current).isdigit() else 2
    return (
        f'<div class="slider-wrap">'
        f'<input type="range" name="scrolling_speed" min="0" max="6" step="1" value="{val}" '
        f'oninput="this.nextElementSibling.textContent=this.value">'
        f'<span class="slider-val">{val}</span></div>'
    )


def build_color_pickers(colors_dict, form_prefix):
    """Build color picker rows for every leaf in the color dict."""
    parts = []
    for dotted_key, hex_val in sorted(flatten_colors(colors_dict)):
        label = dotted_key.replace(".", " › ")
        field_name = f"{form_prefix}::{dotted_key}"
        parts.append(
            f'<div class="color-row">'
            f'<label class="color-label" title="{dotted_key}">{label}</label>'
            f'<div class="color-controls">'
            f'<input type="color" name="{field_name}" value="{hex_val}" '
            f'oninput="this.nextElementSibling.textContent=this.value.toUpperCase()">'
            f'<span class="color-hex">{hex_val.upper()}</span>'
            f'</div></div>'
        )
    return "\n".join(parts)


def build_homekit_section():
    state = homekit_state()
    if state["paired"]:
        n = state["client_count"]
        noun = "controller" if n == 1 else "controllers"
        return f"""
<div class="section">
  <div class="section-header">HomeKit Status</div>
  <div class="hk-status hk-paired">
    <div class="hk-status-icon">&#10003;</div>
    <div>
      <div class="hk-status-title">Paired</div>
      <div class="hk-status-sub">Linked to {n} HomeKit {noun}</div>
    </div>
  </div>
  <div class="hk-body">
    <p style="font-size:.85rem;color:#a0aec0;margin-bottom:14px">
      To re-pair this accessory, remove the current pairing first. This deletes the
      accessory state file and restarts the service so it becomes discoverable again.
    </p>
    <form method="POST" action="/homekit/unpair">
      <button type="submit" class="btn-danger"
        onclick="return confirm('Remove pairing and restart service?')">
        Remove Pairing &amp; Restart
      </button>
    </form>
  </div>
</div>"""
    else:
        qr_uri, xhm_uri = homekit_qr_data_uri()
        qr_block = ""
        if qr_uri:
            qr_block = f"""
    <div class="hk-qr-wrap">
      <img src="{qr_uri}" alt="HomeKit QR code" class="hk-qr">
      <div class="hk-qr-caption">Scan with the iPhone <strong>Home</strong> app<br>
        <span style="font-size:.72rem;color:#718096">{xhm_uri}</span></div>
    </div>"""
        else:
            qr_block = '<p style="color:#718096;font-size:.85rem">Install the <code>qrcode[pil]</code> package to show a QR code.</p>'
        return f"""
<div class="section">
  <div class="section-header">HomeKit Status</div>
  <div class="hk-status hk-unpaired">
    <div class="hk-status-icon">&#9679;</div>
    <div>
      <div class="hk-status-title">Not Paired</div>
      <div class="hk-status-sub">Open the Home app and add an accessory</div>
    </div>
  </div>
  <div class="hk-body">
    {qr_block}
    <div class="hk-pin-wrap">
      <span class="hk-pin-label">Setup Code</span>
      <span class="hk-pin">{HOMEKIT_PINCODE}</span>
    </div>
  </div>
</div>"""


# ── CSS / JS shared shell ──────────────────────────────────────────────────────

SHELL_CSS = """\
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0f1117;color:#e2e8f0;min-height:100vh;padding:24px 16px}
.container{max-width:820px;margin:0 auto}
header{display:flex;align-items:center;gap:12px;margin-bottom:24px;padding-bottom:20px;border-bottom:1px solid #2d3748}
header h1{font-size:1.4rem;font-weight:700;color:#f7fafc}
/* tabs */
.tabs{display:flex;gap:4px;margin-bottom:20px;border-bottom:1px solid #2d3748;padding-bottom:0}
.tab{padding:9px 20px;font-size:.875rem;font-weight:600;color:#718096;cursor:pointer;border-radius:8px 8px 0 0;border:1px solid transparent;border-bottom:none;margin-bottom:-1px;transition:color .15s,background .15s}
.tab:hover{color:#e2e8f0}
.tab.active{color:#90cdf4;background:#1a202c;border-color:#2d3748;border-bottom-color:#1a202c}
.tab-panel{display:none}.tab-panel.active{display:block}
/* alert */
.alert{padding:12px 16px;border-radius:8px;margin-bottom:20px;font-size:.9rem;font-weight:500}
.alert-success{background:#1a3a2a;border:1px solid #276749;color:#68d391}
.alert-error{background:#3b1a1a;border:1px solid #c53030;color:#fc8181}
/* section card */
.section{background:#1a202c;border:1px solid #2d3748;border-radius:10px;margin-bottom:16px;overflow:hidden}
.section-header{padding:14px 18px;background:#2d3748;font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#90cdf4}
/* field rows */
.field-row{display:grid;grid-template-columns:220px 1fr;border-bottom:1px solid #2d3748}
.field-row:last-child{border-bottom:none}
.field-label{padding:12px 18px;font-size:.85rem;color:#a0aec0;display:flex;align-items:flex-start;padding-top:14px;border-right:1px solid #2d3748;word-break:break-word}
.field-value{padding:10px 14px;display:flex;align-items:center;flex-wrap:wrap;gap:6px}
input[type="text"],input[type="number"]{width:100%;background:#2d3748;border:1px solid #4a5568;border-radius:6px;color:#e2e8f0;padding:7px 10px;font-size:.85rem;transition:border-color .15s;outline:none}
input:focus{border-color:#63b3ed}
/* toggle */
.toggle{position:relative;width:44px;height:24px;flex-shrink:0}
.toggle input{opacity:0;width:0;height:0}
.toggle-slider{position:absolute;inset:0;background:#4a5568;border-radius:24px;cursor:pointer;transition:background .2s}
.toggle-slider:before{content:"";position:absolute;width:18px;height:18px;left:3px;top:3px;background:white;border-radius:50%;transition:transform .2s}
.toggle input:checked+.toggle-slider{background:#3182ce}
.toggle input:checked+.toggle-slider:before{transform:translateX(20px)}
/* checkbox grid */
.cb-grid{display:flex;flex-wrap:wrap;gap:6px 10px;padding:10px 14px}
.cb-group-label{width:100%;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#4a5568;margin-top:8px;padding-top:6px;border-top:1px solid #2d3748}
.cb-group-label:first-child{margin-top:0;padding-top:0;border-top:none}
.cb-item{display:flex;align-items:center;gap:5px;font-size:.85rem;color:#cbd5e0;cursor:pointer;white-space:nowrap}
.cb-item input[type="checkbox"]{width:15px;height:15px;accent-color:#3182ce;cursor:pointer;flex-shrink:0}
/* radio */
.radio-group{display:flex;gap:18px;padding:10px 14px;align-items:center}
.radio-item{display:flex;align-items:center;gap:6px;font-size:.9rem;color:#cbd5e0;cursor:pointer}
.radio-item input[type="radio"]{width:16px;height:16px;accent-color:#3182ce;cursor:pointer}
/* slider */
.slider-wrap{display:flex;align-items:center;gap:10px;width:100%}
input[type="range"]{flex:1;accent-color:#3182ce;height:4px}
.slider-val{min-width:20px;text-align:center;font-size:.9rem;font-weight:600;color:#90cdf4}
/* color rows */
.color-section-title{font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#90cdf4;padding:12px 16px 6px;border-bottom:1px solid #2d3748}
.color-row{display:grid;grid-template-columns:1fr auto;align-items:center;padding:7px 16px;border-bottom:1px solid #1a202c;gap:10px}
.color-row:last-child{border-bottom:none}
.color-label{font-size:.82rem;color:#a0aec0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.color-controls{display:flex;align-items:center;gap:8px;flex-shrink:0}
input[type="color"]{width:36px;height:28px;padding:2px;border:1px solid #4a5568;border-radius:5px;background:#2d3748;cursor:pointer}
.color-hex{font-size:.75rem;font-family:monospace;color:#718096;min-width:54px}
/* buttons */
.actions{display:flex;gap:12px;margin-top:24px;flex-wrap:wrap;align-items:center}
button{padding:10px 22px;border:none;border-radius:8px;font-size:.875rem;font-weight:600;cursor:pointer;transition:opacity .15s,transform .1s}
button:active{transform:scale(.98)}
.btn-primary{background:#3182ce;color:white}.btn-primary:hover{opacity:.85}
.btn-restart{background:#276749;color:white}.btn-restart:hover{opacity:.85}
.btn-danger{background:#c53030;color:white}.btn-danger:hover{opacity:.85}
.note{font-size:.78rem;color:#718096;margin-top:10px}
/* HomeKit */
.hk-status{display:flex;align-items:center;gap:14px;padding:16px 18px;border-bottom:1px solid #2d3748}
.hk-status-icon{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0}
.hk-paired .hk-status-icon{background:#1a3a2a;color:#68d391}
.hk-unpaired .hk-status-icon{background:#2d3748;color:#718096;font-size:.6rem}
.hk-status-title{font-weight:700;font-size:.95rem}
.hk-paired .hk-status-title{color:#68d391}
.hk-unpaired .hk-status-title{color:#a0aec0}
.hk-status-sub{font-size:.8rem;color:#718096;margin-top:2px}
.hk-body{padding:18px}
.hk-qr-wrap{display:flex;align-items:center;gap:20px;margin-bottom:18px;flex-wrap:wrap}
.hk-qr{width:160px;height:160px;border-radius:8px;border:3px solid #2d3748;image-rendering:pixelated}
.hk-qr-caption{font-size:.85rem;color:#a0aec0;line-height:1.5}
.hk-pin-wrap{display:flex;align-items:center;gap:12px;margin-top:6px}
.hk-pin-label{font-size:.8rem;color:#718096;text-transform:uppercase;letter-spacing:.06em}
.hk-pin{font-family:monospace;font-size:1.5rem;font-weight:700;color:#f7fafc;letter-spacing:.1em;background:#2d3748;padding:6px 14px;border-radius:8px;border:1px solid #4a5568}
@media(max-width:540px){
  .field-row{grid-template-columns:1fr}
  .field-label{border-right:none;border-bottom:1px solid #2d3748;padding-bottom:6px}
  .hk-qr-wrap{flex-direction:column;align-items:flex-start}
}"""

SHELL_JS = """\
function showTab(id) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === id));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.toggle('active', p.id === id));
  history.replaceState(null,'','?tab='+id);
}
const initTab = new URLSearchParams(location.search).get('tab') || 'config';
showTab(initTab);"""


def build_page(config, alert_html="", active_tab="config"):
    scoreboard_colors = load_json_with_example(SCOREBOARD_COLORS_FILE, SCOREBOARD_COLORS_EXAMPLE_FILE)
    teams_colors      = load_json_with_example(TEAMS_COLORS_FILE, TEAMS_COLORS_EXAMPLE_FILE)

    c = config
    teams = c["preferred"]["teams"]
    if isinstance(teams, str):
        teams = [teams]
    divs = c["preferred"]["divisions"]
    if isinstance(divs, str):
        divs = [divs]

    def ck(val):
        return "checked" if val else ""

    scrolling_raw = c["scrolling_speed"]
    scrolling_int = int(scrolling_raw) if str(scrolling_raw).isdigit() else 2

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MLB LED Scoreboard</title>
<style>{SHELL_CSS}</style>
</head>
<body>
<div class="container">
  <header><h1>MLB LED Scoreboard</h1></header>

  {alert_html}

  <div class="tabs">
    <div class="tab" data-tab="config"   onclick="showTab('config')">Config</div>
    <div class="tab" data-tab="colors"   onclick="showTab('colors')">Colors</div>
    <div class="tab" data-tab="homekit"  onclick="showTab('homekit')">HomeKit</div>
  </div>

  <!-- ═══════════════════ CONFIG TAB ═══════════════════ -->
  <div class="tab-panel" id="config">
  <form method="POST" action="/save?tab=config">

    <div class="section">
      <div class="section-header">Preferred Teams &amp; Divisions</div>
      <div class="field-row" style="grid-template-columns:1fr">
        <div class="field-label" style="border-right:none;border-bottom:1px solid #2d3748;padding-bottom:10px">
          Teams &mdash; <span style="font-size:.75rem;color:#718096">First team is your &ldquo;favorite&rdquo;</span>
        </div>
        <div class="cb-grid">{build_team_checkboxes(teams)}</div>
      </div>
      <div class="field-row" style="grid-template-columns:1fr">
        <div class="field-label" style="border-right:none;border-bottom:1px solid #2d3748;padding-bottom:10px">
          Divisions &mdash; <span style="font-size:.75rem;color:#718096">Shown in standings rotation</span>
        </div>
        <div class="cb-grid" style="gap:8px 16px">{build_division_checkboxes(divs)}</div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">News Ticker</div>
      <div class="field-row"><div class="field-label">Show on team off-day</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__team_offday" {ck(c["news_ticker"]["team_offday"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Always display</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__always_display" {ck(c["news_ticker"]["always_display"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Show preferred teams news</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__preferred_teams" {ck(c["news_ticker"]["preferred_teams"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Show when no games live</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__display_no_games_live" {ck(c["news_ticker"]["display_no_games_live"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Trade rumors</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__traderumors" {ck(c["news_ticker"]["traderumors"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">MLB news</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__mlb_news" {ck(c["news_ticker"]["mlb_news"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Countdowns</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__countdowns" {ck(c["news_ticker"]["countdowns"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Show date</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__date" {ck(c["news_ticker"]["date"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Date format</div><div class="field-value"><input type="text" name="news_ticker__date_format" value="{c["news_ticker"]["date_format"]}" placeholder="%A, %B %-d"></div></div>
    </div>

    <div class="section">
      <div class="section-header">Standings</div>
      <div class="field-row"><div class="field-label">Show on team off-day</div><div class="field-value"><label class="toggle"><input type="checkbox" name="standings__team_offday" {ck(c["standings"]["team_offday"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Show on MLB off-day</div><div class="field-value"><label class="toggle"><input type="checkbox" name="standings__mlb_offday" {ck(c["standings"]["mlb_offday"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Always display</div><div class="field-value"><label class="toggle"><input type="checkbox" name="standings__always_display" {ck(c["standings"]["always_display"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Show when no games live</div><div class="field-value"><label class="toggle"><input type="checkbox" name="standings__display_no_games_live" {ck(c["standings"]["display_no_games_live"])}><span class="toggle-slider"></span></label></div></div>
    </div>

    <div class="section">
      <div class="section-header">Rotation</div>
      <div class="field-row"><div class="field-label">Enabled</div><div class="field-value"><label class="toggle"><input type="checkbox" name="rotation__enabled" {ck(c["rotation"]["enabled"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Scroll until finished</div><div class="field-value"><label class="toggle"><input type="checkbox" name="rotation__scroll_until_finished" {ck(c["rotation"]["scroll_until_finished"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Only preferred teams</div><div class="field-value"><label class="toggle"><input type="checkbox" name="rotation__only_preferred" {ck(c["rotation"]["only_preferred"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Only live games</div><div class="field-value"><label class="toggle"><input type="checkbox" name="rotation__only_live" {ck(c["rotation"]["only_live"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Rate: live (seconds)</div><div class="field-value"><input type="number" name="rotation__rates__live" value="{c["rotation"]["rates"]["live"]}" min="2" step="0.5"></div></div>
      <div class="field-row"><div class="field-label">Rate: final (seconds)</div><div class="field-value"><input type="number" name="rotation__rates__final" value="{c["rotation"]["rates"]["final"]}" min="2" step="0.5"></div></div>
      <div class="field-row"><div class="field-label">Rate: pregame (seconds)</div><div class="field-value"><input type="number" name="rotation__rates__pregame" value="{c["rotation"]["rates"]["pregame"]}" min="2" step="0.5"></div></div>
      <div class="field-row"><div class="field-label">Preferred team live: enabled</div><div class="field-value"><label class="toggle"><input type="checkbox" name="rotation__while_preferred_team_live__enabled" {ck(c["rotation"]["while_preferred_team_live"]["enabled"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Preferred team live: inning breaks</div><div class="field-value"><label class="toggle"><input type="checkbox" name="rotation__while_preferred_team_live__during_inning_breaks" {ck(c["rotation"]["while_preferred_team_live"]["during_inning_breaks"])}><span class="toggle-slider"></span></label></div></div>
    </div>

    <div class="section">
      <div class="section-header">Weather</div>
      <div class="field-row"><div class="field-label">API Key</div><div class="field-value"><input type="text" name="weather__apikey" value="{c["weather"]["apikey"]}" placeholder="OpenWeatherMap API key"></div></div>
      <div class="field-row"><div class="field-label">Location</div><div class="field-value"><input type="text" name="weather__location" value="{c["weather"]["location"]}" placeholder="e.g. Chicago,il,us"></div></div>
      <div class="field-row"><div class="field-label">Metric units</div><div class="field-value"><label class="toggle"><input type="checkbox" name="weather__metric_units" {ck(c["weather"]["metric_units"])}><span class="toggle-slider"></span></label></div></div>
    </div>

    <div class="section">
      <div class="section-header">General</div>
      <div class="field-row"><div class="field-label">Time format</div><div class="radio-group">{build_time_format_radios(c["time_format"])}</div></div>
      <div class="field-row"><div class="field-label">End of day (HH:MM)</div><div class="field-value"><input type="text" name="end_of_day" value="{c["end_of_day"]}" placeholder="00:00" style="max-width:120px"></div></div>
      <div class="field-row"><div class="field-label">Full team names</div><div class="field-value"><label class="toggle"><input type="checkbox" name="full_team_names" {ck(c["full_team_names"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Short names for runs/hits</div><div class="field-value"><label class="toggle"><input type="checkbox" name="short_team_names_for_runs_hits" {ck(c["short_team_names_for_runs_hits"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Pregame weather</div><div class="field-value"><label class="toggle"><input type="checkbox" name="pregame_weather" {ck(c["pregame_weather"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Scrolling speed (0–6)</div><div class="field-value" style="padding:10px 14px">{build_scrolling_speed_slider(scrolling_int)}</div></div>
      <div class="field-row"><div class="field-label">Preferred game delay multiplier</div><div class="field-value"><input type="number" name="preferred_game_delay_multiplier" value="{c["preferred_game_delay_multiplier"]}" min="0" step="1" style="max-width:120px"></div></div>
      <div class="field-row"><div class="field-label">API refresh rate (seconds)</div><div class="field-value"><input type="number" name="api_refresh_rate" value="{c["api_refresh_rate"]}" min="3" step="1" style="max-width:120px"></div></div>
      <div class="field-row"><div class="field-label">Debug mode</div><div class="field-value"><label class="toggle"><input type="checkbox" name="debug" {ck(c["debug"])}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Demo date</div><div class="field-value"><input type="text" name="demo_date" value="{str(c["demo_date"]) if c["demo_date"] else "false"}" placeholder="false or 2024-04-01" style="max-width:180px"></div></div>
    </div>

    <div class="actions">
      <button type="submit" name="action" value="save" class="btn-primary">Save</button>
      <button type="submit" name="action" value="save_restart" class="btn-restart">Save &amp; Restart Service</button>
    </div>
    <p class="note">Saved to <code>config.json</code>. Restart applies to the <code>{SERVICE_NAME}</code> systemd service.</p>
  </form>
  </div>

  <!-- ═══════════════════ COLORS TAB ═══════════════════ -->
  <div class="tab-panel" id="colors">

    <form method="POST" action="/save-colors?tab=colors&file=scoreboard">
      <div class="section">
        <div class="section-header">Scoreboard Colors</div>
        <div class="color-section-body">
          {build_color_pickers(scoreboard_colors, "scoreboard")}
        </div>
      </div>
      <div class="actions">
        <button type="submit" name="action" value="save" class="btn-primary">Save Scoreboard Colors</button>
        <button type="submit" name="action" value="save_restart" class="btn-restart">Save &amp; Restart Service</button>
      </div>
      <p class="note">Saves to <code>colors/scoreboard.json</code>.</p>
    </form>

    <form method="POST" action="/save-colors?tab=colors&file=teams" style="margin-top:28px">
      <div class="section">
        <div class="section-header">Team Colors</div>
        <div class="color-section-body">
          {build_color_pickers(teams_colors, "teams")}
        </div>
      </div>
      <div class="actions">
        <button type="submit" name="action" value="save" class="btn-primary">Save Team Colors</button>
        <button type="submit" name="action" value="save_restart" class="btn-restart">Save &amp; Restart Service</button>
      </div>
      <p class="note">Saves to <code>colors/teams.json</code>. <code>city_connect</code> entries are included but ignored by the validator.</p>
    </form>

  </div>

  <!-- ═══════════════════ HOMEKIT TAB ═══════════════════ -->
  <div class="tab-panel" id="homekit">
    {build_homekit_section()}
  </div>

</div>
<script>{SHELL_JS}</script>
</body>
</html>"""


# ── Backend helpers ────────────────────────────────────────────────────────────

def run_validator():
    validator = ROOT / "validate_config.py"
    if not validator.is_file():
        return False, "validate_config.py not found."
    try:
        result = subprocess.run(
            [sys.executable, str(validator)],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT),
        )
        out = (result.stdout + result.stderr).strip()
        return result.returncode == 0, out
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


def make_alert(ok, msg, detail=""):
    cls = "alert-success" if ok else "alert-error"
    pre = f'<pre style="margin-top:8px;font-size:.75rem;color:#a0aec0;white-space:pre-wrap">{detail}</pre>' if detail else ""
    return f'<div class="alert {cls}">{msg}{pre}</div>'


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
                "live":    float(get("rotation__rates__live",    "15.0")),
                "final":   float(get("rotation__rates__final",   "15.0")),
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


def form_data_to_colors(fields, prefix):
    """Extract color fields (prefix::dotted.key = #rrggbb) and return nested dict."""
    flat = {}
    marker = f"{prefix}::"
    for key, vals in fields.items():
        if key.startswith(marker):
            dotted = key[len(marker):]
            flat[dotted] = vals[0] if vals else "#000000"
    return unflatten_colors(flat)


# ── HTTP handler ───────────────────────────────────────────────────────────────

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

    def redirect(self, location):
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        tab = parse_qs(parsed.query).get("tab", ["config"])[0]
        if path not in ("/", "/index.html"):
            self.send_response(404)
            self.end_headers()
            return
        try:
            self.send_html(build_page(load_config(), active_tab=tab))
        except Exception as e:
            self.send_html(f"<pre>Error: {e}</pre>", 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        tab = qs.get("tab", ["config"])[0]

        if path == "/save":
            self._handle_save_config(tab)
        elif path == "/save-colors":
            file_key = qs.get("file", ["scoreboard"])[0]
            self._handle_save_colors(tab, file_key)
        elif path == "/homekit/unpair":
            self._handle_homekit_unpair()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_save_config(self, tab):
        fields = self._read_body()
        action = fields.get("action", ["save"])[0]
        alert = ""
        try:
            new_config = form_data_to_config(fields)
            CONFIG_FILE.write_text(json.dumps(new_config, indent="\t"))

            val_ok, val_out = run_validator()
            detail = val_out.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;") if val_out else ""

            if action == "save_restart":
                ok, msg = restart_service()
                alert = make_alert(ok, f"Saved. {msg}", detail)
            else:
                alert = make_alert(val_ok, "Config saved.", detail)
        except Exception as e:
            alert = make_alert(False, f"Error saving config: {e}")

        try:
            self.send_html(build_page(load_config(), alert, active_tab=tab))
        except Exception as e:
            self.send_html(f"<pre>{alert}\nError reloading: {e}</pre>")

    def _handle_save_colors(self, tab, file_key):
        fields = self._read_body()
        action = fields.get("action", ["save"])[0]
        target = SCOREBOARD_COLORS_FILE if file_key == "scoreboard" else TEAMS_COLORS_FILE
        label  = "scoreboard" if file_key == "scoreboard" else "teams"
        alert = ""
        try:
            new_colors = form_data_to_colors(fields, label)
            target.write_text(json.dumps(new_colors, indent="  "))

            if action == "save_restart":
                ok, msg = restart_service()
                alert = make_alert(ok, f"Colors saved. {msg}")
            else:
                alert = make_alert(True, f"colors/{label}.json saved.")
        except Exception as e:
            alert = make_alert(False, f"Error saving colors: {e}")

        try:
            self.send_html(build_page(load_config(), alert, active_tab=tab))
        except Exception as e:
            self.send_html(f"<pre>{alert}\nError reloading: {e}</pre>")

    def _handle_homekit_unpair(self):
        alert = ""
        try:
            if HOMEKIT_PERSIST_FILE.is_file():
                # Back up then remove
                bak = HOMEKIT_PERSIST_FILE.with_suffix(".state.bak")
                shutil.copy2(HOMEKIT_PERSIST_FILE, bak)
                HOMEKIT_PERSIST_FILE.unlink()
            ok, msg = restart_service()
            alert = make_alert(ok, f"Pairing removed. {msg}" if ok else f"Pairing removed, but restart failed: {msg}")
        except Exception as e:
            alert = make_alert(False, f"Error removing pairing: {e}")

        try:
            self.send_html(build_page(load_config(), alert, active_tab="homekit"))
        except Exception as e:
            self.send_html(f"<pre>{alert}\nError reloading: {e}</pre>")


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MLB LED Scoreboard web config server")
    parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), ConfigHandler)
    print(f"Config server running at http://{args.host}:{args.port}")
    print(f"Config file:    {CONFIG_FILE}")
    print(f"Service name:   {SERVICE_NAME}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
