# Run with python -m db.seed

from db.connection import ConnectionManager, SETTING_DATABASE_PATH
from models.settings_repository import SettingsRepository
from models.schema import SchemaType

from pathlib import Path

SEEDS_PATH = Path(__file__).parent / "seeds"

manager = ConnectionManager(SETTING_DATABASE_PATH)
settings = SettingsRepository(manager)

for path in SEEDS_PATH.rglob("*.json"):
    seed_type = path.parent.name

    settings.import_schema_from_file(seed_type, path)

settings.close()
