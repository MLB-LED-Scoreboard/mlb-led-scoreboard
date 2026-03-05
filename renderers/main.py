import time
from typing import Callable, NoReturn


import debug
from data import Data, status
from data.scoreboard import Scoreboard
from data.scoreboard.postgame import Postgame
from data.scoreboard.pregame import Pregame
from data.game import Game
import data.config.layout as layout

from renderers import network, offday, standings
from renderers.games import game as gamerender
from renderers.games import irregular
from renderers.games import postgame as postgamerender
from renderers.games import pregame as pregamerender
from renderers.games import teams


class MainRenderer:
    def __init__(self, matrix, data: Data) -> None:
        self.matrix = matrix
        self.data: Data = data
        self.is_playoffs = self.data.schedule.date > self.data.headlines.important_dates.playoffs_start_date.date()
        self.canvas = matrix.CreateFrameCanvas()
        self.scrolling_text_pos = self.canvas.width
        self.scrolling_finished: bool = False

        self.animation_time = 0
        self.standings_stat = "w"
        self.standings_league = "NL"

    def render(self) -> NoReturn:
        while True:
            self.__render_games()
            self.__check_acknowledgement()
            if t := self.data.config.standings_at_priority(self.data.schedule.priority):
                self.__draw_standings(timer_cond(t))
            if t := self.data.config.news_at_priority(self.data.schedule.priority):
                self.__draw_news(any_of(timer_cond(t), self.scrolling_finished_cond))

    def __render_games(self):
        # bit of a hack, helps when we change priorities
        # and want to go back to a specific game.
        # could also let the drawings/standings tell the main that they can update next?
        self.__request_next_game()
        seen_games = set()
        while True:
            self.scrolling_text_pos = self.canvas.width
            self.scrolling_finished = False
            self.__check_acknowledgement()

            game = self.data.get_rendering_game()
            if game is None:
                break

            if game.game_id not in seen_games:
                seen_games.add(game.game_id)
                if len(seen_games) > self.data.schedule.num_games():
                    break
                debug.log("Render thread: showing game %d / %d", len(seen_games), self.data.schedule.num_games())

            cond = any_of(
                timer_cond(self.data.config.rotate_rate_for_status(game.status())),
                self.scrolling_finished_cond,
            )
            while cond():
                self.__update_layout_state(game)
                self.__draw_game(game)
                self.__check_acknowledgement()
                time.sleep(self.data.config.scrolling_speed)

            self.__request_next_game()

    def __request_next_game(self):
        if self.data.rendering == "current":
            debug.log("Render thread: requesting main thread to read 'next' game")
        self.data.rendering = "next"

    def __check_acknowledgement(self):
        if self.data.rendering == "next" and self.data.acknowledged_next_game:
            debug.log("Render thread: main thread has acknowledged, switching back to reading 'current' game")
            self.data.rendering = "current"

    # Draws the provided game on the canvas
    def __draw_game(self, game: Game):
        bgcolor = self.data.config.scoreboard_colors.color("default.background")
        self.canvas.Fill(bgcolor["r"], bgcolor["g"], bgcolor["b"])
        scoreboard = Scoreboard(game)
        layout = self.data.config.layout
        colors = self.data.config.scoreboard_colors

        if status.is_pregame(game.status()):  # Draw the pregame information
            self.__max_scroll_x(layout.coords("pregame.scrolling_text"))
            pregame = Pregame(game, self.data.config.time_format)
            pos = pregamerender.render_pregame(
                self.canvas,
                layout,
                colors,
                pregame,
                self.scrolling_text_pos,
                self.data.config.pregame_weather,
                self.is_playoffs,
            )
            self.__update_scrolling_text_pos(pos, self.canvas.width)

        elif status.is_complete(game.status()):  # Draw the game summary
            self.__max_scroll_x(layout.coords("final.scrolling_text"))
            final = Postgame(game)
            pos = postgamerender.render_postgame(
                self.canvas, layout, colors, final, scoreboard, self.scrolling_text_pos, self.is_playoffs
            )
            self.__update_scrolling_text_pos(pos, self.canvas.width)

        elif status.is_irregular(game.status()):  # Draw game status
            short_text = self.data.config.layout.coords("status.text")["short_text"]
            if scoreboard.get_text_for_reason():
                self.__max_scroll_x(layout.coords("status.scrolling_text"))
                pos = irregular.render_irregular_status(
                    self.canvas, layout, colors, scoreboard, short_text, self.scrolling_text_pos
                )
                self.__update_scrolling_text_pos(pos, self.canvas.width)
            else:
                irregular.render_irregular_status(self.canvas, layout, colors, scoreboard, short_text)
                self.scrolling_finished = True

        else:  # draw a live game
            if scoreboard.homerun() or scoreboard.strikeout() or scoreboard.hit() or scoreboard.walk():
                self.animation_time += 1
            else:
                self.animation_time = 0

            if status.is_inning_break(scoreboard.inning.state):
                loop_point = self.data.config.layout.coords("inning.break.due_up")["loop"]
            else:
                loop_point = self.data.config.layout.coords("atbat")["loop"]

            self.scrolling_text_pos = min(self.scrolling_text_pos, loop_point)
            pos = gamerender.render_live_game(
                self.canvas, layout, colors, scoreboard, self.scrolling_text_pos, self.animation_time
            )
            self.__update_scrolling_text_pos(pos, loop_point)

        # draw last so it is always on top
        teams.render_team_banner(
            self.canvas,
            layout,
            self.data.config.team_colors,
            scoreboard.home_team,
            scoreboard.away_team,
            self.data.config.full_team_names,
            self.data.config.short_team_names_for_runs_hits,
            show_score=not status.is_pregame(game.status()),
        )

        # Show network issues
        if self.data.network_issues:
            network.render_network_error(self.canvas, layout, colors)

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def __draw_news(self, cond: Callable[[], bool]):
        """
        Draw the news screen for as long as cond returns True
        """
        self.scrolling_text_pos = self.canvas.width
        self.scrolling_finished = False
        color = self.data.config.scoreboard_colors.color("default.background")
        while cond():
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
            if self.scrolling_text_pos == self.canvas.width:
                self.data.headlines.advance_ticker()
            # Show network issues
            if self.data.network_issues:
                network.render_network_error(self.canvas, self.data.config.layout, self.data.config.scoreboard_colors)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(self.data.config.scrolling_speed)
            self.__check_acknowledgement()

    def __draw_standings(self, cond: Callable[[], bool]):
        """
        Draw the standings screen for as long as cond returns True
        """
        if not self.data.standings.populated():
            return

        if self.data.standings.is_postseason() and self.canvas.width <= 32:
            return

        update = 1
        while cond():
            if self.data.standings.is_postseason():
                standings.render_bracket(
                    self.canvas,
                    self.data.config.layout,
                    self.data.config.scoreboard_colors,
                    self.data.standings.leagues[self.standings_league],
                )
            else:
                standings.render_standings(
                    self.canvas,
                    self.data.config.layout,
                    self.data.config.scoreboard_colors,
                    self.data.standings.current_standings(),
                    self.standings_stat,
                )

            if self.data.network_issues:
                network.render_network_error(self.canvas, self.data.config.layout, self.data.config.scoreboard_colors)

            self.canvas = self.matrix.SwapOnVSync(self.canvas)

            if self.data.standings.is_postseason():
                if update % 20 == 0:
                    if self.standings_league == "NL":
                        self.standings_league = "AL"
                    else:
                        self.standings_league = "NL"
            elif self.canvas.width == 32 and update % 5 == 0:
                if self.standings_stat == "w":
                    self.standings_stat = "l"
                else:
                    self.standings_stat = "w"
                    self.data.standings.advance_to_next_standings()
            elif self.canvas.width > 32 and update % 10 == 0:
                self.data.standings.advance_to_next_standings()

            time.sleep(1)
            update = (update + 1) % 100
            self.__check_acknowledgement()

    def __max_scroll_x(self, scroll_coords):
        scroll_max_x = scroll_coords["x"] + scroll_coords["width"]
        self.scrolling_text_pos = min(scroll_max_x, self.scrolling_text_pos)

    def __update_scrolling_text_pos(self, new_pos, end):
        """Updates the position of scrolling text"""
        pos_after_scroll = self.scrolling_text_pos - 1
        if pos_after_scroll + new_pos < 0:
            self.scrolling_finished = True
            if pos_after_scroll + new_pos < -10:
                self.scrolling_text_pos = end
                return
        else:
            self.scrolling_finished = False
        self.scrolling_text_pos = pos_after_scroll

    def __update_layout_state(self, game):

        self.data.config.layout.set_state()
        if game.status() == status.WARMUP:
            self.data.config.layout.set_state(layout.LAYOUT_STATE_WARMUP)

        if game.is_no_hitter():
            self.data.config.layout.set_state(layout.LAYOUT_STATE_NOHIT)

        if game.is_perfect_game():
            self.data.config.layout.set_state(layout.LAYOUT_STATE_PERFECT)

    def scrolling_finished_cond(self) -> bool:
        """A condition that is true only while the scrolling text has finished scrolling"""
        return self.data.config.rotation_scroll_until_finished and not self.scrolling_finished


def never_cond() -> bool:
    """A condition that is always false"""
    return False


def permanent_cond() -> bool:
    """A condition that is always true"""
    return True


def timer_cond(seconds) -> Callable[[], bool]:
    """Create a condition that is true for the specified number of seconds"""
    end = time.time() + seconds

    def cond():
        return time.time() < end

    return cond


def any_of(*conds) -> Callable[[], bool]:
    """Create a condition that is true if any of the given conditions are true"""

    def cond():
        return any(c() for c in conds)

    return cond
