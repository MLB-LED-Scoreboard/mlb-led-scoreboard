from utils.font import FontCache


class Config:
    def __init__(self):
        self.font_cache = FontCache()

    def font(self, font_name):
        return self.font_cache.fetch_font(font_name)
