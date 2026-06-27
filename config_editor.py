#!/usr/bin/env python3
"""
MLB LED Scoreboard - Config Web Editor

A small, dependency-free web app for editing the scoreboard's configuration from
a browser on your LAN (e.g. http://raspberrypi.local/). The form is generated
directly from the JSON schemas under ``schemas/``, so every option carries its
own label and description and new options appear automatically.

It reads from your custom ``config.json`` if present (otherwise the bundled
``config.example.json``), validates/reconciles against the schema's example using
the same logic as ``validate_config.py``, backs up the previous file, and writes
``config.json``.

Phase 2 hooks for the boolean options in ``coordinates/<size>.json`` are wired
through the same machinery (``/api/schema/coordinates/<size>``).

Usage:
    python config_editor.py [--port 80] [--host 0.0.0.0] [--service NAME]
"""

import argparse
import json
import logging
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

# Local imports — reuse the project's own reconciler so the editor enforces the
# exact same rules as the CLI verifier.
import validate_config
from data.paths import ROOT_DIRECTORY, COORDINATES_DIRECTORY

LOGGER = logging.getLogger("config_editor")

ROOT = Path(ROOT_DIRECTORY)
STATIC_DIR = ROOT / "config_editor_static"
SCHEMAS_DIR = ROOT / "schemas"

CONFIG_FILE = ROOT / "config.json"
EXAMPLE_CONFIG_FILE = ROOT / "config.example.json"
CONFIG_SCHEMA_FILE = SCHEMAS_DIR / "config.schema.json"

# Service name candidates probed for the optional "restart" button.
SERVICE_NAME_PATTERN = re.compile(r"mlb.*scoreboard", re.IGNORECASE)

# ── JSON helpers ────────────────────────────────────────────────────────────────


def deep_update(base, overrides):
    """Recursively merge ``overrides`` onto a copy of ``base``."""
    result = dict(base)
    for k, v in overrides.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_update(result[k], v)
        else:
            result[k] = v
    return result


def load_json(path):
    return json.loads(Path(path).read_text())


def bundle_schema(schema):
    """Inline every $ref (internal '#/...' and external './_common.schema.json#/...')
    so the client receives a self-contained schema with no refs to resolve.

    Cycles are guarded by a ref stack; an unresolvable ref is dropped (its sibling
    keys are kept), which degrades gracefully to a freeform field."""
    common = {}
    common_path = SCHEMAS_DIR / "coordinates" / "_common.schema.json"
    if common_path.is_file():
        common = load_json(common_path)

    def lookup_in(doc, ref):
        node = doc
        for p in ref.split("#/", 1)[1].split("/"):
            node = node.get(p) if isinstance(node, dict) else None
            if node is None:
                return None
        return node

    # ``doc`` is the schema document the current subtree belongs to, so that an
    # internal "#/..." ref originating inside _common resolves against _common.
    def resolve(node, stack, doc):
        if isinstance(node, list):
            return [resolve(x, stack, doc) for x in node]
        if not isinstance(node, dict):
            return node
        if "$ref" in node:
            ref = node["$ref"]
            siblings = {k: v for k, v in node.items() if k != "$ref"}
            if ref.startswith("#/"):
                target, next_doc = lookup_in(doc, ref), doc
            elif "_common.schema.json#/" in ref:
                target, next_doc = lookup_in(common, ref), common
            else:
                target, next_doc = None, doc
            marker = (ref, id(next_doc))
            if target is None or marker in stack:
                return {k: resolve(v, stack, doc) for k, v in siblings.items()}
            merged = {**target, **siblings}
            return resolve(merged, stack + [marker], next_doc)
        return {k: resolve(v, stack, doc) for k, v in node.items()}

    return resolve(schema, [], schema)


def load_merged(custom_path, example_path):
    """Example as the base, custom merged on top. Returns (values, source)."""
    values = {}
    source = None
    if Path(example_path).is_file():
        values = load_json(example_path)
        source = example_path.name
    if Path(custom_path).is_file():
        values = deep_update(values, load_json(custom_path))
        source = custom_path.name
    return values, source


def backup_file(path):
    """Timestamped backup of ``path`` if it exists. Returns the backup path or None."""
    path = Path(path)
    if not path.is_file():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = path.with_suffix(path.suffix + f".bak-{stamp}")
    shutil.copy2(path, bak)
    return bak


# ── Config save / validate ──────────────────────────────────────────────────────


def reconcile(values, example, options):
    """Run the project's upsert against the example. Returns (result, changes)."""
    _dirty, result, changes = validate_config.upsert_config(values, example, options)
    return result, changes


