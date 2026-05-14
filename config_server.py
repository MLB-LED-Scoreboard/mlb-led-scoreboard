#!/usr/bin/env python3
"""
MLB LED Scoreboard - Web Config Server
Serves a local web page to view/edit config.json and colors.
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

SERVICE_NAME = "mlb-scoreboard"

# ── MLB data (matches schemas/config.schema.json $defs) ────────────────────────
MLB_TEAMS_BY_DIVISION = {
    "AL East":    ["Yankees", "Red Sox", "Blue Jays", "Rays", "Orioles"],
    "AL Central": ["White Sox", "Guardians", "Tigers", "Royals", "Twins"],
    "AL West":    ["Astros", "Angels", "Athletics", "Mariners", "Rangers"],
    "NL East":    ["Braves", "Marlins", "Mets", "Phillies", "Nationals"],
    "NL Central": ["Cubs", "Reds", "Brewers", "Pirates", "Cardinals"],
    "NL West":    ["D-backs", "Rockies", "Dodgers", "Padres", "Giants"],
}

DIVISIONS = [
    "AL East", "AL Central", "AL West",
    "NL East", "NL Central", "NL West",
    "AL Wild Card", "NL Wild Card",
]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

REQUIRED_STATUS_VALUES = ["live", "live_in_inning", "pregame", "game_over"]

BUILTIN_SCREEN_KINDS = ["game", "time", "secondary_game", "news", "standings"]

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

# ── HTML builders ──────────────────────────────────────────────────────────────

def build_team_checkboxes(selected_teams, form_name):
    sel = set(selected_teams)
    parts = []
    for div_name, teams in MLB_TEAMS_BY_DIVISION.items():
        parts.append(f'<div class="cb-group-label">{div_name}</div>')
        for team in teams:
            chk = "checked" if team in sel else ""
            parts.append(
                f'<label class="cb-item">'
                f'<input type="checkbox" name="{form_name}" value="{team}" {chk}>'
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
            f'<input type="checkbox" name="standings__divisions" value="{div}" {chk}>'
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

SHELL_JS = r"""
function showTab(id) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === id));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.toggle('active', p.id === id));
  history.replaceState(null, '', '?tab=' + id);
}
const initTab = new URLSearchParams(location.search).get('tab') || 'config';
showTab(initTab);

function toggleDemoDate(enabled) {
  const picker = document.getElementById('demo_date_picker');
  const dateInput = picker.querySelector('input[type="date"]');
  picker.style.display = enabled ? 'block' : 'none';
  dateInput.disabled = !enabled;
  if (enabled && !dateInput.value) {
    dateInput.value = new Date().toISOString().slice(0, 10);
  }
}

// ── Screens editor (rotation.screens) ────────────────────────────────────────
const SCREENS = window.SCREENS || [];
const BUILTIN_KINDS = window.BUILTIN_KINDS || [];
const TEAMS_BY_DIV = window.TEAMS_BY_DIV || {};
const WEEKDAYS_LIST = window.WEEKDAYS_LIST || [];
const REQUIRED_STATUS = window.REQUIRED_STATUS || [];

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function classifyKind(kind) {
  return BUILTIN_KINDS.includes(kind) ? kind : 'plugin';
}

function priorityString(p) {
  if (Array.isArray(p)) return p.join(',');
  if (p === undefined || p === null) return '';
  return String(p);
}

function parsePriorityField(s) {
  s = String(s);
  if (s.includes(',')) {
    return s.split(',').map(x => Number(x.trim())).filter(x => !Number.isNaN(x));
  }
  const n = Number(s.trim());
  return Number.isNaN(n) ? 0 : n;
}

function renderTeamCheckboxes(idx, teams) {
  const sel = new Set(teams || []);
  const parts = [];
  for (const div of Object.keys(TEAMS_BY_DIV)) {
    parts.push('<div class="cb-group-label">' + esc(div) + '</div>');
    for (const t of TEAMS_BY_DIV[div]) {
      const chk = sel.has(t) ? 'checked' : '';
      parts.push('<label class="cb-item"><input type="checkbox" ' + chk +
        ' onchange="toggleScreenTeam(' + idx + ', \'' + esc(t) + '\', this.checked)">' +
        '<span>' + esc(t) + '</span></label>');
    }
  }
  return parts.join('');
}

