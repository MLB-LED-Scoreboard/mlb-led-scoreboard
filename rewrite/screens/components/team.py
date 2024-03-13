from driver import graphics

from utils.graphics import DrawRect


class TeamBanner:
    def __init__(self, kind, screen):
        self.kind = kind

        # Can reach into the screen to access config for that screen
        self.screen = screen

        # breakpoint()
        self.team_name = self.game.home_name() if kind == "home" else self.game.away_name()
        self.team_abbreviation = self.game.home_abbreviation() if kind == "home" else self.game.away_abbreviation()

        self.__load_colors()

    def render(self):
        self.__render_background()
        self.__render_accents()
        self.__render_team_name()
        self.__render_score()

    def __render_background(self):
        coords = self.layout.coords(f"teams.background.{self.kind}")

        DrawRect(self.canvas, coords.x, coords.y, coords.width, coords.height, self.bg_color)

    def __render_accents(self):
        coords = self.layout.coords(f"teams.accent.{self.kind}")

        DrawRect(self.canvas, coords.x, coords.y, coords.width, coords.height, self.accent_color)

    def __render_score(self):
        pass

    def __render_team_name(self):
        keypath = f"teams.name.{self.kind}"

        coords = self.layout.coords(keypath)
        font, font_size = self.layout.font_for(keypath)

        # TODO: Trunc on long RHE
        if self.config.full_team_names:
            text = "{:13s}".format(self.team_name)
        else:
            text = "{:3s}".format(self.team_abbreviation.upper())

        graphics.DrawText(self.canvas, font, coords.x, coords.y, self.text_color, text)

    def __load_colors(self):
        team_key = self.team_abbreviation.lower()

        self.bg_color = self.__color(f"{team_key}.home", "default.home")
        self.text_color = self.__color(f"{team_key}.text", "default.text")
        self.accent_color = self.__color(f"{team_key}.accent", "default.accent")

    def __color(self, keypath, default_keypath):
        color = self.colors.team_graphics_color(keypath, default=False)

        if color:
            return color

        return self.colors.team_graphics_color(default_keypath)

    @property
    def game(self):
        return self.screen.game

    @property
    def canvas(self):
        return self.screen.canvas

    @property
    def config(self):
        return self.screen.config

    @property
    def colors(self):
        return self.screen.colors

    @property
    def layout(self):
        return self.screen.layout
