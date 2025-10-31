import platform


WINDOWS_DISABLE_PADDING_SYMBOL = "#"
DEFAULT_DISABLE_PADDING_SYMBOL = "-"

def os_datetime_format(format_str):
    '''
    Converts Windows-based strftime() format code to a Unix code and vice versa.
    For example, datetime.date(2025, 1, 1).strftime() with a format string '%Y %m %d'
    left pads the month/day with zeros to two digits, resulting in '2025 01 01'.

    Unix systems disable zero padding with '-', while Windows does so with '#'.
    If the format string has an incompatible character, strftime() can fail.

    The following format strings are equivalent, and both result in to '2025 1 1'.

      Windows : '%Y %#m %#d'
      Unix    : '%Y %-m %-d'
    '''
    if platform.system() == "Windows":
        return format_str.replace(DEFAULT_DISABLE_PADDING_SYMBOL, WINDOWS_DISABLE_PADDING_SYMBOL)
    else:
        return format_str.replace(WINDOWS_DISABLE_PADDING_SYMBOL, DEFAULT_DISABLE_PADDING_SYMBOL)

TIME_FORMAT_12H = os_datetime_format("%-I")
TIME_FORMAT_24H = "%H"
