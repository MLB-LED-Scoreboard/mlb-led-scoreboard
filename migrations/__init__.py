import inspect, json, os, pathlib, shutil
from functools import wraps


BASE_PATH = pathlib.Path(__file__).parent.parent
COLORS_PATH = BASE_PATH / "colors"
COORDINATES_PATH = BASE_PATH / "coordinates"

CHECKPOINT_PATH = pathlib.Path(__file__).parent / "checkpoint.txt"

_configs = None

def fetch_configs():
    global _configs
    if _configs is not None:
        return _configs

    configs = {
        "colors": [],
        "coordinates": [],
        "base": []
    }

    paths = [
        (BASE_PATH, "base"),
        (COLORS_PATH, "colors"),
        (COORDINATES_PATH, "coordinates")
    ]

    for path, key in paths:
        for entry in os.listdir(path):
            if entry.endswith(".json") and "emulator" not in entry:
                configs[key].append(pathlib.Path(path) / entry)

    _configs = configs
    return _configs

class Keypath:
    def __init__(self, keypath):
        self.keypath = keypath
        self.parts = keypath.split('.')

def cast_keypaths(*arg_names):
    """Decorator that casts specific named arguments to Keypath if they are strings."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = inspect.signature(func).bind(*args, **kwargs)
            bound.apply_defaults()

            for name in arg_names:
                if name in bound.arguments and isinstance(bound.arguments[name], str):
                    bound.arguments[name] = Keypath(bound.arguments[name])

            return func(*bound.args, **bound.kwargs)
        return wrapper
    return decorator

class IrreversibleMigration(Exception):
    pass

class Rollback(Exception):
    pass

class ExistingTransaction(Exception):
    pass

class Transaction:
    TEMP_EXTENSION = ".migrate"

    def __init__(self):
        self._backups = []

        self._active = False

    def __enter__(self):
        self.begin()

        return self
    
    def begin(self):
        if self._active:
            return

        print("\tBEGIN TRANSACTION")
        self._active = True
    
    def write(self, path, data):
        if os.path.exists(path):
            if not isinstance(path, pathlib.Path):
                path = pathlib.Path(path)

            print("\t\tSTAGING:", path)

            backup = path.with_suffix(self.TEMP_EXTENSION)

            shutil.copy2(path, backup)
            self._backups.append((path, backup))

        if isinstance(data, (dict, list)):
            data = json.dumps(data, indent=2)

        with open(path, 'w') as f:
            f.write(data)

    def rollback(self):
        for orig, backup in self._backups:
            shutil.move(backup, orig)

    def commit(self):
        for _, backup in self._backups:
            os.remove(backup)

        print("\tCOMMIT TRANSACTION")

    def __exit__(self, exc_type, exc_value, traceback):
        try: 
            if exc_type is None:
                self.commit()
            else:
                raise exc_type(exc_value).with_traceback(traceback)
        except Rollback:
            print("\tROLLBACK TRANSACTION")
            self.rollback()
        except Exception as e:
            print(f"\tROLLBACK TRANSACTION: {e}")
            self.rollback()


class ConfigMigration:
    '''Base class for configuration migrations.'''
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

    @cast_keypaths("keypath")
    def add_key(self, keypath, value, configs):
        '''Add a key to the configuration at the specified keypath.'''
        for content in self.__enumerate_configs(configs):
            parts = keypath.parts
            current = content

            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            if parts[-1] in current:
                raise KeyError(f"Keypath '{keypath.keypath}' already exists.")

            current[parts[-1]] = value

    @cast_keypaths("keypath")
    def remove_key(self, keypath, configs):
        '''Remove a key from the configuration at the specified keypath.'''
        for content in self.__enumerate_configs(configs):
            parts = keypath.parts
            current = content

            for part in parts[:-1]:
                if part not in current:
                    return

                current = current[part]

            del current[parts[-1]]

    @cast_keypaths("keypath_from", "keypath_to")
    def move_key(self, keypath_from, keypath_to, configs):
        '''Move a key from one keypath to another.'''
        for content in self.__enumerate_configs(configs):
            parts_from = keypath_from.parts
            parts_to = keypath_to.parts

            current_from = content
            for part in parts_from[:-1]:
                if part not in current_from:
                    raise KeyError(f"Keypath '{keypath_from.keypath}' does not exist.")

                current_from = current_from[part]

            if parts_from[-1] not in current_from:
                raise KeyError(f"Keypath '{keypath_from.keypath}' does not exist.")

            value = current_from[parts_from[-1]]
            del current_from[parts_from[-1]]

            current_to = content
            for part in parts_to[:-1]:
                if part not in current_to:
                    current_to[part] = {}
                current_to = current_to[part]

            current_to[parts_to[-1]] = value

    @cast_keypaths("keypath")
    def rename_key(self, keypath, new_name, configs):
        '''Rename a key at the specified keypath.'''
        for content in self.__enumerate_configs(configs):
            parts = keypath.parts
            current = content

            for part in parts[:-1]:
                if part not in current:
                    return

                current = current[part]

            if parts[-1] not in current:
                raise KeyError(f"Keypath '{keypath.keypath}' does not exist.")

            value = current[parts[-1]]
            del current[parts[-1]]
            current[new_name] = value

    def __enumerate_configs(self, configs):
        '''
        Iterate over all configuration files in the provided configs.
        Yields the JSON content of each configuration file, and writes back any changes.
        '''
        if not isinstance(configs, list):
            configs = [configs]

        for config_file in configs:
            with open(config_file, 'r') as f:
                content = json.load(f)
            
            yield content

            with open(config_file, 'w') as f:
                json.dump(content, f, indent=2)

class MigrationLoader:
    '''
    Loads migration classes from the migrations directory.
    Each migration file should have a name starting with a timestamp.
    '''
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
