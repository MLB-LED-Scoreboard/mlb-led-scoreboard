import time
from typing import Callable, NoReturn

import debug
from data import Data, status
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
        self.data: Data = data
        self.is_playoffs = self.data.schedule.date > self.data.headlines.important_dates.playoffs_start_date
        self.canvas = matrix.CreateFrameCanvas()
        self.scrolling_text_pos = self.canvas.width
        self.game_changed_time = time.time()
        self.animation_time = 0
        self.standings_stat = "w"
        self.standings_league = "NL"

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
        self.__draw_news(permanent_cond())

    def __draw_news(self, cond: Callable[[], bool]):
        self.data.scrolling_finished = False
        self.scrolling_text_pos = self.canvas.width
        while cond():
            for _ in range(round(1 / self.data.config.scrolling_speed)):
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
                # todo make pos something persistent if we want to show news as part of rotation?
                # not strictly necessary but nice?
                self.__update_scrolling_text_pos(pos, self.canvas.width)
                # Show network issues
                if self.data.network_issues:
                    network.render_network_error(
                        self.canvas, self.data.config.layout, self.data.config.scoreboard_colors
                    )
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                time.sleep(self.data.config.scrolling_speed)

    # Render the standings screen
    def __render_standings(self) -> NoReturn:
        self.__draw_standings(permanent_cond())

        # Out of season off days don't always return standings so fall back on the offday renderer
        debug.error("No standings data.  Falling back to off day.")
        self.__render_offday()

    def __draw_standings(self, cond: Callable[[], bool]):
        if not self.data.standings.populated():
            return

        if self.data.standings.is_postseason() and self.canvas.width <= 32:
            return

        update = 0
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

            if self.data.standings.is_postseason() and update % 20 == 0:
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

    # Renders a game screen based on it's status
    # May also call draw_offday or draw_standings if there are no games
    def __render_game(self) -> NoReturn:
        # Set the refresh rate
        refresh_rate = self.data.config.scrolling_speed

        while True:
            if not self.data.schedule.games_live():
                if self.data.config.news_no_games and self.data.config.standings_no_games:
                    # TODO make configurable time?
                    # also, using all_of here is maybe overkill
                    self.__draw_news(all_of(timer_cond(120), self.no_games_cond()))
                    self.__draw_standings(all_of(timer_cond(120), self.no_games_cond()))
                    continue
                elif self.data.config.news_no_games:
                    self.__draw_news(self.no_games_cond())
                elif self.data.config.standings_no_games:
                    self.__draw_standings(self.no_games_cond())

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

    # TODO: based on the above, we can start to think of a more generalized rotation

    # new config format:
    # offday: [news, standings]
    # no_games_live: [news, standings]
    # rotation: [preferred_teams, news, standings, followed_teams, live_games]

    # requires some coordination for when rotation occurs, data object needs to have a sense of when
    # we're in a game vs another screen, and for how long.

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
            self.data.config.short_team_names_for_runs_hits,
            show_score=not status.is_pregame(game.status()),
        )

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
        if pos_after_scroll + new_pos < 0:
            self.data.scrolling_finished = True
            if pos_after_scroll + new_pos < -10:
                self.scrolling_text_pos = end
                return
        self.scrolling_text_pos = pos_after_scroll

    def no_games_cond(self) -> Callable[[], bool]:
        def cond():
            return not self.data.schedule.games_live()

        return cond


def permanent_cond() -> Callable[[], bool]:
    return lambda: True


def timer_cond(time) -> Callable[[], bool]:
    curr = 0

    def cond():
        nonlocal curr
        curr += 1

        return curr < time

    return cond


def all_of(*conds) -> Callable[[], bool]:
    def cond():
        return all(c() for c in conds)

    return cond
