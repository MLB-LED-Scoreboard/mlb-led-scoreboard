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

        match plugin_name:
            # TODO easiest work around for existing behavior
            case "news" | "standings":
                plugin_colors = self
            case _:
                plugin = self.json.get("plugins", {}).get(plugin_name, {})
                json = {plugin_name: plugin}
                json["default"] = self.json["default"]
                plugin_colors = Color(json)

        return plugin_colors
