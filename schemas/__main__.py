"""
Generates JSON example files from schemas by extracting defaults.

When run without arguments, regenerates all example files under colors/,
coordinates/, and config.example.json from the schemas under schemas/.

Usage:
  python -m schemas                    # regenerate all example files
  python -m schemas --overwrite        # overwrite existing files
  python -m schemas --check            # check if a file would be changed
  python -m schemas --schema schemas/config.schema.json --output config.example.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

from jsonschema_default import create_from


def _preprocess(node):
  """
  Recursively walk the schema and, wherever a node has both '$ref' and
  'default' as siblings, drop the '$ref' so the library uses 'default'.
  """
  if not isinstance(node, dict):
    return node
  if '$ref' in node and 'default' in node:
    node = {k: v for k, v in node.items() if k != '$ref'}
  return {k: _preprocess(v) for k, v in node.items()}

def _postprocess(node):
  """
  Recursively walk the schema and, wherever a node has 'x-schema', replace
  it with '$schema'. This allows us to define editor '$schema' without
  colliding with JSON schema keywords.
  """
  if not isinstance(node, dict):
    return node
  if 'x-schema' in node:
    node['$schema'] = node['x-schema']
    del node['x-schema']
  return {k: _preprocess(v) for k, v in node.items()}

def generate(args):
  if args.schema and args.output:
    _generate(args.schema, args.output, args.overwrite, args.check)
  else:
    _generate_all(args.overwrite, args.check)

def _generate(schema_path, output_path, overwrite, check):
  with open(schema_path) as f:
    schema = json.load(f)

  indent = schema.get('x-indent', '  ')
  config = _postprocess(create_from(_preprocess(schema)))

  if not isinstance(config, dict):
    print(f"Error: could not derive any defaults from {schema_path}.", file=sys.stderr)
    sys.exit(1)

  if os.path.exists(output_path) and not overwrite and not check:
    print(f"Error: {output_path!r} already exists. Use --overwrite to replace it.", file=sys.stderr)
    sys.exit(1)

  if check:
    with open(output_path, 'r') as f:
      existing = json.load(f)

      if config == existing:
        return

      print(f"Error: config at {output_path} differs from schema", file=sys.stderr)
      sys.exit(1)

  os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

  with open(output_path, 'w') as f:
    json.dump(config, f, indent=indent)
    f.write('\n')

  print(f"Generated {output_path}")


def schema_to_output(schema_path):
  """Map schemas/foo/bar.schema.json -> foo/bar.example.json."""
  rel = Path(schema_path).relative_to('schemas')
  return str(rel).replace('.schema.json', '.example.json')


def _generate_all(overwrite=False, check=False):
  for schema_path in sorted(Path('schemas').rglob('*.schema.json')):
    if schema_path.name.startswith('_'):
      continue
    _generate(str(schema_path), schema_to_output(schema_path), overwrite, check)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Manage JSON schemas and associated examples',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""examples:
  python -m schemas                    # regenerate all example files
  python -m schemas --overwrite        # overwrite existing example files
  python -m schemas --schema schemas/config.schema.json --output config.example.json
    """
  )
  parser.add_argument('--schema',    help='Path to a single JSON schema file')
  parser.add_argument('--output',    help='Path to write the generated config (required with --schema)')
  parser.add_argument('--overwrite', action='store_true', help='Overwrite existing output files')
  parser.add_argument('--check',     action='store_true', help='Check if a file would be changed with --overwrite. Returns exit code 1 if so.')
  args = parser.parse_args()

  if args.schema:
    if not args.output:
      parser.error('--output is required when --schema is specified')
  
  generate(args)
