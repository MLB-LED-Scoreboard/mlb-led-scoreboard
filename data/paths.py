from pathlib import Path

"""Centralized path constants for locating project directories at runtime."""
CURRENT_DIRECTORY     = Path.cwd()
ROOT_DIRECTORY        = (Path(__file__) / ".." / "..").resolve()
COORDINATES_DIRECTORY = ROOT_DIRECTORY / "coordinates"
COLORS_DIRECTORY      = ROOT_DIRECTORY / "colors"
