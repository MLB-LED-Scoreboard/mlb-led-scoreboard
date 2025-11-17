from enum import StrEnum
from dataclasses import dataclass

class SchemaType(StrEnum):
    """Supported schema types for configuration values."""
    GLOBAL = "global"
    COORDINATES = "coordinates"
    COLORS = "colors"

@dataclass
class Schema:
    id: int
    directory: str
    filename: str
    type: SchemaType

    @staticmethod
    def from_row(row):
        return Schema(
            id=row["id"],
            directory=row["directory"],
            filename=row["filename"],
            type=SchemaType(row["type"])
        )

    def to_dict(self):
        """Convert Schema to a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "directory": self.directory,
            "filename": self.filename,
            "type": self.type.value
        }
