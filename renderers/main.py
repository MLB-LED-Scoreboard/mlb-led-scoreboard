import time
from typing import Callable, NoReturn
from data.screens import ScreenType

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

# TODO(BMW) make configurable time?
STANDINGS_NEWS_SWITCH_TIME = 120


class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data: Data = data
        self.is_playoffs = self.data.schedule.date > self.data.headlines.important_dates.playoffs_start_date.date()
        self.canvas = matrix.CreateFrameCanvas()
        self.scrolling_text_pos = self.canvas.width
        self.game_changed_time = time.time()
        self.animation_time = 0
        self.standings_stat = "w"
        self.standings_league = "NL"

    def render(self):
        screen = self.data.get_screen_type()
        # display the news ticker
        if screen == ScreenType.ALWAYS_NEWS:
            self.__draw_news(permanent_cond)
        # display the standings
        elif screen == ScreenType.ALWAYS_STANDINGS:
            self.__render_standings()
        elif screen == ScreenType.LEAGUE_OFFDAY:
            self.__render_offday(team_offday=False)
        elif screen == ScreenType.PREFERRED_TEAM_OFFDAY:
            self.__render_offday(team_offday=True)
        # Playball!
        else:
            self.__render_gameday()

    def __render_offday(self, team_offday=True) -> NoReturn:
        if team_offday:
            news = self.data.config.news_ticker_team_offday
            standings = self.data.config.standings_team_offday
        else:
            news = True
            standings = self.data.config.standings_mlb_offday

        if news and standings:
            while True:
                self.__draw_news(timer_cond(STANDINGS_NEWS_SWITCH_TIME))
                self.__draw_standings(timer_cond(STANDINGS_NEWS_SWITCH_TIME))
        elif news:
            self.__draw_news(permanent_cond)
        else:
            self.__render_standings()

    def __render_standings(self) -> NoReturn:
        self.__draw_standings(permanent_cond)

        # Out of season off days don't always return standings so fall back on the news renderer
        debug.error("No standings data.  Falling back to news.")
        self.__draw_news(permanent_cond)

    # Renders a game screen based on it's status
    # May also call draw_offday or draw_standings if there are no games
    def __render_gameday(self) -> NoReturn:
        refresh_rate = self.data.config.scrolling_speed
        while True:
            if not self.data.schedule.games_live():
                if self.data.config.news_no_games and self.data.config.standings_no_games:
                    self.__draw_news(all_of(timer_cond(STANDINGS_NEWS_SWITCH_TIME), self.no_games_cond))
                    self.__draw_standings(all_of(timer_cond(STANDINGS_NEWS_SWITCH_TIME), self.no_games_cond))
                    continue
                elif self.data.config.news_no_games:
                    self.__draw_news(self.no_games_cond)
                elif self.data.config.standings_no_games:
                    self.__draw_standings(self.no_games_cond)

            if self.game_changed_time < self.data.game_changed_time:
                self.scrolling_text_pos = self.canvas.width
                self.data.scrolling_finished = not self.data.config.rotation_scroll_until_finished
                self.game_changed_time = time.time()

            # Draw the current game
            self.__draw_game()

            time.sleep(refresh_rate)

    # Draws the provided game on the canvas
    def __draw_game(self):
        game = self.data.current_game
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
                self.data.scrolling_finished = True

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

    def __draw_news(self, cond: Callable[[], bool]):
        """
        Draw the news screen for as long as cond returns True
        """
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
            # todo make scrolling_text_pos something persistent/news-specific
            # if we want to show news as part of rotation?
            # not strictly necessary but would be nice, avoids only seeing first headline over and over
            self.__update_scrolling_text_pos(pos, self.canvas.width)
            # Show network issues
            if self.data.network_issues:
                network.render_network_error(self.canvas, self.data.config.layout, self.data.config.scoreboard_colors)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(self.data.config.scrolling_speed)

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

    def __max_scroll_x(self, scroll_coords):
        scroll_max_x = scroll_coords["x"] + scroll_coords["width"]
        self.scrolling_text_pos = min(scroll_max_x, self.scrolling_text_pos)

    def __update_scrolling_text_pos(self, new_pos, end):
        """Updates the position of scrolling text"""
        pos_after_scroll = self.scrolling_text_pos - 1
        if pos_after_scroll + new_pos < 0:
            self.data.scrolling_finished = True
            if pos_after_scroll + new_pos < -10:
                self.scrolling_text_pos = end
                return
        self.scrolling_text_pos = pos_after_scroll

    def no_games_cond(self) -> bool:
        """A condition that is true only while there are no games live"""
        return not self.data.schedule.games_live()


def permanent_cond() -> bool:
    """A condition that is always true"""
    return True


def timer_cond(seconds) -> Callable[[], bool]:
    """Create a condition that is true for the specified number of seconds"""
    end = time.time() + seconds

    def cond():
        return time.time() < end

    return cond


def all_of(*conds) -> Callable[[], bool]:
    """Create a condition that is true if all of the given conditions are true"""

    def cond():
        return all(c() for c in conds)

    return cond
