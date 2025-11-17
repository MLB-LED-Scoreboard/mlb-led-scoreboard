import json, os

from db.connection import ConnectionManager

from models.schema import Schema, SchemaType
from models.setting import Setting, SettingType

class SettingsRepository:
    def __init__(self, cm: ConnectionManager):
        self.cm = cm

    def close(self):
        self.cm.close()

    def schemas(self) -> list[Schema]:
        """Get all schemas."""
        rows = self.cm.query("SELECT * FROM schemas")

        return [Schema.from_row(r) for r in rows]
    
    def fetch_schema_by_path(self, path: str) -> Schema | None:
        """Retrieves a schema by path."""
        directory, filename = os.path.split(path)
        rows = self.cm.query("SELECT * FROM schemas WHERE directory = ? AND filename = ?", (directory, filename,))

        if rows:
            return Schema.from_row(rows[0])
    
    def all_settings(self):
        """Get all settings for all configuration schemas."""
        settings = {}

        for schema in self.schemas():
            settings[schema.id] = self.fetch_schema_settings(schema.id)

        return settings

    def fetch_schema_settings(self, schema_id: int) -> list[Setting]:
        """Get all settings for a schema."""
        rows = self.cm.query("SELECT * FROM settings WHERE schema_id = ?", (schema_id,))

        return [Setting.from_row(r) for r in rows]

    def create_schema_setting(
        self,
        schema_id: int,
        namespace: str | None,
        key: str,
        value: any,
        type: SettingType,
        is_default: bool = False
    ) -> Setting:
        """Create a new setting for a schema. Returns the created setting if successful."""
        sql = """
        INSERT INTO settings (schema_id, namespace, key, value, type, is_default)
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING *
        """

        rows = self.cm.query(
            sql,
            (
                schema_id,
                namespace,
                key,
                json.dumps(value),
                type,
                is_default,
            )
        )

        return Setting.from_row(rows[0])

    def fetch_schema_setting(
        self,
        schema_id: int,
        namespace: str | None,
        key: str
    ) -> Setting | None:
        """Fetch a specific setting for a schema."""
        sql = "SELECT * FROM settings WHERE schema_id = ? AND namespace = ? AND key = ?"

        rows = self.cm.query(
            sql,
            (
                schema_id,
                namespace,
                key,
            ))

        if rows:
            return Setting.from_row(rows[0])
        return None

    def import_schema_from_file(self, kind: SchemaType, path: str):
        """
        Creates a new schema associated with the path. The file must exist and contain valid JSON.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File does not exist at {path}")

        with open(path, "r") as f:
            schema_json = json.load(f)

        schema = self.__find_or_create_schema(kind, path)

        self.__delete_schema_settings(schema)
        self.__import_schema(schema, None, schema_json)

    def __find_or_create_schema(self, kind: SchemaType, path: str) -> Schema:
        schema = self.fetch_schema_by_path(path)

        if schema:
            return schema
        
        directory, filename = os.path.split(path)
        rows = self.cm.query("INSERT INTO schemas (directory, filename, type) VALUES (?, ?, ?) RETURNING *", (directory, filename, kind,))

        if rows:
            return Schema.from_row(rows[0])

    def __import_schema(self, schema: Schema, namespace: str | None, data: dict[any]):
        """Recursively traverse the data and create settings appropriately for the schema."""
        for key, value in data.items():
            if isinstance(value, dict):
                new_namespace = key if namespace is None else f"{namespace}.{key}"

                self.__import_schema(schema, new_namespace, value)
            else:
                self.create_schema_setting(
                    schema.id, 
                    namespace,
                    key,
                    value,
                    Setting.infer_type(value),
                    is_default=True
                )

    def __delete_schema_settings(self, schema: Schema):
        """Delete all settings for a schema, keeping the schema itself."""
        self.cm.query("DELETE FROM settings WHERE schema_id = ?", (schema.id,))
