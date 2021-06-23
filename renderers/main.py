import time

import debug
from data.final import Final
from data.pregame import Pregame
from data.scoreboard import Scoreboard
from data.status import Status
from renderers.final import Final as FinalRenderer
from renderers.offday import OffdayRenderer
from renderers.pregame import Pregame as PregameRenderer
from renderers.scoreboard import Scoreboard as ScoreboardRenderer
from renderers.standings import StandingsRenderer
from renderers.status import StatusRenderer

SCROLL_TEXT_FAST_RATE = 0.1
SCROLL_TEXT_SLOW_RATE = 0.2


class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.canvas = matrix.CreateFrameCanvas()
        self.scrolling_text_pos = self.canvas.width
        self.game_changed_time = time.time()
        self.animation_time = 0

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
    def __render_offday(self):
        self.data.scrolling_finished = False
        self.scrolling_text_pos = self.canvas.width

        while True:
            color = self.data.config.scoreboard_colors.color("default.background")
            self.canvas.Fill(color["r"], color["g"], color["b"])

            self.__max_scroll_x(self.data.config.layout.coords("offday.scrolling_text"))
            renderer = OffdayRenderer(self.canvas, self.data, self.scrolling_text_pos)
            self.__update_scrolling_text_pos(renderer.render(), self.canvas.width)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(self.data.config.scrolling_speed)

    # Render the standings screen
    def __render_standings(self):
        if self.data.standings.divisions:
            StandingsRenderer(self.matrix, self.canvas, self.data).render()
        else:
            # Out of season off days don't always return standings so fall back on the offday renderer
            debug.error("No standings data.  Falling back to off day.")
            self.__render_offday()

    # Renders a game screen based on it's status
    def __render_game(self):
        # Set the refresh rate
        refresh_rate = self.data.config.scrolling_speed
        while True:

            if self.data.config.standings_no_games and not self.data.schedule.games_live():
                # we know we aren't out of season so it should be ok to do this unconditionally
                StandingsRenderer(self.matrix, self.canvas, self.data).render()

            # Draw the current game
            self.__draw_game(self.data.current_game)

            # Check if we need to scroll until it's finished
            if not self.data.config.rotation_scroll_until_finished:
                self.data.scrolling_finished = True

            # Currently the only thing that's always static is the live scoreboard
            if Status.is_static(self.data.current_game.status()):
                self.data.scrolling_finished = True

            # If the status is irregular and there's no 'reason' text, finish scrolling
            if (
                Status.is_irregular(self.data.current_game.status())
                and Scoreboard(self.data.current_game).get_text_for_reason() is None
            ):
                self.data.scrolling_finished = True

            time.sleep(refresh_rate)

            if self.game_changed_time < self.data.game_changed_time:
                self.scrolling_text_pos = self.canvas.width
                self.data.scrolling_finished = False
                self.game_changed_time = time.time()

    # Draws the provided game on the canvas
    def __draw_game(self, game):
        color = self.data.config.scoreboard_colors.color("default.background")
        self.canvas.Fill(color["r"], color["g"], color["b"])

        # Draw the pregame renderer
        if Status.is_pregame(game.status()):
            scoreboard = Scoreboard(game)
            self.__max_scroll_x(self.data.config.layout.coords("pregame.scrolling_text"))
            pregame = Pregame(game, self.data.config.time_format)
            renderer = PregameRenderer(self.canvas, pregame, scoreboard, self.data, self.scrolling_text_pos)
            self.__update_scrolling_text_pos(renderer.render(), self.canvas.width)

        # Draw the final game renderer
        elif Status.is_complete(game.status()):
            self.__max_scroll_x(self.data.config.layout.coords("final.scrolling_text"))
            final = Final(game)
            scoreboard = Scoreboard(game)
            renderer = FinalRenderer(self.canvas, final, scoreboard, self.data, self.scrolling_text_pos)
            self.__update_scrolling_text_pos(renderer.render(), self.canvas.width)

        # Draw the scoreboar renderer
        elif Status.is_irregular(game.status()):
            scoreboard = Scoreboard(game)
            if scoreboard.get_text_for_reason():
                self.__max_scroll_x(self.data.config.layout.coords("status.scrolling_text"))
                renderer = StatusRenderer(self.canvas, scoreboard, self.data, self.scrolling_text_pos)
                self.__update_scrolling_text_pos(renderer.render(), self.canvas.width)
            else:
                StatusRenderer(self.canvas, scoreboard, self.data).render()
        else:
            self.__max_scroll_x(self.data.config.layout.coords("status.scrolling_text"))
            scoreboard = Scoreboard(game)
            loop_point = self.data.config.layout.coords("atbat")["loop"]
            self.animation_time = (
                0 if not (scoreboard.homerun() or scoreboard.strikeout()) else (self.animation_time + 1)
            )
            self.scrolling_text_pos = min(self.scrolling_text_pos, loop_point)
            renderer = ScoreboardRenderer(
                self.canvas, scoreboard, self.data, self.scrolling_text_pos, self.animation_time
            )
            self.__update_scrolling_text_pos(renderer.render(), loop_point)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def __max_scroll_x(self, scroll_coords):
        scroll_coords = self.data.config.layout.coords("final.scrolling_text")
        scroll_max_x = scroll_coords["x"] + scroll_coords["width"]
        if self.scrolling_text_pos > scroll_max_x:
            self.scrolling_text_pos = scroll_max_x
        return scroll_max_x

    def __update_scrolling_text_pos(self, new_pos, end):
        """Updates the position of the probable starting pitcher text."""
        pos_after_scroll = self.scrolling_text_pos - 1
        if pos_after_scroll + new_pos < -4:
            self.data.scrolling_finished = True
            self.scrolling_text_pos = end
        else:
            self.scrolling_text_pos = pos_after_scroll
