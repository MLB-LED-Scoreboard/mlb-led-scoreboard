import io, re, unittest
from collections import namedtuple
from unittest import mock

from validate_config import *

class TestValidateConfigMethods(unittest.TestCase):
  
  def test_colorize(self):
    text = "OUTPUT"
    color_code = 99
    
    self.assertEqual(
      colorize(text, color_code),
      f"\033[{color_code}m{text}\033[0m"
    )

  def test_indent_string(self):
    text = "OUTPUT"

    self.assertEqual(indent_string(text, 1, " "), " OUTPUT")
    self.assertEqual(indent_string(text, 2, " "), "  OUTPUT")
    self.assertEqual(indent_string(text, 5, " "), "     OUTPUT")
    self.assertEqual(indent_string(text, 1, "-"), "-OUTPUT")
    self.assertEqual(indent_string(text, 3, "-"), "---OUTPUT")
    self.assertEqual(indent_string(text, 0),      "OUTPUT")
    self.assertEqual(indent_string(text, 1),      "  OUTPUT")
    self.assertEqual(indent_string(text, 5),      "          OUTPUT")

  def test_output(self):
    OutputTest = namedtuple("OutputTest", ["text", "options", "expected"])

    tests = [
      OutputTest("OUTPUT", {}, "OUTPUT\n"),
      OutputTest("OUTPUT", { "indent": 1 }, "  OUTPUT\n"),
      OutputTest("OUTPUT", { "color": TermColor.RED }, "\033[31mOUTPUT\033[0m\n"),
      OutputTest("OUTPUT", { "indent": 2, "color": TermColor.GREEN }, "    \033[32mOUTPUT\033[0m\n"),
      OutputTest("OUTPUT", { "indent": 0, "color": TermColor.YELLOW }, "\033[33mOUTPUT\033[0m\n"),
    ]

    for test in tests:
      with mock.patch('sys.stdout', new=io.StringIO()) as mocked_stdout:
        output(test.text, **test.options)

        self.assertEqual(mocked_stdout.getvalue(), test.expected)

  def test_deep_pop_with_simple_pop(self):
    d = { "simple": "dict" }

    self.assertEqual(
      deep_pop(d, "simple"),
      {}
    )

  def test_deep_pop_with_nested_pop(self):
    d = {
      "deeply": { "nested": "dict" },
      "second": { "nested": "dict" } 
    }

    self.assertEqual(
      deep_pop(d, "nested", path=["deeply"]),
      {
        "deeply": {},
        "second": { "nested": "dict" }
      }
    )

  def test_deep_set_with_simple_set(self):
    d = {}

    self.assertEqual(
      deep_set(d, "simple", "set"),
      { "simple": "set" }
    )
  
  def test_deep_set_with_nested_set(self):
    d = {
      "deeply": { "nested": "dict" },
      "second": {} 
    }

    self.assertEqual(
      deep_set(d, "nested", "dict", path=["second"]),
      {
        "deeply": { "nested": "dict" },
        "second": { "nested": "dict" }
      }
    )

  def test_generate_change(self):
    source = { "three": 4 }
    
    self.assertEqual(
      generate_change(source, "three", ["one", "two"]),
      { "one": { "two": { "three": 4 } } }
    )

  def test_custom_config_files(self):
    with mock.patch("os.listdir") as mocked_listdir:
      files = [
        "config.json",
        "config.example.json",
        "config_INVALID.json"
      ]
      mocked_listdir.return_value = files

      # Checking whether a schema exists for the custom config
      with mock.patch("os.path.isfile") as mocked_isfile:
        mocked_isfile.side_effect = lambda file: "config.example.json" in file

        COORDINATES_IGNORED_KEYS = [
          "font_name",
          "no_hitter",
          "perfect_game",
          "warmup"
        ]
        COLORS_IGNORED_KEYS = [
          "city_connect"
        ]
        self.assertEqual(
          custom_config_files(),
          [
            (ROOT_DIR, "config.json", { "ignored_keys": [] }),
            (COORDINATES_DIR, "config.json", { "ignored_keys": COORDINATES_IGNORED_KEYS }),
            (COLORS_DIR, "config.json", { "ignored_keys": COLORS_IGNORED_KEYS })
          ]
        )

  def test_upsert_config_with_no_diff(self):
    config = { "some": { "dict": { "with": { "deeply": { "nested": "keys" } } } } }
    schema = copy.deepcopy(config)

    (changed, result, changes) = upsert_config(config, schema)

    self.assertFalse(changed)
    self.assertEqual(config, result)
    self.assertEqual(changes, { "add": [], "delete": [] })

  def test_upsert_config_with_simple_addition(self):
    config = {}
    schema = { "should": "be added" }

    (changed, result, changes) = upsert_config(config, schema)

    self.assertTrue(changed)
    self.assertNotEqual(config, result)
    self.assertEqual(result, schema)
    self.assertEqual(
      changes,
      {
        "add": [
          { "should": "be added" }
        ],
        "delete": []
      }
    )
  
  def test_upsert_config_with_simple_deletion(self):
    config = { "should": "be deleted" }
    schema = {}

    (changed, result, changes) = upsert_config(config, schema)

    self.assertTrue(changed)
    self.assertNotEqual(config, result)
    self.assertEqual(result, schema)
    self.assertEqual(
      changes,
      {
        "add": [],
        "delete": [
          { "should": "be deleted" }
        ]
      }
    )

  def test_upsert_config_with_simple_addition_and_deletion(self):
    config = { "needs to be": "deleted" }
    schema = { "should be": "added" }

    (changed, result, changes) = upsert_config(config, schema)

    self.assertTrue(changed)
    self.assertNotEqual(config, result)
    self.assertEqual(result, schema)
    self.assertEqual(
      changes,
      {
        "add": [
          { "should be": "added" }
        ],
        "delete": [
          { "needs to be": "deleted" }
        ]
      }
    )

  def test_upsert_config_with_nested_addition(self):
    config = { "already": { "has": "this one" } }
    schema = { "already": { "has": "this one", "but": "not this one" } }

    (changed, result, changes) = upsert_config(config, schema)

    self.assertTrue(changed)
    self.assertNotEqual(config, result)
    self.assertEqual(result, schema)
    self.assertEqual(
      changes,
      {
        "add": [
          { 
            "already": { "but": "not this one" }
          }
        ],
        "delete": []
      }
    )

  def test_upsert_config_with_nested_deletion(self):
    config = { "already": { "has": "this one", "and": "an extra" } }
    schema = { "already": { "has": "this one" } }

    (changed, result, changes) = upsert_config(config, schema)

    self.assertTrue(changed)
    self.assertNotEqual(config, result)
    self.assertEqual(result, schema)
    self.assertEqual(
      changes,
      {
        "add": [],
        "delete": [
          {
            "already": { "and": "an extra" }
          }
        ]
      }
    )

  def test_upsert_config_with_nested_addition_to_same_key(self):
    config = { "should": { "already": "exist" } }
    schema = { "should": { "already": "exist", "be": "added" } }

    (changed, result, changes) = upsert_config(config, schema)

    self.assertTrue(changed)
    self.assertNotEqual(config, result)
    self.assertEqual(result, schema)
    self.assertEqual(
      changes,
      {
        "add": [
          { "should": { "be": "added" } }
        ],
        "delete": []
      }
    )

  def test_upsert_config_with_nested_deletion_to_same_key(self):
    config = { "should": { "continue": "existing", "be": "deleted" } }
    schema = { "should": { "continue": "existing" } }

    (changed, result, changes) = upsert_config(config, schema)

    self.assertTrue(changed)
    self.assertNotEqual(config, result)
    self.assertEqual(result, schema)
    self.assertEqual(
      changes,
      {
        "add": [],
        "delete": [
          {
            "should": { "be": "deleted" }
          }
        ]
      }
    )

  def test_upsert_config_preserves_dict_values(self):
    config = { "this": { "is true": True } }
    schema = { "this": { "is true": False } }

    (changed, result, changes) = upsert_config(config, schema)

    self.assertFalse(changed)
    self.assertEqual(config, result)
    self.assertEqual(
      changes,
      {
        "add": [],
        "delete": []
      }
    )

  def test_upsert_config_preserves_non_dict_values(self):
    config = { "this": True }
    schema = { "this": { "is true": False } }

    (changed, result, changes) = upsert_config(config, schema)

    self.assertFalse(changed)
    self.assertEqual(config, result)
    self.assertEqual(
      changes,
      {
        "add": [],
        "delete": []
      }
    )

  def test_upsert_config_with_ignored_keys_in_config(self):
    '''
    Keys that are extra in the config but not in the schema are ignored if they are in the ignored_keys list.
    '''
    config = { "this": True, "that": False }
    schema = { "this": True }

    options = { "ignored_keys": ["that"] }

    (changed, result, changes) = upsert_config(config, schema, options)

    self.assertFalse(changed)
    self.assertEqual(config, result)
    self.assertEqual(
      changes,
      {
        "add": [],
        "delete": []
      }
    )

  def test_upsert_config_with_ignored_keys_with_subkeys_in_config(self):
    '''
    Keys in the ignore list ignore all subkeys.
    '''
    config = { "this": True, "that": { "those": False } }
    schema = { "this": True }

    options = { "ignored_keys": ["that"] }

    (changed, result, changes) = upsert_config(config, schema, options)

    self.assertFalse(changed)
    self.assertEqual(config, result)
    self.assertEqual(
      changes,
      {
        "add": [],
        "delete": []
      }
    )

  def test_upsert_config_with_ignored_keys_as_extra_subkey_in_config(self):
    '''
    Keys in the ignore list as a subkey are not ignored.
    '''
    config = { "this": True, "those": { "that": False } }
    schema = { "this": True }

    options = { "ignored_keys": ["that"] }

    (changed, result, changes) = upsert_config(config, schema, options)

    self.assertTrue(changed)
    self.assertNotEqual(config, result)
    self.assertEqual(result, schema)
    self.assertEqual(
      changes,
      {
        "add": [],
        "delete": [
          { "those": { "that": False } }
        ]
      }
    )

  def test_upsert_config_with_ignored_keys_in_schema(self):
    '''
    Keys that are extra in the schema but not in the config are ALWAYS placed in the add changeset.
    '''
    config = { "this": True }
    schema = { "this": True, "that": False }

    options = { "ignored_keys": ["that"] }

    (changed, result, changes) = upsert_config(config, schema, options)

    self.assertTrue(changed)
    self.assertNotEqual(config, result)
    self.assertEqual(result, schema)
    self.assertEqual(
      changes,
      {
        "add": [
          { "that": False }
        ],
        "delete": []
      }
    )

  def test_upsert_config_with_ignored_keys_with_subkeys_in_schema(self):
    '''
    Keys in the ignore list still add all subkeys.
    '''
    config = { "this": True }
    schema = { "this": True, "that": { "those": False } }

    options = { "ignored_keys": ["that"] }

    (changed, result, changes) = upsert_config(config, schema, options)

    self.assertTrue(changed)
    self.assertNotEqual(config, result)
    self.assertEqual(result, schema)
    self.assertEqual(
      changes,
      {
        "add": [
          { "that": { "those": False } }
        ],
        "delete": []
      }
    )

  def test_format_change(self):
    change = { "some": { "arbitrary": "change" } }

    self.assertEqual(
      format_change(change),
'''
- "some": {
    "arbitrary": "change"
  }
'''.strip("\n")
    )

  def test_format_change_with_small_indent(self):
    change = { "some": { "arbitrary": "change" } }

    self.assertEqual(
      format_change(change, indent = " "),
'''
- "some": {
   "arbitrary": "change"
  }
'''.strip("\n")
    )

  def test_format_change_with_large_indent(self):
    change = { "some": { "arbitrary": "change" } }

    self.assertEqual(
      format_change(change, indent = "  " * 3),
'''
- "some": {
        "arbitrary": "change"
  }
'''.strip("\n")
    )

  def test_format_change_with_more_indents(self):
    change = { "some": { "arbitrary": "change" } }

    self.assertEqual(
      format_change(change, indents=2),
'''
    - "some": {
        "arbitrary": "change"
      }
'''.strip("\n")
    )

  def test_format_change_with_different_delimiter(self):
    change = { "some": { "arbitrary": "change" } }

    self.assertEqual(
      format_change(change, delimiter="*"),
'''
* "some": {
    "arbitrary": "change"
  }
'''.strip("\n")
    )

  def test_format_change_with_color(self):
    change = { "some": { "arbitrary": "change" } }

    self.assertRegex(
      format_change(change, color=TermColor.RED),
      re.compile(fr'\033\[{TermColor.RED}.+\033\[0m')
    )