function renderWeekdayCheckboxes(idx, days) {
  const sel = new Set(days || []);
  return WEEKDAYS_LIST.map(d => {
    const chk = sel.has(d) ? 'checked' : '';
    return '<label class="cb-item"><input type="checkbox" ' + chk +
      ' onchange="toggleScreenWeekday(' + idx + ', \'' + d + '\', this.checked)">' +
      '<span>' + d + '</span></label>';
  }).join('');
}

function renderRequiredStatusSelect(idx, current) {
  const cur = current || '';
  const opts = ['<option value="">(any)</option>'].concat(
    REQUIRED_STATUS.map(s => '<option value="' + s + '"' + (cur === s ? ' selected' : '') + '>' + s + '</option>')
  ).join('');
  return '<select onchange="setScreenField(' + idx + ', \'required_status\', this.value || undefined)" ' +
    'style="background:#2d3748;border:1px solid #4a5568;border-radius:6px;color:#e2e8f0;padding:6px 10px;font-size:.85rem">' +
    opts + '</select>';
}

function screenFields(idx, s) {
  const k = classifyKind(s.kind);
  const num = (v, fallback) => (v === undefined || v === null ? fallback : v);
  if (k === 'game') {
    return ''
      + fieldRow('Priority', '<input type="number" min="0" value="' + esc(num(s.priority, 0)) +
        '" onchange="setScreenField(' + idx + ', \'priority\', Number(this.value))" style="max-width:120px">')
      + fieldRow('Required status', renderRequiredStatusSelect(idx, s.required_status))
      + fieldRowFullWidth('Teams (any match)', '<div class="cb-grid">' + renderTeamCheckboxes(idx, s.teams) + '</div>');
  }
  if (k === 'time') {
    return ''
      + fieldRow('Priority', '<input type="number" min="0" value="' + esc(num(s.priority, 0)) +
        '" onchange="setScreenField(' + idx + ', \'priority\', Number(this.value))" style="max-width:120px">')
      + fieldRow('Start (HH:MM)', '<input type="text" value="' + esc(s.start_time || '00:00') +
        '" onchange="setScreenField(' + idx + ', \'start_time\', this.value)" style="max-width:120px">')
      + fieldRow('End (HH:MM)', '<input type="text" value="' + esc(s.end_time || '') +
        '" onchange="setScreenField(' + idx + ', \'end_time\', this.value || undefined)" placeholder="(optional)" style="max-width:120px">')
      + fieldRowFullWidth('Weekdays (empty = any)', '<div class="cb-grid">' + renderWeekdayCheckboxes(idx, s.weekdays) + '</div>');
  }
  if (k === 'secondary_game') {
    return ''
      + fieldRow('With priority', '<input type="text" value="' + esc(priorityString(s.with_priority)) +
        '" onchange="setScreenField(' + idx + ', \'with_priority\', parsePriorityField(this.value))" placeholder="0 or 0,1,2" style="max-width:160px">')
      + fieldRow('Required status', renderRequiredStatusSelect(idx, s.required_status))
      + fieldRowFullWidth('Teams', '<div class="cb-grid">' + renderTeamCheckboxes(idx, s.teams) + '</div>');
  }
  if (k === 'news' || k === 'standings') {
    return ''
      + fieldRow('With priority', '<input type="text" value="' + esc(priorityString(s.with_priority)) +
        '" onchange="setScreenField(' + idx + ', \'with_priority\', parsePriorityField(this.value))" placeholder="0 or 0,1,2" style="max-width:160px">')
      + fieldRow('Seconds', '<input type="number" min="5" value="' + esc(num(s.seconds, 20)) +
        '" onchange="setScreenField(' + idx + ', \'seconds\', Number(this.value))" style="max-width:120px">');
  }
  // plugin (any other kind)
  return ''
    + fieldRow('Plugin name (kind)', '<input type="text" value="' + esc(s.kind) +
      '" onchange="setScreenField(' + idx + ', \'kind\', this.value); renderScreens()" style="max-width:240px">')
    + fieldRow('With priority', '<input type="text" value="' + esc(priorityString(s.with_priority)) +
      '" onchange="setScreenField(' + idx + ', \'with_priority\', parsePriorityField(this.value))" placeholder="0 or 0,1,2" style="max-width:160px">')
    + fieldRow('Seconds', '<input type="number" min="5" value="' + esc(num(s.seconds, 20)) +
      '" onchange="setScreenField(' + idx + ', \'seconds\', Number(this.value))" style="max-width:120px">');
}

