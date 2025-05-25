import json, os, unittest

class TestColorSchema(unittest.TestCase):

    ERROR_LIMIT = 10
    REQUIRED_KEYS = ["home", "text", "accent"]
    CITY_CONNECT_KEY = "city_connect"

    def setUp(self):
        with open(os.path.join("colors", "teams.example.json")) as f:
            self.team_colors = json.load(f)

    def _validate_required_keys(self, data, context):
        errors = []

        for key in self.REQUIRED_KEYS:
            if key not in data:
                errors.append(f"Expected {context}.{key} to exist")

        return errors

    def _msg(self, errors):
        displayed = errors[:self.ERROR_LIMIT]
        msg = "Schema contains errors:\n\t" + "\n\t".join(displayed)

        if len(errors) > self.ERROR_LIMIT:
            msg += f"\n\n\t... and {len(errors) - self.ERROR_LIMIT} more"

        return msg
    
    def test_team_base_schema(self):
        errors = []
        
        for team, values in self.team_colors.items():
            errors.extend(self._validate_required_keys(values, team))

        if errors:
            self.fail(self._msg(errors))

    def test_team_city_connect_schema(self):
        errors = []
        
        for team, values in self.team_colors.items():
            if self.CITY_CONNECT_KEY not in values:
                continue
            
            values = values[self.CITY_CONNECT_KEY]
            context = f"{team}.{self.CITY_CONNECT_KEY}"

            errors.extend(self._validate_required_keys(values, context))

        if errors:
            self.fail(self._msg(errors))
