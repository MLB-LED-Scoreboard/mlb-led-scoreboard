import time
from typing import Callable, NoReturn


import debug
from data import Data, status
from data.scoreboard import Scoreboard
from data.scoreboard.postgame import Postgame
from data.scoreboard.pregame import Pregame
from data.game import Game
import data.config.layout as layout
from data.screens import ScreenType

from renderers import network, offday, standings
from renderers.games import game as gamerender
from renderers.games import irregular
from renderers.games import postgame as postgamerender
from renderers.games import pregame as pregamerender
from renderers.games import teams

# TODO(BMW) make configurable?
STANDINGS_NEWS_SWITCH_TIME = 120
STANDINGS_NEWS_ROTATION_TIME = 20  # should be multiple of 10 due to division timings


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

    def __render_offday(self, team_offday=True):
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

    def __render_standings(self):
        self.__draw_standings(permanent_cond)

        # Out of season off days don't always return standings so fall back on the news renderer
        debug.error("No standings data.  Falling back to news.")
        self.__draw_news(permanent_cond)

    # Renders a game screen based on it's status
    # May also call draw_offday or draw_standings if there are no games
    def __render_gameday(self) -> NoReturn:
        while True:
            if not self.data.schedule.games_live():
                if self.data.config.news_no_games and self.data.config.standings_no_games:
                    while self.no_games_cond():
                        self.__draw_news(timer_cond(STANDINGS_NEWS_SWITCH_TIME))
                        self.__draw_standings(timer_cond(STANDINGS_NEWS_SWITCH_TIME))
                elif self.data.config.news_no_games:
                    self.__draw_news(self.no_games_cond)
                elif self.data.config.standings_no_games:
                    self.__draw_standings(self.no_games_cond)

            self.__render_games()
            if self.data.config.rotation_include_news:
                self.__draw_news(any_of(timer_cond(STANDINGS_NEWS_ROTATION_TIME), self.scrolling_finished_cond))
            if self.data.config.rotation_include_standings:
                self.__draw_standings(timer_cond(STANDINGS_NEWS_ROTATION_TIME))

    def __render_games(self):

        # this loop is purely so that every now and then this function returns
        # which lets __render_gameday show weather/standings/etc and run its checks
        # we could also make this a timer_cond?
        for _ in range(self.data.schedule.num_games()):
            self.scrolling_text_pos = self.canvas.width
            self.scrolling_finished = False
            self.__check_acknowledgement()

            game = self.data.get_rendering_game()
            timer = timer_cond(self.data.config.rotate_rate_for_status(game))
            game_cond = self.game_cond(game)
            while any_of(
                timer,
                game_cond,
                self.scrolling_finished_cond,
            )():
                self.__update_layout_state(game)
                self.__draw_game(game)
                self.__check_acknowledgement()
                time.sleep(self.data.config.scrolling_speed)

            self.__request_next_game()

    def __request_next_game(self):
        self.data.rendering = "next"
        debug.log("Render thread: requesting main thread to read 'next' game")
        self.data.next_requested = self.data.schedule.next_game()

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

    def no_games_cond(self) -> bool:
        """A condition that is true only while there are no games live"""
        return not self.data.schedule.games_live()

    def scrolling_finished_cond(self) -> bool:
        """A condition that is true only while the scrolling text has finished scrolling"""
        return self.data.config.rotation_scroll_until_finished and not self.scrolling_finished

    def game_cond(self, game: Game) -> Callable[[], bool]:
        if not self.data.config.rotation_enabled:
            # never rotate
            return permanent_cond

        if self.data.config.rotation_preferred_team_live_enabled or not self.data.config.preferred_teams:
            # if there's no preferred team, or if we rotate during their games, always rotate
            return never_cond

        def cond():
            if status.is_live(game.status()):
                if self.data.schedule.num_games() <= 1:
                    # don't rotate if this is the only game
                    return True

                # if we're here, it means we should pause on the preferred team's games
                if game.features_team(self.data.config.preferred_teams[0]):
                    # unless we're allowed to rotate during mid-inning breaks
                    return not (
                        self.data.config.rotation_preferred_team_live_mid_inning
                        and status.is_inning_break(game.inning_state())
                    )

            # if our current game isn't live, we might as well try to rotate.
            # this should help most issues with games getting stuck
            return False

        return cond


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