function fieldRow(label, control) {
  return '<div class="field-row"><div class="field-label">' + esc(label) + '</div><div class="field-value">' + control + '</div></div>';
}

function fieldRowFullWidth(label, body) {
  return '<div class="field-row" style="grid-template-columns:1fr">' +
    '<div class="field-label" style="border-right:none;border-bottom:1px solid #2d3748;padding-bottom:10px">' + esc(label) + '</div>' +
    body + '</div>';
}

function screenCard(idx, s) {
  const k = classifyKind(s.kind);
  const label = k === 'plugin' ? 'Plugin: ' + esc(s.kind) : k;
  return ''
    + '<div class="section" style="margin-bottom:12px">'
    +   '<div class="section-header" style="display:flex;justify-content:space-between;align-items:center;gap:8px">'
    +     '<span>#' + (idx + 1) + ' &middot; ' + label + '</span>'
    +     '<span style="display:flex;gap:6px">'
    +       '<button type="button" onclick="moveScreen(' + idx + ', -1)" style="padding:4px 10px;background:#4a5568;color:#e2e8f0;font-size:.75rem">Up</button>'
    +       '<button type="button" onclick="moveScreen(' + idx + ', 1)" style="padding:4px 10px;background:#4a5568;color:#e2e8f0;font-size:.75rem">Down</button>'
    +       '<button type="button" onclick="removeScreen(' + idx + ')" style="padding:4px 10px;background:#c53030;color:#fff;font-size:.75rem">Remove</button>'
    +     '</span>'
    +   '</div>'
    +   screenFields(idx, s)
    + '</div>';
}

function renderScreens() {
  const host = document.getElementById('screens-list');
  if (!host) return;
  host.innerHTML = SCREENS.map((s, i) => screenCard(i, s)).join('');
}

function setScreenField(idx, key, value) {
  if (value === undefined) delete SCREENS[idx][key];
  else SCREENS[idx][key] = value;
}

function toggleScreenTeam(idx, team, on) {
  SCREENS[idx].teams = SCREENS[idx].teams || [];
  const arr = SCREENS[idx].teams;
  const i = arr.indexOf(team);
  if (on && i < 0) arr.push(team);
  if (!on && i >= 0) arr.splice(i, 1);
}

function toggleScreenWeekday(idx, day, on) {
  SCREENS[idx].weekdays = SCREENS[idx].weekdays || [];
  const arr = SCREENS[idx].weekdays;
  const i = arr.indexOf(day);
  if (on && i < 0) arr.push(day);
  if (!on && i >= 0) arr.splice(i, 1);
}

function moveScreen(idx, dir) {
  const j = idx + dir;
  if (j < 0 || j >= SCREENS.length) return;
  [SCREENS[idx], SCREENS[j]] = [SCREENS[j], SCREENS[idx]];
  renderScreens();
}

function removeScreen(idx) {
  if (!confirm('Remove screen #' + (idx + 1) + '?')) return;
  SCREENS.splice(idx, 1);
  renderScreens();
}

function addScreen() {
  const kind = document.getElementById('add-screen-kind').value;
  let s;
  if (kind === 'game')                s = { kind: 'game', priority: 1, teams: [] };
  else if (kind === 'time')           s = { kind: 'time', priority: 1, start_time: '00:00' };
  else if (kind === 'secondary_game') s = { kind: 'secondary_game', with_priority: 0, teams: [] };
  else if (kind === 'news')           s = { kind: 'news', with_priority: 0, seconds: 20 };
  else if (kind === 'standings')      s = { kind: 'standings', with_priority: 0, seconds: 20 };
  else                                s = { kind: 'example', with_priority: 0, seconds: 20 };
  SCREENS.push(s);
  renderScreens();
}

function syncScreensJson() {
  const el = document.getElementById('screens_json');
  if (el) el.value = JSON.stringify(SCREENS);
}

