import argparse, os, json

from utils import logger as ScoreboardLogger

from collections.abc import Mapping


def args():
    parser = argparse.ArgumentParser()

    # Options for the rpi-rgb-led-matrix library
    parser.add_argument(
        "--led-rows",
        action="store",
        help="Display rows. 16 for 16x32, 32 for 32x32. (Default: 32)",
        default=32,
        type=int,
    )
    parser.add_argument(
        "--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 32)", default=32, type=int
    )
    parser.add_argument("--led-chain", action="store", help="Daisy-chained boards. (Default: 1)", default=1, type=int)
    parser.add_argument(
        "--led-parallel",
        action="store",
        help="For Plus-models or RPi2: parallel chains. 1..3. (Default: 1)",
        default=1,
        type=int,
    )
    parser.add_argument(
        "--led-pwm-bits", action="store", help="Bits used for PWM. Range 1..11. (Default: 11)", default=11, type=int
    )
    parser.add_argument(
        "--led-brightness",
        action="store",
        help="Sets brightness level. Range: 1..100. (Default: 100)",
        default=100,
        type=int,
    )
    parser.add_argument(
        "--led-gpio-mapping",
        help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm",
        choices=["regular", "adafruit-hat", "adafruit-hat-pwm"],
        type=str,
    )
    parser.add_argument(
        "--led-scan-mode",
        action="store",
        help="Progressive or interlaced scan. 0 = Progressive, 1 = Interlaced. (Default: 1)",
        default=1,
        choices=range(2),
        type=int,
    )
    parser.add_argument(
        "--led-pwm-lsb-nanoseconds",
        action="store",
        help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. (Default: 130)",
        default=130,
        type=int,
    )
    parser.add_argument(
        "--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel."
    )
    parser.add_argument(
        "--led-slowdown-gpio",
        action="store",
        help="Slow down writing to GPIO. Range: 0..4. (Default: 1)",
        choices=range(5),
        type=int,
    )
    parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation.")
    parser.add_argument(
        "--led-rgb-sequence",
        action="store",
        help="Switch if your matrix has led colors swapped. (Default: RGB)",
        default="RGB",
        type=str,
    )
    parser.add_argument(
        "--led-pixel-mapper", action="store", help='Apply pixel mappers. e.g "Rotate:90"', default="", type=str
    )
    parser.add_argument(
        "--led-row-addr-type",
        action="store",
        help="0 = default; 1 = AB-addressed panels; 2 = direct row select; 3 = ABC-addressed panels. (Default: 0)",
        default=0,
        type=int,
        choices=[0, 1, 2, 3],
    )
    parser.add_argument(
        "--led-multiplexing",
        action="store",
        help="Multiplexing type: 0 = direct; 1 = strip; 2 = checker; 3 = spiral; 4 = Z-strip; 5 = ZnMirrorZStripe;"
        "6 = coreman; 7 = Kaler2Scan; 8 = ZStripeUneven. (Default: 0)",
        default=0,
        type=int,
    )
    parser.add_argument(
        "--led-limit-refresh",
        action="store",
        help="Limit refresh rate to this frequency in Hz. Useful to keep a constant refresh rate on loaded system. "
        "0=no limit. Default: 0",
        default=0,
        type=int,
    )
    parser.add_argument(
        "--led-pwm-dither-bits",
        action="store",
        help="Time dithering of lower bits (Default: 0)",
        default=0,
        type=int,
    )
    parser.add_argument(
        "--config",
        action="store",
        help="Base file name for config file. Can use relative path, e.g. config/rockies.config",
        default="config",
        type=str,
    )
    parser.add_argument(
        "--emulated", action="store_const", help="Force using emulator mode over default matrix display.", const=True
    )
    return parser.parse_args()


def led_matrix_options(args):
    from driver import RGBMatrixOptions

    options = RGBMatrixOptions()

    if args.led_gpio_mapping is not None:
        options.hardware_mapping = args.led_gpio_mapping

    options.rows = args.led_rows
    options.cols = args.led_cols
    options.chain_length = args.led_chain
    options.parallel = args.led_parallel
    options.row_address_type = args.led_row_addr_type
    options.multiplexing = args.led_multiplexing
    options.pwm_bits = args.led_pwm_bits
    options.brightness = args.led_brightness
    options.scan_mode = args.led_scan_mode
    options.pwm_lsb_nanoseconds = args.led_pwm_lsb_nanoseconds
    options.led_rgb_sequence = args.led_rgb_sequence

    try:
        options.pixel_mapper_config = args.led_pixel_mapper
    except AttributeError:
        ScoreboardLogger.warning("Your compiled RGB Matrix Library is out of date.")
        ScoreboardLogger.warning("The --led-pixel-mapper argument will not work until it is updated.")

    try:
        options.pwm_dither_bits = args.led_pwm_dither_bits
    except AttributeError:
        ScoreboardLogger.warning("Your compiled RGB Matrix Library is out of date.")
        ScoreboardLogger.warning("The --led-pwm-dither-bits argument will not work until it is updated.")

    try:
        options.limit_refresh_rate_hz = args.led_limit_refresh
    except AttributeError:
        ScoreboardLogger.warning("Your compiled RGB Matrix Library is out of date.")
        ScoreboardLogger.warning("The --led-limit-refresh argument will not work until it is updated.")

    if args.led_show_refresh:
        options.show_refresh_rate = 1

    if args.led_slowdown_gpio is not None:
        options.gpio_slowdown = args.led_slowdown_gpio

    if args.led_no_hardware_pulse:
        options.disable_hardware_pulsing = True

    return options


def read_json(path):
    """
    Read a file expected to contain valid JSON to dict.

    If the file is not present returns an empty dict.
    """
    j = {}
    if os.path.isfile(path):
        j = json.load(open(path))
    else:
        ScoreboardLogger.info(f"Could not find json file {path}. Skipping.")
    return j


def deep_update(reference, overrides):
    """
    Performs a deep merge of two dicts.

    If the key is not present in the reference, the override is ignored.
    """
    for key, value in list(overrides.items()):
        if isinstance(value, Mapping) and value:
            returned = deep_update(reference.get(key, {}), value)
            reference[key] = returned
        else:
            reference[key] = overrides[key]

    return reference
