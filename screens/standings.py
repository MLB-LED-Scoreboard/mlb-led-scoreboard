from screens.base import MLBLEDScoreboardScreen
from driver import graphics
from utils import center_text_position

import time

class DivisionStandingsScreen(MLBLEDScoreboardScreen):

    class DivisionRequired(Exception):
        pass

    def __init__(self, *args, division=None):
        if division is None:
            raise DivisionStandingsScreen.DivisionRequired("A division is required to use this screen type")

        super().__init__(*args)

        self.division = division
        self.league = self.division[:2].lower()

    def on_render(self):
        self.subscreen.on_render()

    def ready_to_rotate(self):
        return self.subscreen.ready_to_rotate()
    
    def on_rotate_to(self):
        if self.canvas.width > 32:
            self.subscreen = DivisionStandingsScreen.StaticStandingsSubscreen(self)
        else:
            self.subscreen = DivisionStandingsScreen.RotatingStandingsSubscreen(self)

    @property
    def background_color(self):
        return self.get_standings_color_node("background")

    def get_standings_color_node(self, name):
        try:
            return self.data.config.scoreboard_colors.graphics_color(f"standings.{self.league}.{name}")
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

        def ready_to_rotate(self):
            return True


    class RotatingStandingsSubscreen:

        # How long to display wins vs. losses
        # This is not configurable at the moment, but could be later.
        ROTATION_RATE_SECONDS = 5

        WINS = "w"
        LOSSES = "l"

        def __init__(self, parent):
            self.parent = parent
            self.stat = self.WINS

            # This subscreen must rotate through both W and L stats
            self.rotated_at = time.time()
            self.rotated = False

        def on_render(self):
            self.try_rotation()

            coords = self.parent.data.config.layout.coords("standings")
            font   = self.parent.data.config.layout.font("standings")

            divider_color       = self.parent.get_standings_color_node("divider")
            stat_color          = self.parent.get_standings_color_node("stat")
            team_stat_color     = self.parent.get_standings_color_node("team.stat")
            team_name_color     = self.parent.get_standings_color_node("team.name")
            team_elim_color     = self.parent.get_standings_color_node("team.elim")
            team_clinched_color = self.parent.get_standings_color_node("team.clinched")

            offset = coords["offset"]

            graphics.DrawLine(
                self.parent.canvas,
                0,
                0,
                coords["width"],
                0,
                divider_color
            )

            graphics.DrawText(
                self.parent.canvas,
                font["font"],
                coords["stat_title"]["x"],
                offset,
                stat_color,
                self.stat.upper()
            )

            graphics.DrawLine(
                self.parent.canvas,
                coords["divider"]["x"],
                0,
                coords["divider"]["x"],
                coords["height"],
                divider_color
            )

            teams = self.parent.data.standings.standings_for(self.parent.division).teams

            for team in teams:
                graphics.DrawLine(self.parent.canvas, 0, offset, coords["width"], offset, divider_color)

                team_text = "{:3s}".format(team.team_abbrev)
                stat_text = str(getattr(team, self.stat))
                color = team_elim_color if team.elim else (team_clinched_color if team.clinched else team_name_color)
                graphics.DrawText(self.parent.canvas, font["font"], coords["team"]["name"]["x"], offset, color, team_text)
                color = team_elim_color if team.elim else (team_clinched_color if team.clinched else team_stat_color)
                graphics.DrawText(self.parent.canvas, font["font"], coords["team"]["record"]["x"], offset, color, stat_text)

                offset += coords["offset"]

        def ready_to_rotate(self):
            # The stats have rotated and it's been at least ROTATION_RATE_SECONDS since it rotated
            return self.rotated and self.rotated_at + self.ROTATION_RATE_SECONDS <= time.time()
        
        def try_rotation(self):
            # This ensures that W / L are rotated evenly -- if wins are displayed, losses also must be.
            if self.rotated_at + self.ROTATION_RATE_SECONDS <= time.time():
                self.rotated_at = time.time()

                if self.stat == self.WINS:
                    self.stat = self.LOSSES

                    self.rotated = True
                else:
                    self.stat = self.WINS

                    self.rotated = False