def validate_runtime(config):
    """Run the board's own parsing to catch errors before writing.

    Returns a list of human-readable error strings (empty == valid). Uses the
    scoreboard's real validators so the editor rejects anything that would crash
    Config() at startup (priority 0, unknown teams, missing with_priority=0, ...).
    Degrades gracefully (no runtime check) if the board modules can't be imported.
    """
    errors = []
    try:
        from data.config import _screen_rules_from_json
        from data.teams import get_team_id
    except Exception as e:  # board package unavailable — skip runtime check
        LOGGER.warning("Skipping runtime validation (board import failed): %s", e)
        return errors

    rotation = config.get("rotation", {}) or {}
    try:
        _screen_rules_from_json(rotation.get("screens", []) or [])
    except Exception as e:
        errors.append(str(e))

    for team in (config.get("news_ticker", {}) or {}).get("teams", []) or []:
        try:
            get_team_id(team)
        except Exception as e:
            errors.append(f"News ticker: {e}")

    return errors


def save_config(values):
    """Validate, back up, and write config.json. Returns a result dict."""
    example = load_json(EXAMPLE_CONFIG_FILE)
    result, changes = reconcile(values, example, _root_options())

    # Ensure it serialises cleanly before touching disk.
    serialized = json.dumps(result, indent=2)

    # Refuse to write a config the board would reject at startup.
    errors = validate_runtime(result)
    if errors:
        return {"ok": False, "error": "Configuration is invalid — nothing was saved.", "errors": errors}

    bak = backup_file(CONFIG_FILE)
    CONFIG_FILE.write_text(serialized + "\n")
    return {
        "ok": True,
        "written": CONFIG_FILE.name,
        "backup": bak.name if bak else None,
        "changes": _summarize_changes(changes),
    }


def _root_options():
    # Mirror validate_config.VALIDATIONS for the root dir (keyed by Path there).
    for key, opts in validate_config.VALIDATIONS.items():
        if Path(key).resolve() == ROOT.resolve():
            return opts
    return {"ignored_keys": ["matrix-*", "plugins-*"], "renamed_keys": {}}


def _summarize_changes(changes):
    return {
        "added": len(changes.get("add", [])),
        "deleted": len(changes.get("delete", [])),
        "renamed": len(changes.get("rename", [])),
    }


# ── Coordinates (Phase 2) ───────────────────────────────────────────────────────


def coordinate_sizes():
    """Available layout sizes that have both a schema and an example."""
    sizes = []
    for schema in sorted((SCHEMAS_DIR / "coordinates").glob("w*.schema.json")):
        size = schema.name.replace(".schema.json", "")
        if (COORDINATES_DIRECTORY / f"{size}.example.json").is_file():
            sizes.append(size)
    return sizes


def coordinate_paths(size):
    custom = COORDINATES_DIRECTORY / f"{size}.json"
    example = COORDINATES_DIRECTORY / f"{size}.example.json"
    return custom, example


# ── Line-score display toggles (apply to every layout) ──────────────────────────
#
# Four booleans under teams.line_score that users actually want to flip, surfaced
# on the main page and written to *every* coordinate file so the setting applies
# regardless of which panel resolution is in use. Existing custom layouts are
# updated surgically (only these keys); sizes with no custom file get a minimal
# override, which the board deep-merges over the example at runtime.

LINE_SCORE_KEYS = [
    "show_hits_and_errors",
    "show_abs_challenges",
    "compress_digits",
    "shorten_team_name_on_high_line_score",
]
PRIMARY_SIZE = "w128h64"


def get_line_score():
    """Representative current values, read from the primary size (custom-or-example)."""
    sizes = coordinate_sizes()
    primary = PRIMARY_SIZE if PRIMARY_SIZE in sizes else (sizes[0] if sizes else None)
    values = {k: False for k in LINE_SCORE_KEYS}
    if primary:
        custom, example = coordinate_paths(primary)
        merged, _ = load_merged(custom, example)
        ls = merged.get("teams", {}).get("line_score", {})
        for k in LINE_SCORE_KEYS:
            values[k] = bool(ls.get(k, False))
    return {"values": values, "keys": LINE_SCORE_KEYS}


def save_line_score(body):
    """Write the requested line_score booleans into every coordinate custom file."""
    written = []
    for size in coordinate_sizes():
        custom, example = coordinate_paths(size)
        # Preserve any existing custom layout; otherwise start a minimal override
        # that the board will deep-merge over the example.
        if custom.is_file():
            doc = load_json(custom)
        else:
            doc = {"$schema": load_json(example).get("$schema", f"./../schemas/coordinates/{size}.schema.json")}
        ls = doc.setdefault("teams", {}).setdefault("line_score", {})
        for k in LINE_SCORE_KEYS:
            if k in body:
                ls[k] = bool(body[k])
        bak = backup_file(custom)
        custom.write_text(json.dumps(doc, indent=2) + "\n")
        written.append({"size": size, "backup": bak.name if bak else None})
    return {"ok": True, "written": [w["size"] for w in written], "count": len(written)}


# ── Service detection ───────────────────────────────────────────────────────────


