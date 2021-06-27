import time
from typing import NoReturn

import debug
from data import status
from data.scoreboard import Scoreboard
from data.scoreboard.postgame import Postgame
from data.scoreboard.pregame import Pregame
from renderers import network, offday, standings
from renderers.games import game as gamerender
from renderers.games import irregular
from renderers.games import postgame as postgamerender
from renderers.games import pregame as pregamerender
from renderers.games import teams


class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.canvas = matrix.CreateFrameCanvas()
        self.scrolling_text_pos = self.canvas.width
        self.game_changed_time = time.time()
        self.animation_time = 0
        self.standings_stat = "w"

    def render(self):
        screen = self.data.get_screen_type()
        # display the news ticker
        if screen == "news":
            self.__render_offday()
        # display the standings
        elif screen == "standings":
            self.__render_standings()
        # Playball!
        else:
            self.__render_game()

    # Render an offday screen with the weather, clock and news
    def __render_offday(self) -> NoReturn:
        self.data.scrolling_finished = False
        self.scrolling_text_pos = self.canvas.width

        while True:
            color = self.data.config.scoreboard_colors.color("default.background")
            self.canvas.Fill(color["r"], color["g"], color["b"])

            self.__max_scroll_x(self.data.config.layout.coords("offday.scrolling_text"))
            pos = offday.render_offday_screen(
                self.canvas,
                self.data.config.layout,
                self.data.config.scoreboard_colors,
                self.data.weather,
                self.data.headlines,
                self.data.config.time_format,
                self.scrolling_text_pos,
            )
            self.__update_scrolling_text_pos(pos, self.canvas.width)
            # Show network issues
            if self.data.network_issues:
                network.render_network_error(self.canvas, self.data.config.layout, self.data.config.scoreboard_colors)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(self.data.config.scrolling_speed)

    # Render the standings screen
    def __render_standings(self) -> NoReturn:
        if self.data.standings.divisions:
            self.__draw_standings(True)
        else:
            # Out of season off days don't always return standings so fall back on the offday renderer
            debug.error("No standings data.  Falling back to off day.")
            self.__render_offday()

    def __draw_standings(self, stick=False):
        while stick or (self.data.config.standings_no_games and not self.data.schedule.games_live()):
            standings.render_standings(
                self.canvas,
                self.data.config.layout,
                self.data.config.scoreboard_colors,
                self.data.standings,
                self.standings_stat,
            )

            if self.data.network_issues:
                network.render_network_error(self.canvas, self.data.config.layout, self.data.config.scoreboard_colors)

            self.canvas = self.matrix.SwapOnVSync(self.canvas)

            # we actually keep this logic on the render thread
            if self.canvas.width > 32:
                time.sleep(10)
                self.data.standings.advance_to_next_standings()
            else:
                if self.standings_stat == "w":
                    self.standings_stat = "l"
                else:
                    self.standings_stat = "w"
                    self.data.standings.advance_to_next_standings()
                time.sleep(5)

    # Renders a game screen based on it's status
    def __render_game(self) -> NoReturn:
        # Set the refresh rate
        refresh_rate = self.data.config.scrolling_speed

        while True:
            # we know we aren't out of season so it should be ok to do this unconditionally
            self.__draw_standings()

            if self.game_changed_time < self.data.game_changed_time:
                self.scrolling_text_pos = self.canvas.width
                self.data.scrolling_finished = False
                self.game_changed_time = time.time()

            # Draw the current game
            self.__draw_game()

            # Check if we need to scroll until it's finished
            if not self.data.config.rotation_scroll_until_finished:
                self.data.scrolling_finished = True

            time.sleep(refresh_rate)

    # Draws the provided game on the canvas
    def __draw_game(self):
        game = self.data.current_game
        bgcolor = self.data.config.scoreboard_colors.color("default.background")
        self.canvas.Fill(bgcolor["r"], bgcolor["g"], bgcolor["b"])

        scoreboard = Scoreboard(game)
        layout = self.data.config.layout
        colors = self.data.config.scoreboard_colors
        teams.render_team_banner(
            self.canvas,
            layout,
            self.data.config.team_colors,
            scoreboard.home_team,
            scoreboard.away_team,
            self.data.config.full_team_names,
        )

        if status.is_pregame(game.status()):  # Draw the pregame information
            self.__max_scroll_x(layout.coords("pregame.scrolling_text"))
            pregame = Pregame(game, self.data.config.time_format)
            pos = pregamerender.render_pregame(self.canvas, layout, colors, pregame, self.scrolling_text_pos)
            self.__update_scrolling_text_pos(pos, self.canvas.width)

        elif status.is_complete(game.status()):  # Draw the game summary
            self.__max_scroll_x(layout.coords("final.scrolling_text"))
            final = Postgame(game)
            pos = postgamerender.render_postgame(
                self.canvas, layout, colors, final, scoreboard, self.scrolling_text_pos
            )
            self.__update_scrolling_text_pos(pos, self.canvas.width)

        elif status.is_irregular(game.status()):  # Draw game status
            short_text = (self.data.config.layout.coords("status.text")["short_text"],)
            if scoreboard.get_text_for_reason():
                self.__max_scroll_x(layout.coords("status.scrolling_text"))
                pos = irregular.render_irregular_status(
                    self.canvas, layout, colors, scoreboard, short_text, self.scrolling_text_pos
                )
                self.__update_scrolling_text_pos(pos, self.canvas.width)
            else:
                irregular.render_irregular_status(self.canvas, layout, colors, scoreboard, short_text)
                self.data.scrolling_finished = True

        else:  # draw a live game
            if scoreboard.homerun() or scoreboard.strikeout():
                self.animation_time += 1
            else:
                self.animation_time = 0

            loop_point = self.data.config.layout.coords("atbat")["loop"]
            self.scrolling_text_pos = min(self.scrolling_text_pos, loop_point)
            pos = gamerender.render_live_game(
                self.canvas, layout, colors, scoreboard, self.scrolling_text_pos, self.animation_time
            )
            self.__update_scrolling_text_pos(pos, loop_point)

        # Show network issues
        if self.data.network_issues:
            network.render_network_error(self.canvas, layout, colors)

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def __max_scroll_x(self, scroll_coords):
        scroll_max_x = scroll_coords["x"] + scroll_coords["width"]
        self.scrolling_text_pos = min(scroll_max_x, self.scrolling_text_pos)

    def __update_scrolling_text_pos(self, new_pos, end):
        """Updates the position of the probable starting pitcher text."""
        pos_after_scroll = self.scrolling_text_pos - 1
        if pos_after_scroll + new_pos < -4:
            self.data.scrolling_finished = True
            self.scrolling_text_pos = end
        else:
            self.scrolling_text_pos = pos_after_scroll
