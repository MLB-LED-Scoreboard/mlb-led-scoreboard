import argparse
import sys


class ScoreboardCLI:
    def __init__(self):
        self.parser = self.__make_parser()

    def arguments(self) -> argparse.Namespace:
        """Returns the parsed CLI arguments as a Namespace."""
        if "unittest" in sys.modules:
            # If in test and instantiate a config, only parse the known flags to avoid crashes.
            args, _ = self.parser.parse_known_args()
            return args

        return self.parser.parse_args()

    def canonical_arguments(self, json_data: dict = {}) -> argparse.Namespace:
        """
        Creates arguments in priority order:
            user-specified CLI flags > JSON configuration flags > CLI defaults.

        `json_data` should have keys corresponding to normalized CLI flag names (i.e. `--flag-name=123` -> `flag_name`).
        Any key present there overrides the parser default. Any flag explicitly passed on the command line wins over both.

        Returns arguments as a Namespace.
        """
        defaults = vars(self.default_arguments())
        clargs = vars(self.arguments())

        argv_flags = {self.__normalize(f) for f in sys.argv}

        config_flags = {flag: json_data[flag] for flag in defaults if flag in json_data}
        explicit_flags = {flag: clargs[flag] for flag in defaults if flag in argv_flags}

        return argparse.Namespace(**(defaults | config_flags | explicit_flags))

    def default_arguments(self) -> argparse.Namespace:
        """Returns a Namespace populated entirely with parser defaults, ignoring sys.argv."""
        return self.parser.parse_args([])

    @staticmethod
    def __normalize(flag) -> str:
        """Converts a flag `--flag-name=123` into a normalized `flag_name`"""
        return flag.strip("-").split("=")[0].replace("-", "_")

    def __make_parser(self) -> argparse.ArgumentParser:
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
        parser.add_argument(
            "--led-chain", action="store", help="Daisy-chained boards. (Default: 1)", default=1, type=int
        )
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
            help="Relative path to a custom config JSON file. Defaults to root config.json. The '.json' suffix is optional.",
            default=None,
            type=str,
        )
        parser.add_argument(
            "--emulated",
            action="store_const",
            help="Force using emulator mode over default matrix display.",
            const=True,
        )
        parser.add_argument(
            "--drop-privileges",
            action="store_true",
            help="Force the matrix driver to drop root privileges after setup.",
        )

        return parser
