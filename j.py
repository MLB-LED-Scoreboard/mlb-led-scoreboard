# from jsonschema import validate
import json

# with open('colors/scoreboard.schema.json') as f:
#     schema = json.load(f)

# with open('colors/scoreboard.example.json') as f:
#     example = json.load(f)

# # breakpoint()

# validate(instance=example, schema=schema)

with open("colors/scoreboard.json.example") as f:
    teams = json.load(f)

default_colors = teams["default"]["text"]

output = {}

for k, v in teams.items():
    output[k] = v

    if "text" in v:
        continue

    output[k]["text"] = default_colors

with open("colors/scoreboard.json.example", "w") as f:
    json.dump(output, f, indent=2)
