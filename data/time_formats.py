import platform

TIME_FORMAT_24H = "%H"
TIME_FORMAT_12H = "%#I" if platform.system() == "Windows" else "%-I"
