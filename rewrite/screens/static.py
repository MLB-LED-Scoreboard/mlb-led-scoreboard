import os

from PIL import Image

from screens.base import ScreenBase


class StaticScreen(ScreenBase):

    """
    This screen is used to display a static image on startup before real data is loaded.

    Outside data sources must request a transition to move away from this screen.
    """

    MIN_DURATION_SECONDS = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        dimensions = self.manager.config.dimensions
        logo_path = os.path.abspath(
            os.path.join(__file__, f"./../../assets/logo/mlb-w{dimensions[0]}h{dimensions[1]}.png")
        )

        with Image.open(logo_path) as logo:
            self.manager.matrix.SetImage(logo.convert("RGB"))

    def render(self):
        pass

    def ready_to_transition(self):
        """
        If the static load screen is displayed, then leave it on screen for a few seconds to avoid flashing.
        """
        return self.duration >= StaticScreen.MIN_DURATION_SECONDS * 1000