document.addEventListener('DOMContentLoaded', () => {
  const cb = document.getElementById('demo_date_enabled');
  if (cb) toggleDemoDate(cb.checked);
  renderScreens();
});
"""


def build_page(config, alert_html="", active_tab="config"):
    scoreboard_colors = load_json_with_example(SCOREBOARD_COLORS_FILE, SCOREBOARD_COLORS_EXAMPLE_FILE)
    teams_colors      = load_json_with_example(TEAMS_COLORS_FILE, TEAMS_COLORS_EXAMPLE_FILE)

    c = config
    nt    = c.get("news_ticker", {})
    rot   = c.get("rotation", {})
    rates = rot.get("rates", {})
    wx    = c.get("weather", {})
    st    = c.get("standings", {})

    nt_teams = nt.get("teams") or []
    if isinstance(nt_teams, str):
        nt_teams = [nt_teams]
    st_divs = st.get("divisions") or []
    if isinstance(st_divs, str):
        st_divs = [st_divs]

    def ck(val):
        return "checked" if val else ""

    scrolling_raw = c.get("scrolling_speed", 2)
    scrolling_int = int(scrolling_raw) if str(scrolling_raw).isdigit() else 2

    screens = rot.get("screens", [])
    initial_state = json.dumps({
        "SCREENS": screens,
        "BUILTIN_KINDS": BUILTIN_SCREEN_KINDS,
        "TEAMS_BY_DIV": MLB_TEAMS_BY_DIVISION,
        "WEEKDAYS_LIST": WEEKDAYS,
        "REQUIRED_STATUS": REQUIRED_STATUS_VALUES,
    }).replace("</", "<\\/")

    add_screen_options = "".join(
        f'<option value="{k}">{k}</option>' for k in BUILTIN_SCREEN_KINDS
    ) + '<option value="plugin">plugin (custom)</option>'

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
  </div>

  <!-- ═══════════════════ CONFIG TAB ═══════════════════ -->
  <div class="tab-panel" id="config">
  <form method="POST" action="/save?tab=config" onsubmit="syncScreensJson()">
    <input type="hidden" id="screens_json" name="screens_json" value="">

    <div class="section">
      <div class="section-header">News Ticker</div>
      <div class="field-row" style="grid-template-columns:1fr">
        <div class="field-label" style="border-right:none;border-bottom:1px solid #2d3748;padding-bottom:10px">
          Teams &mdash; <span style="font-size:.75rem;color:#718096">Teams to show news headlines for</span>
        </div>
        <div class="cb-grid">{build_team_checkboxes(nt_teams, "news_ticker__teams")}</div>
      </div>
      <div class="field-row"><div class="field-label">Trade rumors</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__traderumors" {ck(nt.get("traderumors", True))}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">MLB news</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__mlb_news" {ck(nt.get("mlb_news", True))}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Countdowns</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__countdowns" {ck(nt.get("countdowns", True))}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Show date</div><div class="field-value"><label class="toggle"><input type="checkbox" name="news_ticker__date" {ck(nt.get("date", True))}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row">
        <div class="field-label">Date format</div>
        <div class="field-value" style="flex-direction:column;align-items:flex-start;gap:6px">
          <input type="text" name="news_ticker__date_format" value="{nt.get("date_format", "%A, %B %-d")}" placeholder="%A, %B %-d">
          <span style="font-size:.75rem;color:#718096">
            Uses Python strftime codes &mdash;
            <a href="https://strftime.org" target="_blank" rel="noopener"
              style="color:#63b3ed;text-decoration:none">strftime.org</a>
            &nbsp;&middot;&nbsp; e.g. <code style="color:#90cdf4">%A</code> = Monday &nbsp;
            <code style="color:#90cdf4">%B</code> = January &nbsp;
            <code style="color:#90cdf4">%-d</code> = 4
          </span>
        </div>
      </div>
      <p class="note" style="padding:0 16px 12px">Events list (<code>news_ticker.events</code>) preserved from JSON; edit directly to change.</p>
    </div>

    <div class="section">
      <div class="section-header">Standings</div>
      <div class="field-row" style="grid-template-columns:1fr">
        <div class="field-label" style="border-right:none;border-bottom:1px solid #2d3748;padding-bottom:10px">
          Divisions &mdash; <span style="font-size:.75rem;color:#718096">Shown in standings rotation</span>
        </div>
        <div class="cb-grid" style="gap:8px 16px">{build_division_checkboxes(st_divs)}</div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">Weather</div>
      <div class="field-row"><div class="field-label">API Key</div><div class="field-value"><input type="text" name="weather__apikey" value="{wx.get("apikey", "")}" placeholder="OpenWeatherMap API key"></div></div>
      <div class="field-row"><div class="field-label">Location</div><div class="field-value"><input type="text" name="weather__location" value="{wx.get("location", "")}" placeholder="e.g. Chicago,il,us"></div></div>
      <div class="field-row"><div class="field-label">Metric units</div><div class="field-value"><label class="toggle"><input type="checkbox" name="weather__metric_units" {ck(wx.get("metric_units", False))}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Pregame (include in pre-game text)</div><div class="field-value"><label class="toggle"><input type="checkbox" name="weather__pregame" {ck(wx.get("pregame", True))}><span class="toggle-slider"></span></label></div></div>
    </div>

    <div class="section">
      <div class="section-header">Rotation</div>
      <div class="field-row"><div class="field-label">Scroll until finished</div><div class="field-value"><label class="toggle"><input type="checkbox" name="rotation__scroll_until_finished" {ck(rot.get("scroll_until_finished", True))}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row"><div class="field-label">Rate: live (seconds)</div><div class="field-value"><input type="number" name="rotation__rates__live" value="{rates.get("live", 15)}" min="1" step="0.5" style="max-width:140px"></div></div>
      <div class="field-row"><div class="field-label">Rate: final (seconds)</div><div class="field-value"><input type="number" name="rotation__rates__final" value="{rates.get("final", 15)}" min="1" step="0.5" style="max-width:140px"></div></div>
      <div class="field-row"><div class="field-label">Rate: pregame (seconds)</div><div class="field-value"><input type="number" name="rotation__rates__pregame" value="{rates.get("pregame", 15)}" min="1" step="0.5" style="max-width:140px"></div></div>
    </div>

    <div class="section">
      <div class="section-header">Rotation Screens</div>
      <div id="screens-list" style="padding:14px 14px 4px"></div>
      <div style="display:flex;gap:8px;align-items:center;padding:6px 14px 14px;flex-wrap:wrap">
        <select id="add-screen-kind" style="background:#2d3748;border:1px solid #4a5568;border-radius:6px;color:#e2e8f0;padding:7px 10px;font-size:.85rem">
          {add_screen_options}
        </select>
        <button type="button" onclick="addScreen()" class="btn-primary" style="padding:7px 16px">Add Screen</button>
        <span style="font-size:.75rem;color:#718096">Use Up/Down to reorder. Remove deletes a screen.</span>
      </div>
    </div>

    <div class="section">
      <div class="section-header">General</div>
      <div class="field-row"><div class="field-label">Time format</div><div class="radio-group">{build_time_format_radios(c.get("time_format", "12h"))}</div></div>
      <div class="field-row"><div class="field-label">End of day (HH:MM)</div><div class="field-value"><input type="text" name="end_of_day" value="{c.get("end_of_day", "00:00")}" placeholder="00:00" style="max-width:120px"></div></div>
      <div class="field-row"><div class="field-label">Sync delay (seconds)</div><div class="field-value"><input type="number" name="sync_delay_seconds" value="{c.get("sync_delay_seconds", 0)}" min="0" step="1" style="max-width:140px"></div></div>
      <div class="field-row"><div class="field-label">API refresh rate (seconds)</div><div class="field-value"><input type="number" name="api_refresh_rate" value="{c.get("api_refresh_rate", 5)}" min="1" step="1" style="max-width:140px"></div></div>
      <div class="field-row"><div class="field-label">Scrolling speed (0–6)</div><div class="field-value" style="padding:10px 14px">{build_scrolling_speed_slider(scrolling_int)}</div></div>
      <div class="field-row"><div class="field-label">Debug mode</div><div class="field-value"><label class="toggle"><input type="checkbox" name="debug" {ck(c.get("debug", False))}><span class="toggle-slider"></span></label></div></div>
      <div class="field-row">
        <div class="field-label">Demo date</div>
        <div class="field-value" style="flex-direction:column;align-items:flex-start;gap:8px">
          <label class="toggle" title="Enable demo mode">
            <input type="checkbox" id="demo_date_enabled" {"checked" if c.get("demo_date") else ""}
              onchange="toggleDemoDate(this.checked)">
            <span class="toggle-slider"></span>
          </label>
          <div id="demo_date_picker" style="display:{"block" if c.get("demo_date") else "none"}">
            <input type="date" name="demo_date"
              value="{str(c.get("demo_date")) if c.get("demo_date") else ""}"
              style="background:#2d3748;border:1px solid #4a5568;border-radius:6px;color:#e2e8f0;padding:7px 10px;font-size:.85rem;outline:none;color-scheme:dark">
          </div>
          <span style="font-size:.75rem;color:#718096">{"Demo mode: " + str(c.get("demo_date")) if c.get("demo_date") else "Live data"}</span>
        </div>
      </div>
    </div>

    <div class="actions">
      <button type="submit" name="action" value="save" class="btn-primary">Save</button>
      <button type="submit" name="action" value="save_restart" class="btn-restart">Save &amp; Restart Service</button>
    </div>
    <p class="note">Saved to <code>config.json</code>. Untouched fields (<code>matrix</code>, <code>plugins</code>, <code>news_ticker.events</code>, <code>$schema</code>, <code>format</code>) are preserved. Restart applies to the <code>{SERVICE_NAME}</code> systemd service.</p>
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
<script>Object.assign(window, {initial_state});</script>
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


def load_user_config():
    """Read the user's config.json verbatim (no example merge) so the save round-trip
    preserves keys the UI doesn't surface (matrix, plugins, $schema, news_ticker.events, etc.)."""
    if CONFIG_FILE.is_file():
        return json.loads(CONFIG_FILE.read_text())
    if EXAMPLE_CONFIG_FILE.is_file():
        return json.loads(EXAMPLE_CONFIG_FILE.read_text())
    return {}


