import time
from typing import Callable, NoReturn

import bullpen.api as api


import debug
from data import Data, status
from data.scoreboard import Scoreboard
from data.scoreboard.postgame import Postgame
from data.scoreboard.pregame import Pregame
from data.game import Game

from renderers import network
from renderers.games import game as gamerender
from renderers.games import irregular
from renderers.games import postgame as postgamerender
from renderers.games import pregame as pregamerender
from renderers.games import teams


class MainRenderer:
    def __init__(self, matrix, data: Data, plugins: dict[str, api.Renderer]) -> None:
        self.matrix = matrix
        self.data = data
        self.canvas = matrix.CreateFrameCanvas()
        self.scrolling_text_pos = self.canvas.width
        self.scrolling_finished: bool = False
        self.plugins = plugins

        self.animation_time = 0

    def render(self) -> NoReturn:
        while True:
            if self.data.schedule.num_games() > 0:
                self.__render_games()

            for plugin in self.data.config.rotation_screen_rules.get(self.data.schedule.priority, {}):
                if t := self.data.config.screen_time_at_priority(plugin, self.data.schedule.priority):
                    debug.log("Rotating to plugin %s for %d seconds", plugin, t)
                    self.__draw_plugin_screen(plugin, any_of(timer_cond(t), self.scrolling_finished_cond()))

    def __render_games(self):
        seen_games = set()
        while True:
            self.scrolling_text_pos = self.canvas.width

            game = self.data.games.next()
            if game is None:
                debug.warning("Render thread: no game to render, sleeping for a bit")
                time.sleep(1)
                break

            if len(seen_games) >= self.data.schedule.num_games():
                break
            seen_games.add(game.game_id)

            debug.log("Render thread: showing game %d / %d", len(seen_games), self.data.schedule.num_games())

            cond = any_of(
                timer_cond(self.data.config.rotate_rate_for_status(game.status())),
                self.scrolling_finished_cond(),
            )
            while cond():
                self.data.config.layout.state_for_game(game)
                self.__draw_game(game)
                time.sleep(self.data.config.scrolling_speed)

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
                self.data.config.is_postseason(),
            )
            self.__update_scrolling_text_pos(pos, self.canvas.width)

        elif status.is_complete(game.status()):  # Draw the game summary
            self.__max_scroll_x(layout.coords("final.scrolling_text"))
            final = Postgame(game)
            pos = postgamerender.render_postgame(
                self.canvas,
                layout,
                colors,
                final,
                scoreboard,
                self.scrolling_text_pos,
                self.data.config.is_postseason(),
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
            show_score=not status.is_pregame(game.status()),
        )

        # Show network issues
        if self.data.network_issues:
            network.render_network_error(self.canvas, layout, colors)

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def __draw_plugin_screen(self, plugin_name: str, cond: Callable[[], bool]) -> None:
        from driver import graphics

        self.scrolling_text_pos = self.canvas.width

        renderer = self.plugins[plugin_name]
        wait_time = renderer.wait_time()

        while cond():
            pos = renderer.render(self.data.plugin_data[plugin_name], self.canvas, graphics, self.scrolling_text_pos)
            self.__update_scrolling_text_pos(pos, self.canvas.width)

            # Show network issues
            if self.data.network_issues:
                network.render_network_error(self.canvas, self.data.config.layout, self.data.config.scoreboard_colors)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(wait_time)

        renderer.reset()

    def __max_scroll_x(self, scroll_coords):
        scroll_max_x = scroll_coords["x"] + scroll_coords["width"]
        self.scrolling_text_pos = min(scroll_max_x, self.scrolling_text_pos)

    def __update_scrolling_text_pos(self, new_pos, end):
        """Updates the position of scrolling text"""
        if new_pos is None:
            self.scrolling_finished = True
            return
        pos_after_scroll = self.scrolling_text_pos - 1
        if pos_after_scroll + new_pos < 0:
            self.scrolling_finished = True
            if pos_after_scroll + new_pos < -10:
                self.scrolling_text_pos = end
                return
        else:
            self.scrolling_finished = False
        self.scrolling_text_pos = pos_after_scroll

    def scrolling_finished_cond(self) -> Callable[[], bool]:
        """A condition that is true only while the scrolling text has finished scrolling"""
        if not self.data.config.rotation_scroll_until_finished:
            return never_cond

        self.scrolling_finished = False

        def cond():
            return not self.scrolling_finished

        return cond


def never_cond() -> bool:
    """A condition that is always false"""
    return False


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
