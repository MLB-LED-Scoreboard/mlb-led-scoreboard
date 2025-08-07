import pathlib, time

from migrations.commands import CLICommand


MIGRATION_TEMPLATE = '''\
from migrations import ConfigMigration


class {}(ConfigMigration):
    def up(self):
        raise NotImplementedError("Migration logic not implemented.")

    def down(self):
        super().down()
'''

class Generate(CLICommand):
    def __init__(self, migration_name):
        self.__validate_migration_name(migration_name)
        self.migration_name = migration_name

    def execute(self):
        print(f"Generating migration '{self.migration_name}'.")

        ts = int(time.time())
        filename = f"{ts}_{self.migration_name}.py"
        migration_path = pathlib.Path(__file__).parent.parent / filename

        with open(migration_path, 'w') as f:
            f.write(MIGRATION_TEMPLATE.format(self.migration_name, ts))

        print(f"Migration '{self.migration_name}' generated successfully.")

    def __validate_migration_name(self, name):
        if not name.isidentifier():
            raise ValueError("Migration name must be a valid Python identifier.")
