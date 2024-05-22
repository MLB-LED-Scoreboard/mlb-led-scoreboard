import argparse
from collections.abc import Mapping

from RGBMatrixDriver import RGBMatrixArguments

import debug


def center_text_position(text, center_pos, font_width):
    return abs(center_pos - ((len(text) * font_width) // 2))


def split_string(string, num_chars):
    return [(string[i : i + num_chars]).strip() for i in range(0, len(string), num_chars)]  # noqa: E203

def scoreboard_args():
    sb_parser = RGBMatrixArguments()
    sb_parser.add_argument(
        "--config",
        action="store",
        help="Base file name for config file. Can use relative path, e.g. config/rockies.config",
        default="config",
        type=str,
    )

    return sb_parser.parse_args()

def deep_update(source, overrides):
    """Update a nested dictionary or similar mapping.
    Modify ``source`` in place.
    """
    for key, value in list(overrides.items()):
        if isinstance(value, Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source
