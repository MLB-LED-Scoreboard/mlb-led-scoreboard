try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics


class Color:
    def __init__(self, color_json):
        self.json = color_json

    def color(self, keypath):
        try:
            d = self.__find_at_keypath(keypath)
        except KeyError as e:
            raise e
        return d

    def graphics_color(self, keypath):
        color = self.color(keypath)
        if not color:
            color = self.color("default.text")
        return graphics.Color(color["r"], color["g"], color["b"])

    def __find_at_keypath(self, keypath):
        keys = keypath.split(".")
        rv = self.json
        for key in keys:
            rv = rv[key]
        return rv
