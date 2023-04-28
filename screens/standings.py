from screens.base import MLBLEDScoreboardScreen
from driver import graphics
from utils import center_text_position

class DivisionStandingsScreen(MLBLEDScoreboardScreen):

    class DivisionRequired(Exception):
        pass

    def __init__(self, *args, division=None):
        if division is None:
            raise DivisionStandingsScreen.DivisionRequired("A division is required to use this screen type")

        super().__init__(*args)

        if self.canvas.width > 32:
            self.subscreen = DivisionStandingsScreen.StaticStandingsSubscreen(self)

        self.division = division

    def on_render(self):
        self.subscreen.on_render()

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def get_standings_color_node(self, name):
        try:
            league = self.data.division_for(self.division).name[:2].lower()
            return self.data.config.scoreboard_colors.graphics_color(f"standings.{league}.{name}")
        except Exception:
            return self.data.config.scoreboard_colors.graphics_color(f"standings.{name}")
    
    class StaticStandingsSubscreen:

        def __init__(self, parent):
            self.parent = parent

        def on_render(self):
            coords = self.parent.data.config.layout.coords("standings")
            font   = self.parent.data.config.layout.font("standings")

            divider_color       = self.parent.get_standings_color_node("divider")
            team_stat_color     = self.parent.get_standings_color_node("team.stat")
            team_name_color     = self.parent.get_standings_color_node("team.name")
            team_elim_color     = self.parent.get_standings_color_node("team.elim")
            team_clinched_color = self.parent.get_standings_color_node("team.clinched")

            start = coords.get("start", 0)
            offset = coords["offset"]

            graphics.DrawLine(
                self.parent.canvas,
                0,
                start,
                coords["width"],
                start,
                divider_color
            )

            graphics.DrawLine(
                self.parent.canvas,
                coords["divider"]["x"],
                start,
                coords["divider"]["x"],
                start + coords["height"],
                divider_color
            )

            offset += start

            teams = self.parent.data.standings.standings_for(self.parent.division).teams

            for team in teams:
                graphics.DrawLine(self.parent.canvas, 0, offset, coords["width"], offset, divider_color)

                color = team_elim_color if team.elim else (team_clinched_color if team.clinched else team_name_color)
                team_text = team.team_abbrev
                graphics.DrawText(self.parent.canvas, font["font"], coords["team"]["name"]["x"], offset, color, team_text)

                record_text = "{:>3}-{:<3}".format(team.w, team.l)
                record_text_x = center_text_position(record_text, coords["team"]["record"]["x"], font["size"]["width"])

                if "-" in str(team.gb):
                    gb_text = " -  "
                else:
                    gb_text = "{:>4s}".format(str(team.gb))
                gb_text_x = coords["team"]["games_back"]["x"] - (len(gb_text) * font["size"]["width"])

                color = team_elim_color if team.elim else (team_clinched_color if team.clinched else team_stat_color)
                graphics.DrawText(self.parent.canvas, font["font"], record_text_x, offset, color, record_text)
                graphics.DrawText(self.parent.canvas, font["font"], gb_text_x, offset, color, gb_text)

                offset += coords["offset"]

