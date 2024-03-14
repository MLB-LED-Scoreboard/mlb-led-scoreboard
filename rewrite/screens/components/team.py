from driver import graphics

from data.team import TeamType

from utils.graphics import DrawRect

from collections import namedtuple


class TeamBanner:
    def __init__(self, kind, screen):
        self.kind = kind

        # Can reach into the screen to access config for that screen
        self.screen = screen

        self.team_name = self.game.home_name() if kind == TeamType.HOME else self.game.away_name()
        self.team_abbreviation = (
            self.game.home_abbreviation() if kind == TeamType.HOME else self.game.away_abbreviation()
        )

        self.__load_colors()

        # Constructor to build scoreline objects for both teams
        self._scoreline = namedtuple("Scoreline", ("runs", "hits", "errors"))

    def render(self):
        self.__render_background()
        self.__render_accents()
        self.__render_team_name()
        self.__render_scoreline()

    def __render_background(self):
        coords = self.layout.coords(f"teams.background.{self.kind}")

        DrawRect(self.canvas, coords.x, coords.y, coords.width, coords.height, self.bg_color)

    def __render_accents(self):
        coords = self.layout.coords(f"teams.accent.{self.kind}")

        DrawRect(self.canvas, coords.x, coords.y, coords.width, coords.height, self.accent_color)

    def __render_team_name(self):
        keypath = f"teams.name.{self.kind}"

        coords = self.layout.coords(keypath)
        font, font_size = self.layout.font_for(keypath)
        text = self.__team_name()

        graphics.DrawText(self.canvas, font, coords.x, coords.y, self.text_color, text)

    def __render_scoreline(self):
        coords = self.layout.coords(f"teams.runs.{self.kind}")
        font, font_size = self.layout.font_for(f"teams.runs.{self.kind}")

        for c, pos in self.__calculate_scoreline_positions(coords.x, font_size):
            graphics.DrawText(self.canvas, font, pos, coords.y, self.text_color, c)

    def __calculate_scoreline_positions(self, start, font_size):
        """
        Returns an array of tuples containing a character and position (c, p) for values in the scoreline.

        Character tuples will be arranged in format runs-hits-errors (RHE).
        Each value is placed into a column with its value right-justified if required.
        This class is responsible for rendering a single team's banner, but guarantees the column will align with the opposite team's columns.

        Order of the characters in the returned array is not guaranteed. They should be sorted on position if required.
        """
        scoreline_options = self.layout.coords("teams.runs.runs_hits_errors")

        if scoreline_options.show:
            # Assumes scoreline constructor will have fields in R, H, E order
            home = [str(value) for value in self.scoreline[TeamType.HOME]]
            away = [str(value) for value in self.scoreline[TeamType.AWAY]]
        else:
            home = [str(self.scoreline[TeamType.HOME].runs)]
            away = [str(self.scoreline[TeamType.AWAY].runs)]

        pairs = list(zip(home, away))
        positions = []

        # Need to manage the position pointer and iterator on our own.
        x = start
        i = 0

        # Characters are drawn right to left
        for pair in pairs[::-1]:
            hv, av = pair

            # Ensure the algorithm operates on strings of equal length, otherwise add padding left.
            hv = hv.rjust(max(len(hv), len(av)), " ")
            av = av.rjust(max(len(hv), len(av)), " ")

            target = hv if self.kind == TeamType.HOME else av

            # Continue to draw right to left
            for c in target[::-1]:
                # If compression is set, shift pointer back to the left
                if i > 0 and scoreline_options.compress_digits:
                    x += 1

                # Append a pair (character, position) if not blank
                if c != " ":
                    positions.append((c, x - font_size[0] * (i + 1)))

                i += 1

            # Shift position pointer to the right by the spacing setting.
            # BUG: Why is this a setting but is possibly off-by-one?
            x -= scoreline_options.spacing - 1

        return positions

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

    def __team_name(self):
        """
        Returns either the team's actual name or the abbreviated name based on several criteria.

        Long names are returned if:
            1. `full_team_names` config setting is enabled
            2. Matrix width is greater than 32px
            3. `short_team_names_for_runs_hits` config setting is
                a. Disabled
                    -OR-
                b. Enabled, but any team's runs and hits is less than 9 (two digits)

        Otherwise, short names are returned.
        """
        short_name = "{:3s}".format(self.team_abbreviation.upper())
        long_name = "{:13s}".format(self.team_name)

        enabled = self.config.full_team_names
        matrix_size_supported = self.canvas.width > 32
        overflow_prevention_enabled = self.config.short_team_names_for_runs_hits

        if not enabled or not matrix_size_supported:
            return short_name

        if not overflow_prevention_enabled:
            return long_name

        # Either team can possibly overflow
        for kind in [TeamType.HOME, TeamType.AWAY]:
            if self.scoreline[kind].hits > 9 or self.scoreline[kind].runs > 9:
                return short_name

        return long_name

    @property
    def scoreline(self):
        return {
            TeamType.HOME: self._scoreline(self.game.home_runs(), self.game.home_hits(), self.game.home_errors()),
            TeamType.AWAY: self._scoreline(self.game.away_runs(), self.game.away_hits(), self.game.away_errors()),
        }

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
