import data.scoreboard_config
import time

debug_enabled = False

def set_debug_status(config):
	global debug_enabled
	debug_enabled = config.debug_enabled

def log(text):
	if debug_enabled:
		print("DEBUG ({}): {}".format(__timestamp(), text))

def error(text):
	print("ERROR ({}): {}".format(__timestamp(), text))

def __timestamp():
	return time.strftime("%H:%M:%S", time.localtime())