from screens.base import ScreenBase
from screens.components.team import TeamBanner


class GameScreen(ScreenBase):
    class MissingGame(Exception):
        pass

    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.game = game

        if self.game is None:
            raise GameScreen.MissingGame("Game screens cannot be instantiated without a game object!")

        self.away_team_banner = TeamBanner("away", self)
        self.home_team_banner = TeamBanner("home", self)
