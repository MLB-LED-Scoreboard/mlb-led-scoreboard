#!/usr/bin/env python3
"""
Generates a new JSON configuration file from a schema by extracting defaults.

Usage:
  python generate_config.py --schema config.schema.json --output config.json
  python generate_config.py --schema colors/scoreboard.schema.json --output colors/scoreboard.json
  python generate_config.py --schema colors/teams.schema.json --output colors/teams.json
  python generate_config.py --schema coordinates/wxhy.schema.json --output coordinates/w64h32.json
"""

import argparse
import json
import os
import re
import sys

_MISSING = object()


def resolve_ref(ref, root):
  """Resolve a JSON Pointer ($ref starting with #/) within the schema."""
  if not ref.startswith('#/'):
    raise ValueError(f"Only local $refs are supported: {ref!r}")
  node = root
  for part in ref[2:].split('/'):
    node = node[part]
  return node


def defaults_from_schema(node, root):
  """
  Recursively derive a default value from a schema node.
  Returns _MISSING if no default can be determined.
  """
  # Resolve $ref, letting sibling keys override resolved values
  if '$ref' in node:
    resolved = resolve_ref(node['$ref'], root)
    merged = {**resolved, **{k: v for k, v in node.items() if k != '$ref'}}
    return defaults_from_schema(merged, root)

  # const always wins
  if 'const' in node:
    return node['const']

  # explicit default
  if 'default' in node:
    return node['default']

  node_type = node.get('type')

  if node_type == 'object':
    props = node.get('properties', {})
    required_keys = set(node.get('required', []))
    result = {}
    for key, prop_schema in props.items():
      val = defaults_from_schema(prop_schema, root)
      if val is not _MISSING:
        result[key] = val
      elif key in required_keys:
        result[key] = _placeholder(prop_schema, root)
    return result if result else _MISSING

  if node_type == 'array':
    return []

  # oneOf / anyOf: return the first sub-schema with a usable default
  for combiner in ('oneOf', 'anyOf'):
    if combiner in node:
      for option in node[combiner]:
        val = defaults_from_schema(option, root)
        if val is not _MISSING:
          return val

  return _MISSING


def _placeholder(node, root):
  """Return a zero-value placeholder for a node that has no default."""
  if '$ref' in node:
    resolved = resolve_ref(node['$ref'], root)
    merged = {**resolved, **{k: v for k, v in node.items() if k != '$ref'}}
    return _placeholder(merged, root)

  node_type = node.get('type')

  if node_type == 'number':
    return node.get('minimum', 0)
  if node_type == 'boolean':
    return False
  if node_type == 'string':
    enum = node.get('enum')
    return enum[0] if enum else ''
  if node_type == 'array':
    return []
  if node_type == 'object':
    props = node.get('properties', {})
    required_keys = set(node.get('required', []))
    result = {}
    for key, prop in props.items():
      val = defaults_from_schema(prop, root)
      if val is not _MISSING:
        result[key] = val
      elif key in required_keys:
        result[key] = _placeholder(prop, root)
    return result

  return None


def generate(schema_path, output_path, overwrite=False):
  with open(schema_path) as f:
    schema = json.load(f)

  indent = schema.get('x-indent', '  ')

  config = defaults_from_schema(schema, schema)

  if config is _MISSING or not isinstance(config, dict):
    print("Error: could not derive any defaults from the schema.", file=sys.stderr)
    sys.exit(1)

  if os.path.exists(output_path) and not overwrite:
    print(f"Error: {output_path!r} already exists. Use --overwrite to replace it.", file=sys.stderr)
    sys.exit(1)

  with open(output_path, 'w') as f:
    json.dump(config, f, indent=indent)
    f.write('\n')

  print(f"Generated {output_path}")


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Generate a config file from a JSON schema.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""examples:
  python generate_config.py --schema config.schema.json --output config.json
  python generate_config.py --schema colors/scoreboard.schema.json --output colors/scoreboard.json
  python generate_config.py --schema coordinates/wxhy.schema.json --output coordinates/w64h32.json
    """
  )
  parser.add_argument('--schema',    required=True, help='path to the JSON schema file')
  parser.add_argument('--output',    required=True, help='path to write the generated config')
  parser.add_argument('--check', action='store_true', help='exit')
  args = parser.parse_args()

  generate(args.schema, args.output, args.check)
