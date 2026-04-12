import sys
import pathlib
import logging
import time

# hack: allow importing from parent directory
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from RGBMatrixEmulator.internal.emulator_config import RGBMatrixEmulatorConfig

from data.config import Config
from data.config.layout import Layout
from data.teams import TEAM_ID_ABBR
from data.scoreboard.team import Team
from data.uniforms import CITY_CONNECT
from renderers.games.teams import render_team_banner

RAW_CONFIG = pathlib.Path(__file__).parent / "raw_config.json"
HEIGHT = 170
WIDTH = 155


def make_layout(x, y):
    json = {
        "teams": {
            "background": {
                "away": {"width": 24, "height": 9, "x": x, "y": y},
                "home": {"width": 24, "height": 9, "x": x, "y": y + 9},
            },
            "name": {"full": False, "away": {"x": x + 4, "y": y + 7}, "home": {"x": x + 4, "y": y + 16}},
            "accent": {
                "away": {"width": 2, "height": 9, "x": x, "y": y},
                "home": {"width": 2, "height": 9, "x": x, "y": y + 9},
            },
        },
        "defaults": {"font_name": "4x6"},
    }

    return Layout(json, WIDTH, HEIGHT)


def team_matrix_options(raw=False):
    if raw:
        RGBMatrixEmulatorConfig.CONFIG_PATH = RAW_CONFIG
    options = RGBMatrixOptions()
    options.rows = HEIGHT
    options.cols = WIDTH
    return options


def draw_teams(canvas, config):
    canvas.Clear()
    for i, team in enumerate(sorted(TEAM_ID_ABBR.values())):
        team_default = Team(team, 0, "", 0, 0, "", None)
        team_cc = Team(team, 0, "", 0, 0, "", CITY_CONNECT)

        col, row = divmod(i, 6)
        layout = make_layout(row * 26, col * 19)
        render_team_banner(canvas, layout, config.team_colors, team_cc, team_default, False)

    return matrix.SwapOnVSync(canvas)


if __name__ == "__main__":
    logging.getLogger("mlbled").setLevel(logging.DEBUG)

    save = sys.argv[-1] == "save"
    if save:
        sys.argv.pop()  # remove "save" arg so it doesn't mess with config loading

    # Initialize the matrix
    matrix = RGBMatrix(options=team_matrix_options(raw=save))

    config = Config()

    canvas = matrix.CreateFrameCanvas()
    canvas = draw_teams(canvas, config)
    if save:
        canvas.display_adapter._dump_screenshot("team_colors.jpg")
    else:
        while True:
            try:
                config = Config()
            except:
                logging.exception("Error error re-loading config")
                pass
            canvas = draw_teams(canvas, config)

            time.sleep(5)
