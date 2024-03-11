from screens.base import ScreenBase


class GameScreen(ScreenBase):
    class MissingGame(Exception):
        pass

    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.game = game

        if self.game is None:
            raise GameScreen.MissingGame("Game screens cannot be instantiated without a game object!")
