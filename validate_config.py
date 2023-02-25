import copy, json, os

ROOT_DIR        = "."
COORDINATES_DIR = "coordinates"
COLORS_DIR      = "colors"

def upsert_config(config, schema, result=None):
  '''
  Recursively updates deeply nested configuration against a given schema.
  At each level, the keys in the configuration are compared against the schema.

  This has 3 cases:
    * If present in the schema and configuration, no action is taken.
    * If present in the config but not schema, then the key is deleted from the configuration.
    * If present in the schema but not config, the entire child node is added to the configuration under the given key.

  If at any point the config is altered, the result is considered "dirty" and flagged for update.
  The dirty flag and resulting upserted config are returned as a tuple.
  '''
  if not result:
    result = copy.deepcopy(config)

  dirty = False

  for kind in [config, schema]:
    for key in kind.keys():
      if key in result and key in schema:
        if isinstance(result[key], dict):
          (possibly_dirty, result) = upsert_config(config[key], schema[key], result)

          # Don't let deeply nested upserts unset the dirty flag
          dirty = possibly_dirty or dirty

        continue

      dirty = True

      if key in result and key not in schema:
        result.pop(key)
      if key in schema and key not in result:
        result[key] = schema[key]

  return (dirty, result)

def custom_config_files():
  '''
  Iterates over any directories that contain custom configuration and checks for a custom `.json` config with a
  matching `.example` schema.
  '''
  files = []

  for directory in [ROOT_DIR, COORDINATES_DIR, COLORS_DIR]:
    for file in os.listdir(directory):
      if file.endswith(".json") and os.path.isfile(file + ".example"):
        files.append((directory, file))

  return files


if __name__ == "__main__":
  for directory, file in custom_config_files():
    with open(os.path.join(directory, file)) as config_file:
      config = json.load(config_file)

    with open(os.path.join(directory, file + ".example")) as schema_file:
      schema = json.load(schema_file)

    (changed, result) = upsert_config(config, schema)

    if changed:
      with open(os.path.join(directory, file), "w") as config_file:
        json.dump(result, config_file, indent=2)
