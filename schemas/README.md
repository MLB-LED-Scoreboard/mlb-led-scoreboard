# `schemas`

JSON schemas for validating and documenting scoreboard configuration files, coordinates, and colors. Also contains a tool for generating example files from schema defaults.

## Structure

| Path | Description |
|------|-------------|
| `config.schema.json` | Schema for the main `config.json` |
| `colors/*.schema.json` | Schemas for color definition files |
| `coordinates/*.schema.json` | Schemas for per-resolution coordinate files |

Files prefixed with `_` (e.g. `_common.schema.json`) are shared definitions referenced by other schemas and are not processed directly.

## Installing dev dependencies

Schema management requires additional dependencies that are not installed by default. Make sure you've installed dev requirements:

```sh
# Ideally within a venv
python -m pip install -r requirements.dev.txt
```

## Generating example files

---------------
> [!IMPORTANT]
> **Do not edit example files directly.** They are generated from schema defaults and any manual changes will be overwritten. To change an example value, update the `default` in the relevant schema and regenerate.
---------------

## Command Line Interface

Run from the repo root:

```bash
python -m schemas                    # regenerate all example files
python -m schemas --overwrite        # overwrite existing files
python -m schemas --check            # exit 1 if any file would change

# single file
python -m schemas --schema schemas/config.schema.json --output config.example.json
```

Output paths are derived from schema paths: `schemas/foo/bar.schema.json` -> `foo/bar.example.json`.
