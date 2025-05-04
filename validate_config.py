import copy, json, os

ROOT_DIR        = "."
COORDINATES_DIR = os.path.join(ROOT_DIR, "coordinates")
COLORS_DIR      = os.path.join(ROOT_DIR, "colors")

VALIDATIONS = {
  ROOT_DIR: {
    "ignored_keys": [],
  },
  COORDINATES_DIR: {
    "ignored_keys": [
      "font_name"
    ],
  },
  COLORS_DIR: {
    "ignored_keys": []
  }
}


class TermColor:
  RED     = 31
  GREEN   = 32
  YELLOW  = 33
  BLUE    = 34
  MAGENTA = 35
  CYAN    = 36


def colorize(text, color_code):
  if color_code:
    return f"\033[{color_code}m{text}\033[0m"
  else:
    return text

def deep_pop(dictionary, key, path=[]):
  '''
  Pops a key from the target dictionary at the given path (or top level if not provided).
  '''
  temp = copy.deepcopy(dictionary)
  dictionary = temp

  for path_key in path:
    temp = temp[path_key]

  temp.pop(key)

  return dictionary

def deep_set(dictionary, key, value, path=[]):
  '''
  Sets a key from the target dictionary at the given path (or top level if not provided).
  '''
  temp = copy.deepcopy(dictionary)
  dictionary = temp

  for path_key in path:
    temp = temp[path_key]

  temp[key] = value

  return dictionary

def generate_change(origin, key, path):
  '''
  Creates a dictionary with all the keys along the path in the source dictionary, with the last key-value pair set to
  the target.

  The target key must be present in the origin.
  '''
  temp = {}
  change = temp

  for path_key in path:
    temp[path_key] = {}
    temp = temp[path_key]

  temp[key] = origin[key]

  return change  

def upsert_config(config, schema, options={}, result=None, changeset=None, path=None):
  '''
  Recursively updates deeply nested configuration against a given schema.
  At each level, the keys in the configuration are compared against the schema.

  This has 3 cases:
    * If present in the schema and configuration, no action is taken.
    * If present in the config but not schema, then the key is deleted from the configuration and appended to the
      `delete` changeset.
    * If present in the schema but not config, the entire child node is added to the configuration under the given
      key and appended to the `add` changeset.

  If at any point the config is altered, the result is considered "dirty" and flagged for update.
  The dirty flag, resulting upserted config, and changeset are returned as a tuple.
  '''
  if result is None:
    result = copy.deepcopy(config)
    changeset = { "add": [], "delete": [] }
    path = []

  dirty = False

  ignored_keys = options.get("ignored_keys", [])

  for kind in [config, schema]:
    for key in kind.keys():
      if ignored_keys and key in ignored_keys:
        continue

      if key in config and key in schema and key in result:
        if isinstance(result[key], dict):
          path = copy.deepcopy(path)
          path.append(key)

          (possibly_dirty, result, _) = upsert_config(config[key], schema[key], options, result, changeset, path)
          
          path.pop()

          # Don't let deeply nested upserts unset the dirty flag
          dirty = possibly_dirty or dirty

        continue

      if key in config and key not in schema:
        change = generate_change(config, key, path)

        if change not in changeset["delete"]:
          changeset["delete"].append(change)
          result = deep_pop(result, key, path=path)
          dirty = True
      if key in schema and key not in config:
        change = generate_change(schema, key, path)

        if change not in changeset["add"]:
          changeset["add"].append(change)
          result = deep_set(result, key, schema[key], path=path)
          dirty = True

  return (dirty, result, changeset)

def custom_config_files():
  '''
  Iterates over any directories that might contain custom configuration and checks for a custom `.json` config with a
  matching `.example` schema.
  '''
  files = []

  for directory, options in VALIDATIONS.items():
    for file in os.listdir(directory):
      if file.endswith(".json"):
        expected_schema_path = os.path.join(directory, file + ".example")
        if os.path.isfile(expected_schema_path):
          files.append((directory, file, options))

  return files

def indent_string(string, indent, num_indents=1):
  '''
  Indents a string a specified number of times.
  '''
  return (indent * num_indents) + string

def format_change(change, indent="  ", num_indents=0, delimiter="-", color=None):
  '''
  Formats a change (dict) with the given indent as JSON.
  
  Optionally pass the delimiter, number of indents, and text color as required.
  '''
  change_string = json.dumps(change, indent=indent)
  space = " " * (len(delimiter) + 1)
  output = ""
  whitespace_size = len(indent)

  for line_no, line in enumerate(change_string.split("\n")[1:]):
    if line_no == 0:
      # Indent the string with the delimiter, after slicing off all the extra whitespace at the beginning.
      line = indent_string(delimiter + " " + line[whitespace_size:], indent, num_indents)
    else:
      # Indent the string with the delimiter, after slicing off all the extra whitespace at the beginning.
      # This also accounts for the whitespace taken up by the delimiter + 1 extra space, and adds a newline.
      line = "\n" + indent_string(space + line[whitespace_size:], indent, num_indents)

    if color:
      line = colorize(line, color)

    output += line.rstrip()

  return output.strip("\n")

def perform_validation(root_dir=ROOT_DIR):
  '''
  Performs configuration validation and upserting, printing status along the way.
  '''
  indent = "  "

  print("Fetching custom config files...")

  for directory, file, options in custom_config_files():
    print(indent_string(f"- Found custom configuration at {os.path.join(directory, file)}!", indent))

    with open(os.path.join(directory, file)) as config_file:
      config = json.load(config_file)

    with open(os.path.join(directory, file + ".example")) as schema_file:
      schema = json.load(schema_file)

    should_overrwrite_config = False

    (changed, result, changes) = upsert_config(config, schema, options)

    should_overrwrite_config = should_overrwrite_config or changed

    if changed:
      print(indent_string("Adding missing keys and deleting unused configuration options...", indent, 2))

      change_options = [
        ("add", "Additions", TermColor.GREEN),
        ("delete", "Deletions (these options are no longer used):", TermColor.RED)
      ]

      for change_type, preamble, color in change_options:
        if len(changes[change_type]) > 0:
          print(indent_string(preamble, indent, 3))

          for change in changes[change_type]:
            print(format_change(change, indent, num_indents=4, color=color))

    if should_overrwrite_config:
      with open(os.path.join(directory, file), "w") as config_file:
        json.dump(result, config_file, indent=indent)
      print(indent_string(f"Finished updating {os.path.join(directory, file)}!", indent, 3))
    else:
      print(
        colorize(
          indent_string("Configuration is up-to-date.", indent, 3),
          TermColor.GREEN
        )
      )

if __name__ == "__main__":
  perform_validation()
