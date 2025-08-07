import argparse

from migrations.commands.generate import Generate
from migrations.commands.up import Up
from migrations.commands.down import Down


def positive_int(value):
    """Custom argparse type for positive integers."""
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
