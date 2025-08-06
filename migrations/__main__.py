import argparse, re, pathlib, time

from migrations._base import MigrationLoader

CHECKPOINT_FILE = 'migrations/checkpoint.txt'


class CLICommand:
    def execute(self):
        raise NotImplementedError("Subclasses should implement this method.")

class Generate(CLICommand):
    TEMPLATE = '''\
from migrations._base import ConfigMigration

import json


class {}(ConfigMigration):
    def up(self):
        raise NotImplementedError("Migration logic not implemented.")

    def down(self):
        super().down()
'''

    def __init__(self, migration_name):
        self.__validate_migration_name(migration_name)
        self.migration_name = migration_name

    def execute(self):
        print(f"Generating migration '{self.migration_name}'.")

        ts = int(time.time())
        filename = f"{ts}_{self.migration_name}.py"
        migration_path = pathlib.Path(__file__).parent / filename

        with open(migration_path, 'w') as f:
            f.write(self.TEMPLATE.format(self.migration_name, ts))

        print(f"Migration '{self.migration_name}' generated successfully.")

    def __validate_migration_name(self, name):
        if not name.isidentifier():
            raise ValueError("Migration name must be a valid Python identifier.")


class Execute(CLICommand):
    def execute(self):
        print("Executing migrations...")

        migrations = MigrationLoader.load_migrations()
        for version, migration_class in migrations:
            print("=" * 80)
            print(f"MIGRATE {migration_class.__name__} - Version: {version}")
            print("=" * 80)

            migration = migration_class()

            if self.last_checkpoint() < version:
                migration.up()
                self.create_checkpoint(version)
                print("Done.")
            else:
                print("Up to date, skipping migration.")

    def create_checkpoint(self, ts):
        with open(CHECKPOINT_FILE, 'a') as f:
            f.write(f"{ts}\n")

    def last_checkpoint(self):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                checkpoints = f.readlines()
                return checkpoints[-1].strip()
        except (FileNotFoundError, IndexError):
            return "0"

class Rollback(CLICommand):
    class RollbackFailed(Exception):
        pass

    def execute(self):
        print("Rolling back most recent migration...")

        migrations = MigrationLoader.load_migrations()
        for version, migration_class in migrations[::-1]:
            print("=" * 80)
            print(f"ROLLBACK {migration_class.__name__} - Version: {version}")
            print("=" * 80)

            migration = migration_class()

            if self.last_checkpoint() == version:
                migration.down()
                self.create_checkpoint()
                print("Done.")

                return
            else:
                print("Migration not yet executed, skipping migration.")

        print("No migrations to roll back.")

    def create_checkpoint(self):
        with open(CHECKPOINT_FILE, 'r+') as f:
            checkpoints = f.readlines()
            f.seek(0)
            f.writelines(checkpoints[:-1])
            f.truncate()

    def last_checkpoint(self):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                checkpoints = f.readlines()
                return checkpoints[-1].strip()
        except (FileNotFoundError, IndexError):
            return "0"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data migration manager for mlb-led-scoreboard configuration objects.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # "generate" command
    generate_parser = subparsers.add_parser('generate', help='Generate a new migration file')
    generate_parser.add_argument('migration_name', type=str, help='Name of the migration')

    # "migrate" command
    migrate_parser = subparsers.add_parser('execute', help='Run migrations')

    # "rollback" command
    rollback_parser = subparsers.add_parser('rollback', help='Roll back the last migration (if possible)')

    args = parser.parse_args()

    if args.command == 'generate':
        command = Generate(args.migration_name)
        command.execute()

    if args.command == "execute":
        command = Execute()
        command.execute()

    if args.command == "rollback":
        command = Rollback()
        command.execute()
