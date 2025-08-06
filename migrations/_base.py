import json, os, pathlib


BASE_PATH = pathlib.Path(__file__).parent.parent
COLORS_PATH = BASE_PATH / "colors"
COORDINATES_PATH = BASE_PATH / "coordinates"

_configs = None

def fetch_configs():
    global _configs
    if _configs is not None:
        return _configs

    configs = {
        "colors": set(),
        "coordinates": set(),
        "base": set()
    }

    paths = [
        (BASE_PATH, "base"),
        (COLORS_PATH, "colors"),
        (COORDINATES_PATH, "coordinates")
    ]

    for path, key in paths:
        for entry in os.listdir(path):
            if entry.endswith(".json"):
                configs[key].add(pathlib.Path(path) / entry)

    _configs = configs
    return _configs

class IrreversibleMigration(Exception):
    pass

class ConfigMigration:
    def __init__(self):
        self.configs = fetch_configs()

    def up(self):
        '''
        Performs a data migration for a configuration object.
        '''
        raise NotImplementedError("ConfigMigration subclasses must implement up()")

    def down(self):
        '''
        Reverse a migration. 

        Raises IrreversibleMigration if migration cannot be reversed.
        Default implementation assumes an irreversible migration.
        '''
        raise IrreversibleMigration()

class MigrationLoader:
    @staticmethod
    def load_migrations():
        migrations = []

        for path in sorted((pathlib.Path(__file__).parent).glob("*.py")):
            if path.name[0].isdigit():
                migration_module = getattr(__import__("migrations." + path.stem), path.stem)
                version, migration_class_name = path.stem.split('_', 1)
                migration_class = getattr(migration_module, migration_class_name.replace('_', ''))

                migrations.append((version, migration_class))

        return migrations