def detect_service(override=None):
    """Find a scoreboard service to (optionally) restart. Best-effort, never raises."""
    if override:
        return {"detected": True, "name": override, "manager": _guess_manager()}
    # systemd (Linux / Raspberry Pi)
    try:
        out = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--all", "--no-legend", "--plain"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        for line in out.splitlines():
            unit = line.split()[0] if line.split() else ""
            if unit.endswith(".service") and SERVICE_NAME_PATTERN.search(unit):
                return {"detected": True, "name": unit.removesuffix(".service"), "manager": "systemd"}
    except Exception:
        pass
    # launchd (macOS)
    try:
        out = subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=5).stdout
        for line in out.splitlines():
            label = line.split()[-1] if line.split() else ""
            if SERVICE_NAME_PATTERN.search(label):
                return {"detected": True, "name": label, "manager": "launchd"}
    except Exception:
        pass
    return {"detected": False, "name": None, "manager": None}


def _guess_manager():
    return "systemd" if shutil.which("systemctl") else ("launchd" if shutil.which("launchctl") else None)


def restart_service(svc):
    if not svc.get("detected"):
        return {"ok": False, "error": "No scoreboard service detected."}
    name, manager = svc["name"], svc["manager"]
    try:
        if manager == "systemd":
            subprocess.run(["sudo", "systemctl", "restart", name], check=True, timeout=30)
        elif manager == "launchd":
            subprocess.run(["launchctl", "kickstart", "-k", f"system/{name}"], check=True, timeout=30)
        else:
            return {"ok": False, "error": f"Unknown service manager for {name}."}
        return {"ok": True, "restarted": name}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── HTTP handler ────────────────────────────────────────────────────────────────


class Handler(BaseHTTPRequestHandler):
    service_override = None  # set from CLI

    def log_message(self, fmt, *args):
        sys.stderr.write("[config-editor] " + (fmt % args) + "\n")

    # -- helpers --
    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, content_type):
        try:
            body = Path(path).read_bytes()
        except OSError:
            self._send_json({"error": "not found"}, 404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    # -- routing --
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            return self._send_file(STATIC_DIR / "editor.html", "text/html; charset=utf-8")
        if path == "/editor.js":
            return self._send_file(STATIC_DIR / "editor.js", "application/javascript")
        if path == "/editor.css":
            return self._send_file(STATIC_DIR / "editor.css", "text/css")
        if path == "/api/schema/config":
            values, source = load_merged(CONFIG_FILE, EXAMPLE_CONFIG_FILE)
            return self._send_json({
                "schema": bundle_schema(load_json(CONFIG_SCHEMA_FILE)),
                "values": values,
                "source": source,
            })
        if path == "/api/coordinates":
            return self._send_json({"sizes": coordinate_sizes()})
        m = re.match(r"^/api/schema/coordinates/(w\d+h\d+)$", path)
        if m:
            size = m.group(1)
            custom, example = coordinate_paths(size)
            values, source = load_merged(custom, example)
            return self._send_json({
                "schema": bundle_schema(load_json(SCHEMAS_DIR / "coordinates" / f"{size}.schema.json")),
                "values": values,
                "source": source,
                "booleansOnly": True,
            })
        if path == "/api/line_score":
            return self._send_json(get_line_score())
        if path == "/api/service":
            return self._send_json(detect_service(self.service_override))
        return self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/save/config":
                return self._send_json(save_config(self._read_body()))
            if path == "/api/save/line_score":
                return self._send_json(save_line_score(self._read_body()))
            m = re.match(r"^/api/save/coordinates/(w\d+h\d+)$", path)
            if m:
                return self._send_json(self._save_coordinates(m.group(1), self._read_body()))
            if path == "/api/restart":
                return self._send_json(restart_service(detect_service(self.service_override)))
        except Exception as e:
            self.log_message("error handling %s: %s", path, e)
            return self._send_json({"ok": False, "error": str(e)}, 500)
        return self._send_json({"error": "not found"}, 404)

    def _save_coordinates(self, size, values):
        custom, example = coordinate_paths(size)
        example_data = load_json(example)
        options = _coord_options()
        _dirty, result, changes = validate_config.upsert_config(values, example_data, options)
        serialized = json.dumps(result, indent=2)
        bak = backup_file(custom)
        custom.write_text(serialized + "\n")
        return {
            "ok": True,
            "written": custom.name,
            "backup": bak.name if bak else None,
            "changes": _summarize_changes(changes),
        }


def _coord_options():
    for key, opts in validate_config.VALIDATIONS.items():
        if Path(key).resolve() == COORDINATES_DIRECTORY.resolve():
            return opts
    return {"ignored_keys": ["font_name", "plugins-*"], "renamed_keys": {}}


# ── Entrypoint ──────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="MLB LED Scoreboard config web editor")
    parser.add_argument("--port", type=int, default=80, help="Port to listen on (default 80)")
    parser.add_argument("--host", default="0.0.0.0", help="Interface to bind (default all)")
    parser.add_argument("--service", default=None, help="Override the service name for the restart button")
    args = parser.parse_args()

    Handler.service_override = args.service

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[config-editor] serving on http://{args.host}:{args.port}/ (Ctrl-C to stop)")
    svc = detect_service(args.service)
    if svc["detected"]:
        print(f"[config-editor] scoreboard service detected: {svc['name']} ({svc['manager']})")
    else:
        print("[config-editor] no scoreboard service detected — restart button hidden")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[config-editor] shutting down")
        httpd.shutdown()


if __name__ == "__main__":
    main()
