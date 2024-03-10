import statsapi, sys, threading

from queue import PriorityQueue

from version import SCRIPT_NAME, SCRIPT_VERSION

from utils import args, led_matrix_options
from utils import logger as ScoreboardLogger

from screens.screen_manager import ScreenManager

from data import Data

from config import Config

import driver
from driver import RGBMatrix, __version__


statsapi_version = tuple(map(int, statsapi.__version__.split(".")))
if statsapi_version < (1, 5, 1):
    ScoreboardLogger.error("We require MLB-StatsAPI 1.5.1 or higher. You may need to re-run install.sh")
    sys.exit(1)
elif statsapi_version < (1, 6, 1):
    ScoreboardLogger.warning("We recommend MLB-StatsAPI 1.6.1 or higher. You may want to re-run install.sh")


def main(matrix):
    #TODO: Configure matrix dimensions
    ScoreboardLogger.info(f"{SCRIPT_NAME} - v#{SCRIPT_VERSION} (32x32)")

    canvas = matrix.CreateFrameCanvas()
    screen_queue = PriorityQueue(10)

    config = Config()
    screen_manager = ScreenManager(matrix, canvas, config, screen_queue)

    render_thread = threading.Thread(
        target=screen_manager.start,
        name="render_thread",
        daemon=True
    )

    render_thread.start()

    data = Data(screen_manager)
    screen_manager.connect_datasource(data)

    while render_thread.is_alive():
        pass


if __name__ == "__main__":
    command_line_args = args()
    matrix_options = led_matrix_options(command_line_args)

    matrix = RGBMatrix(options=matrix_options)

    try:
        main(matrix)
    except:
        ScoreboardLogger.exception("Untrapped error in main!")
        sys.exit(1)
    finally:
        matrix.Clear()