class TestPerformValidation(unittest.TestCase):

  def setUp(self):
    self.config_fixture_path = os.path.join("tests", "fixtures", "config.json")
    with open(self.config_fixture_path) as config_file:
      self.config = json.load(config_file)

  def tearDown(self):
    with open(self.config_fixture_path, "w") as config_file:
      self.config = json.dump(self.config, config_file, indent="  ")

  def test_perform_validation_end_to_end(self):
    with mock.patch("validate_config.custom_config_files") as mocked_custom_files:
      mocked_custom_files.return_value = [(os.path.join("tests", "fixtures"), "config.json", {})]

      with mock.patch("validate_config.colorize") as mocked_color:
        mocked_color.side_effect = lambda text, _: text

        with mock.patch('sys.stdout', new=io.StringIO()) as mocked_stdout:

          perform_validation()

          expected_output = \
f'''
Fetching custom config files...
  - Found custom configuration at {self.config_fixture_path}!
    Adding missing keys and deleting unused configuration options...
      Additions
        - "test_config": {{
            "easter_eggs": true
          }}
      Deletions (these options are no longer used):
        - "test_config": {{
            "deprecated_option": null
          }}
        - Creating a backup of {self.config_fixture_path}
        - Backup located at {self.config_fixture_path}.bak
        - Updating {self.config_fixture_path}...
      Finished updating {self.config_fixture_path}!
'''.lstrip("\n")

          # Remove the maxDiff limit to see the full output in case of failure
          self.maxDiff = None
          self.assertEqual(
            mocked_stdout.getvalue(),
            expected_output
          )

        with open(self.config_fixture_path) as config_file:
          new_config = json.load(config_file)
          # Spot check an insertion
          self.assertTrue(new_config["test_config"]["easter_eggs"])
          # Spot check a deletion
          self.assertFalse("deprecated_option" in new_config["test_config"])
          # Make sure we haven't killed an overwritten option
          self.assertEqual(
            new_config["preferred"],
            {
              "teams": ["Braves"],
              "divisions": ["AL Central", "AL Wild Card"]
            }
          )


if __name__ == "__main__":
  unittest.main()
