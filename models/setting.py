import json
from enum import StrEnum
from dataclasses import dataclass

class SettingType(StrEnum):
    """
    Supported setting types for configuration values.
    
    JSON is a catch-all type for anything that does not match a primitive type (for instance, lists).
    """
    INTEGER = "integer"
    STRING = "string"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"

@dataclass
class Setting:
    id: int
    key: str
    value: str
    type: SettingType
    namespace: str
    schema_id: int
    is_default: bool = True

    @staticmethod
    def from_row(row):
        return Setting(
            id=row["id"],
            key=row["key"],
            value=Setting.cast_value(SettingType(row["type"]), row["value"]),
            type=SettingType(row["type"]),
            namespace=row["namespace"],
            schema_id=row["schema_id"],
            is_default=bool(row["is_default"]) if "is_default" in row.keys() else False
        )

    @staticmethod
    def cast_value(type, value):
        if type == SettingType.INTEGER:
            return int(value)
        if type == SettingType.FLOAT:
            return float(value)
        if type == SettingType.BOOLEAN:
            return value in ("1", "true", "True")
        if type == SettingType.JSON:
            return json.loads(value)
        return value

    @staticmethod
    def infer_type(value):
        if isinstance(value, bool):
            return SettingType.BOOLEAN
        elif isinstance(value, int):
            return SettingType.INTEGER
        elif isinstance(value, float):
            return SettingType.FLOAT
        elif isinstance(value, str):
            return SettingType.STRING
        else:
            return SettingType.JSON

    def to_dict(self):
        """Convert Setting to a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "type": self.type.value,
            "namespace": self.namespace,
            "schema_id": self.schema_id,
            "is_default": self.is_default
        }