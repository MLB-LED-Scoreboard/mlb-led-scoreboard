import data.scoreboard_config
import time
import sys

debug_enabled = False

def set_debug_status(config):
	global debug_enabled
	debug_enabled = config.debug_enabled

def __debugprint(text):
	print(text)
	sys.stdout.flush()

def log(text):
	if debug_enabled:
		__debugprint("DEBUG ({}): {}".format(__timestamp(), text))

def warning(text):
  __debugprint("WARNING ({}): {}".format(__timestamp(), text))

def error(text):
	__debugprint("ERROR ({}): {}".format(__timestamp(), text))

def info(text):
	__debugprint("INFO ({}): {}".format(__timestamp(), text))

def __timestamp():
	return time.strftime("%H:%M:%S", time.localtime())
