import os

from PIL import Image

from screens.base import ScreenBase


class StaticScreen(ScreenBase):

    """
    This screen is used to display a static image on startup before real data is loaded.
    """

    MIN_DURATION_SECONDS = 3

    # TODO: Pull this from config.
    LOGO_PATH = os.path.abspath(os.path.join(__file__, "./../../assets/logo/mlb-w32h32.png"))

    def __init__(self, *args):
        super(self.__class__, self).__init__(*args)

        with Image.open(self.LOGO_PATH) as logo:
            self.manager.matrix.SetImage(logo.convert("RGB"))

    def render(self):
        pass

    def ready_to_transition(self):
        """
        If the static load screen is displayed, then leave it on screen for a few seconds to avoid flashing.
        """
        return self.duration >= self.MIN_DURATION_SECONDS * 1000
