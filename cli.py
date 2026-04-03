import argparse
import sys


def arguments(overrides={}):
    """Returns parsed CLI arguments, with JSON overrides baked in as parser defaults."""
    parser = _make_parser(overrides)

    # Prevent parsing errors for unittest flags
    if "unittest" in sys.modules:
        args, _ = parser.parse_known_args()
        return args

    return parser.parse_args()


def _make_parser(defaults) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    # Options for the rpi-rgb-led-matrix library
    parser.add_argument(
        "--led-rows",
        action="store",
        help="Display rows. 16 for 16x32, 32 for 32x32. (Default: 32)",
        default=defaults.get("led_rows", 32),
        type=int,
    )
    parser.add_argument(
        "--led-cols",
        action="store",
        help="Panel columns. Typically 32 or 64. (Default: 32)",
        default=defaults.get("led_cols", 32),
        type=int,
    )
    parser.add_argument(
        "--led-chain",
        action="store",
        help="Daisy-chained boards. (Default: 1)",
        default=defaults.get("led_chain", 1),
        type=int,
    )
    parser.add_argument(
        "--led-parallel",
        action="store",
        help="For Plus-models or RPi2: parallel chains. 1..3. (Default: 1)",
        default=defaults.get("led_parallel", 1),
        type=int,
    )
    parser.add_argument(
        "--led-pwm-bits",
        action="store",
        help="Bits used for PWM. Range 1..11. (Default: 11)",
        default=defaults.get("led_pwm_bits", 11),
        type=int,
    )
    parser.add_argument(
        "--led-brightness",
        action="store",
        help="Sets brightness level. Range: 1..100. (Default: 100)",
        default=defaults.get("led_brightness", 100),
        type=int,
    )
    parser.add_argument(
        "--led-gpio-mapping",
        help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm",
        choices=["regular", "adafruit-hat", "adafruit-hat-pwm"],
        default=defaults.get("led_gpio_mapping", None),
        type=str,
    )
    parser.add_argument(
        "--led-scan-mode",
        action="store",
        help="Progressive or interlaced scan. 0 = Progressive, 1 = Interlaced. (Default: 1)",
        default=defaults.get("led_scan_mode", 1),
        choices=range(2),
        type=int,
    )
    parser.add_argument(
        "--led-pwm-lsb-nanoseconds",
        action="store",
        help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. (Default: 130)",
        default=defaults.get("led_pwm_lsb_nanoseconds", 130),
        type=int,
    )
    parser.add_argument(
        "--led-show-refresh",
        action="store_true",
        help="Shows the current refresh rate of the LED panel.",
        default=defaults.get("led_show_refresh", False),
    )
    parser.add_argument(
        "--led-slowdown-gpio",
        action="store",
        help="Slow down writing to GPIO. Range: 0..4. (Default: 1)",
        default=defaults.get("led_slowdown_gpio", None),
        choices=range(5),
        type=int,
    )
    parser.add_argument(
        "--led-no-hardware-pulse",
        action="store",
        help="Don't use hardware pin-pulse generation.",
        default=defaults.get("led_no_hardware_pulse", None),
    )
    parser.add_argument(
        "--led-rgb-sequence",
        action="store",
        help="Switch if your matrix has led colors swapped. (Default: RGB)",
        default=defaults.get("led_rgb_sequence", "RGB"),
        type=str,
    )
    parser.add_argument(
        "--led-pixel-mapper",
        action="store",
        help='Apply pixel mappers. e.g "Rotate:90"',
        default=defaults.get("led_pixel_mapper", ""),
        type=str,
    )
    parser.add_argument(
        "--led-row-addr-type",
        action="store",
        help="0 = default; 1 = AB-addressed panels; 2 = direct row select; 3 = ABC-addressed panels. (Default: 0)",
        default=defaults.get("led_row_addr_type", 0),
        type=int,
        choices=[0, 1, 2, 3],
    )
    parser.add_argument(
        "--led-multiplexing",
        action="store",
        help="Multiplexing type: 0 = direct; 1 = strip; 2 = checker; 3 = spiral; 4 = Z-strip; 5 = ZnMirrorZStripe;"
        "6 = coreman; 7 = Kaler2Scan; 8 = ZStripeUneven. (Default: 0)",
        default=defaults.get("led_multiplexing", 0),
        type=int,
    )
    parser.add_argument(
        "--led-limit-refresh",
        action="store",
        help="Limit refresh rate to this frequency in Hz. Useful to keep a constant refresh rate on loaded system. "
        "0=no limit. Default: 0",
        default=defaults.get("led_limit_refresh", 0),
        type=int,
    )
    parser.add_argument(
        "--led-pwm-dither-bits",
        action="store",
        help="Time dithering of lower bits (Default: 0)",
        default=defaults.get("led_pwm_dither_bits", 0),
        type=int,
    )
    parser.add_argument(
        "--drop-privileges",
        action="store_true",
        help="Force the matrix driver to drop root privileges after setup.",
        default=defaults.get("drop_privileges", False),
    )

    # Scoreboard options
    parser.add_argument(
        "--config",
        action="store",
        help="Relative path to a custom config JSON file. Defaults to root config.json. The '.json' suffix is optional.",
        default=defaults.get("config", None),
        type=str,
    )
    parser.add_argument(
        "--emulated",
        action="store_const",
        help="Force using emulator mode over default matrix display.",
        const=True,
        default=defaults.get("emulated", False),
    )

    return parser
