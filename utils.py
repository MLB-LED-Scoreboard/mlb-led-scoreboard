from collections.abc import Mapping


def center_text_position(text, center_pos, font_width):
    return abs(center_pos - ((len(text) * font_width) // 2))


def split_string(string, num_chars):
    return [(string[i : i + num_chars]).strip() for i in range(0, len(string), num_chars)]  # noqa: E203


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
