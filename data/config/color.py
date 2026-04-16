from driver import graphics


class Color:
    def __init__(self, color_json):
        self.json = color_json

    def color(self, keypath):
        return self.__find_at_keypath(keypath)

    def graphics_color(self, keypath):
        color = self.color(keypath)
        return graphics.Color(color["r"], color["g"], color["b"])

    def __find_at_keypath(self, keypath):
        keys = keypath.split(".")
        rv = self.json
        for key in keys:
            rv = rv[key]
        return rv

    def __eq__(self, other):
        return isinstance(other, Color) and self.json == other.json

    def for_plugin(self, plugin_name: str) -> "Color":

        plugins = self.json.get("plugins", {})
        if plugin_name in ("news", "standings"):
            # legacy workaround
            plugins = self.json

        plugin = plugins.get(plugin_name, {})
        json = {plugin_name: plugin}
        json["default"] = self.json["default"]
        return Color(json)
