import argparse, re, pathlib, time

from migrations._base import MigrationLoader

CHECKPOINT_FILE = 'migrations/checkpoint.txt'


class CLICommand:
    def execute(self):
        raise NotImplementedError("Subclasses should implement this method.")

class Generate(CLICommand):
    TEMPLATE = '''\
from migrations._base import ConfigMigration


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


class Up(CLICommand):
    def execute(self, step):
        print("Executing migrations...")

        migrations = MigrationLoader.load_migrations()
        if len(migrations) == 0:
            print("No migrations to execute.")
            return

        for version, migration_class in migrations:
            print("=" * 80)
            print(f"MIGRATE {version} << {migration_class.__name__} >>")

            migration = migration_class()

            if self.last_checkpoint() < version:
                migration.up()
                self.create_checkpoint(version)

                step -= 1
            else:
                print("\t-- Up to date, skipping migration. --")

            if step == 0:
                break

        print("=" * 80)
        print("Done.")

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

class Down(CLICommand):
    class RollbackFailed(Exception):
        pass

    def execute(self, step):
        print("Rolling back migrations...")

        migrations = MigrationLoader.load_migrations()
        if len(migrations) == 0:
            print("No migrations to roll back.")
            return

        for version, migration_class in migrations[::-1]:
            print("=" * 80)
            print(f"ROLLBACK {version} << {migration_class.__name__} >>")

            migration = migration_class()

            if self.last_checkpoint() == version:
                migration.down()
                self.create_checkpoint()

                step -= 1
            else:
                print("\t-- Migration not yet executed, skipping migration. --")

            if step == 0:
                break

        print("=" * 80)
        print("Done.")
        

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

def positive_int(value):
    ivalue = int(value)

    if ivalue < 1:
        raise argparse.ArgumentTypeError("must be at least 1")

    return ivalue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data migration manager for mlb-led-scoreboard configuration objects.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # "generate" command
    generate_parser = subparsers.add_parser('generate', help='Generate a new migration file')
    generate_parser.add_argument('migration_name', type=str, help='Name of the migration')

    # "up" command
    up_parser = subparsers.add_parser('up', help='Run migrations')
    up_parser.add_argument(
        '--step',
        type=positive_int,
        default=999_999,
        help='Number of migrations to process (defaults to all migrations)'
    )

    # "down" command
    down_parser = subparsers.add_parser('down', help='Roll back migrations')
    down_parser.add_argument(
        '--step',
        type=positive_int,
        default=1,
        help='Number of migrations to process (defaults to most recent)'
    )

    args = parser.parse_args()

    if args.command == 'generate':
        command = Generate(args.migration_name)
        command.execute()

    if args.command == "up":
        command = Up()
        command.execute(args.step)

    if args.command == "down":
        command = Down()
        command.execute(args.step)
