import json, os, re, unittest

from validate_config import upsert_config

class TestValidateCoordinateExamples(unittest.TestCase):

    COORDINATES_DIR = "coordinates"
    REFERENCE_FILENAME = "coordinates.json.example"
    REFERENCE_PATH = os.path.join(COORDINATES_DIR, REFERENCE_FILENAME)
    SCHEMA_PATHS = [path for path in os.listdir(COORDINATES_DIR) if re.match(r'w[0-9]+h[0-9]+\.json\.example', path)]

    def __test_coordinate_schema(self, schema_path):
        reference = self.__load_schema(self.REFERENCE_PATH)
        schema = self.__load_schema(schema_path)

        (changed, _result, changes) = upsert_config(schema, reference)

        self.assertEqual(changes, { "add": [], "delete": []})
        self.assertFalse(changed)

    def __load_schema(self, schema_path):
        with open(schema_path) as schema_file:
            schema = json.load(schema_file)

        return schema
    
    def test_all_schemas(self):
        '''
        This tests ALL schemas matching the regex /w[0-9]+h[0-9]+\.json\.example/ in the coordinates directory.

        By doing it this way, if someone adds support for a new matrix size, the tests will automatically run for it.
        '''

        for path in self.SCHEMA_PATHS:
            with self.subTest():
                schema_path = os.path.join(self.COORDINATES_DIR, path)
                self.__test_coordinate_schema(schema_path)
