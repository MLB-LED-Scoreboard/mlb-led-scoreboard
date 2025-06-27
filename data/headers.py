# Headers to be sent on each statsapi.get()
# call.

import version

# TODO (NMS): Detect rpi hardware.  Inject gzip headers only for
#             rpi's >=3 or emulator.




API_HEADERS = {
    'Accept-Encoding': 'gzip',
    'User-Agent': 'MLB-LED-Scoreboard/' + version.SCRIPT_VERSION,
}