def form_data_to_config(fields, existing):
    new = json.loads(json.dumps(existing))  # deep copy

    def get(key, default=""):
        vals = fields.get(key, [default])
        return vals[0] if vals else default

    def get_list(key):
        return fields.get(key, [])

    def checkbox(key):
        return key in fields

    nt = new.setdefault("news_ticker", {})
    nt["teams"]        = get_list("news_ticker__teams")
    nt["traderumors"]  = checkbox("news_ticker__traderumors")
    nt["mlb_news"]     = checkbox("news_ticker__mlb_news")
    nt["countdowns"]   = checkbox("news_ticker__countdowns")
    nt["date"]         = checkbox("news_ticker__date")
    nt["date_format"]  = get("news_ticker__date_format", "%A, %B %-d")

    st = new.setdefault("standings", {})
    st["divisions"] = get_list("standings__divisions")

    wx = new.setdefault("weather", {})
    wx["apikey"]       = get("weather__apikey", "")
    wx["location"]     = get("weather__location", "")
    wx["metric_units"] = checkbox("weather__metric_units")
    wx["pregame"]      = checkbox("weather__pregame")

    rot = new.setdefault("rotation", {})
    rot["scroll_until_finished"] = checkbox("rotation__scroll_until_finished")
    rates = rot.setdefault("rates", {})
    rates["live"]    = float(get("rotation__rates__live",    "15.0"))
    rates["final"]   = float(get("rotation__rates__final",   "15.0"))
    rates["pregame"] = float(get("rotation__rates__pregame", "15.0"))

    screens_raw = get("screens_json", "").strip()
    if screens_raw:
        try:
            rot["screens"] = json.loads(screens_raw)
        except json.JSONDecodeError:
            pass  # keep existing screens if JSON parse fails

    new["time_format"]        = get("time_format", "12h")
    new["end_of_day"]         = get("end_of_day", "00:00")
    new["sync_delay_seconds"] = int(float(get("sync_delay_seconds", "0")))
    new["api_refresh_rate"]   = int(float(get("api_refresh_rate", "5")))
    new["scrolling_speed"]    = int(get("scrolling_speed", "2"))
    new["debug"]              = checkbox("debug")

    demo_raw = get("demo_date", "").strip()
    new["demo_date"]          = demo_raw if demo_raw else False

    return new


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
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_save_config(self, tab):
        fields = self._read_body()
        action = fields.get("action", ["save"])[0]
        alert = ""
        try:
            new_config = form_data_to_config(fields, load_user_config())
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
