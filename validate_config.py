import copy, json, os

ROOT_DIR        = "."
COORDINATES_DIR = os.path.join(ROOT_DIR, "coordinates")
COLORS_DIR      = os.path.join(ROOT_DIR, "colors")

VALIDATIONS = {
  ROOT_DIR: {
    "ignored_keys": [],
    "renamed_keys": {},
  },
  COORDINATES_DIR: {
    "ignored_keys": [
      "font_name",
      "no_hitter",
      "perfect_game",
      "warmup"
    ],
    "renamed_keys": {},
  },
  COLORS_DIR: {
    "ignored_keys": [
      "city_connect"
    ],
    "renamed_keys": {},
  }
}

INDENT_SIZE = 2
INDENT = " " * INDENT_SIZE


class TermColor:
  RED     = 31
  GREEN   = 32
  YELLOW  = 33
  BLUE    = 34
  MAGENTA = 35
  CYAN    = 36


def colorize(text, color_code):
  '''
  Adds ANSI color codes to a string for terminal output.
  '''
  if color_code:
    return f"\033[{color_code}m{text}\033[0m"
  else:
    return text
  
def indent_string(string, amt=1, indent=INDENT):
  '''
  Indents a string a specified number of times.
  '''
  return (indent * amt) + string

def output(string, indent=0, color=None):
  '''
  Outputs a string with the given INDENT and color.
  '''
  if color:
    string = colorize(string, color)

  print(indent_string(string, indent))

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

def reversible(d):
  '''
  Simple reversible dict. Returns a dict with "from" and "to" mappings.

  Input:                Output:
  {                     {
    "a": "b",             "from": { "a": "b", "c": "d" },
    "c": "d"              "to":   { "b": "a", "d": "c" }
  }                     }
  '''
  o = { "from": {}, "to": {} }

  for k, v in d.items():
    o["from"][k] = v
    o["to"][v] = k
  
  return o

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
    changeset = { "add": [], "delete": [], "rename": [] }
    path = []

  dirty = False

  ignored_keys = options.get("ignored_keys", [])
  renamed_keys = reversible(options.get("renamed_keys", {}))

  for kind in [config, schema]:
    for key in kind.keys():
      if ignored_keys and key in ignored_keys and kind == config:
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

      # Check for renamed keys. This works from both schema and config.
      # If the we're traversing the schema, the target (rename_to) is the current key,
      # otherwise check if it exists in the rename mapping
      #
      # Then follow the same procedure for the source (rename_from) for config.
      renamed_from = renamed_keys["to"].get(key, None) if kind == schema else key
      renamed_to = renamed_keys["from"].get(key, None) if kind == config else key

      # It is a valid rename if both the renamed_from and renamed_to are present in the config and schema.
      rename = renamed_from in config and renamed_to in schema

      if rename:
        deletion = generate_change(config, renamed_from, path)
        addition = copy.deepcopy(deletion)
        addition = deep_pop(addition, renamed_from, path=path)
        addition = deep_set(addition, renamed_to, config[renamed_from], path)

        change = (deletion, addition)

        if change not in changeset["rename"]:
          changeset["rename"].append(change)
          result = deep_pop(result, renamed_from, path=path)
          result = deep_set(result, renamed_to, config[renamed_from], path=path)
          dirty = True

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
      if file.endswith(".example.json"):
        continue

      if file.endswith(".json"):
        filename = file.split(".")[0] + ".example.json"
        expected_schema_path = os.path.join(directory, filename)
        if os.path.isfile(expected_schema_path):
          files.append((directory, file, options))

  return files

def format_change(change, indent=INDENT, indents=0, delimiter="-", color=None):
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
      line = indent_string(delimiter + " " + line[whitespace_size:], indents, indent)
    else:
      # Indent the string with the delimiter, after slicing off all the extra whitespace at the beginning.
      # This also accounts for the whitespace taken up by the delimiter + 1 extra space, and adds a newline.
      line = "\n" + indent_string(space + line[whitespace_size:], indents, indent)

    line = line.rstrip()

    if color:
      line = colorize(line, color)

    output += line.rstrip()

  return output.strip("\n")

def format_rename_change(change, **kwargs):
  '''
  Formats a rename change, which is a tuple of two changes (from, to) with the given indent.
  '''
  change_from = format_change(change[0], **kwargs)
  change_to   = format_change(change[1], **(kwargs | { "delimiter": " " }))

  change_message = kwargs.get("indent", INDENT) * (kwargs.get("indents", 0) + 2) + "renamed to"

  return "\n".join([change_from, change_message, change_to])

def perform_validation():
  '''
  Performs configuration validation and upserting, printing status along the way.
  '''
  output("Fetching custom config files...")

  for directory, file, options in custom_config_files():
    output(f"- Found custom configuration at {os.path.join(directory, file)}!", indent=1)

    with open(os.path.join(directory, file)) as config_file:
      config = json.load(config_file)

    schema_filename= file.split(".")[0] + ".example.json"
    with open(os.path.join(directory, schema_filename)) as schema_file:
      schema = json.load(schema_file)

    should_overrwrite_config = False

    (changed, result, changes) = upsert_config(config, schema, options)

    should_overrwrite_config = should_overrwrite_config or changed

    if changed:
      output("Adding missing keys and deleting unused configuration options...", indent=2)

      change_options = [
        ("add", "Additions", TermColor.GREEN),
        ("delete", "Deletions (these options are no longer used)", TermColor.RED),
        ("rename", "Renames", TermColor.MAGENTA),
      ]

      for change_type, preamble, color in change_options:
        if len(changes[change_type]) > 0:
          output(preamble, indent=3)

          for change in changes[change_type]:
            if change_type in ["add", "delete"]:
              output(format_change(change, indents=4, color=color))
            if change_type == "rename":
              output(format_rename_change(change, indents=4, color=color))

    if should_overrwrite_config:
      config_path = os.path.join(directory, file)

      output(f"- Creating a backup of {config_path}", indent=4, color=TermColor.YELLOW)

      with open(os.path.join(directory, file + ".bak"), "w") as config_file:
        json.dump(config, config_file, indent=INDENT)

      output(f"- Backup located at {config_path}.bak", indent=4, color=TermColor.YELLOW)
      output(f"- Updating {config_path}...", indent=4, color=TermColor.YELLOW)

      with open(config_path, "w") as config_file:
        json.dump(result, config_file, indent=INDENT)

      output(f"Finished updating {config_path}!", indent=3, color=TermColor.GREEN),
    else:
      output("Configuration is up-to-date.", indent=3, color=TermColor.GREEN)

if __name__ == "__main__":
  perform_validation()
