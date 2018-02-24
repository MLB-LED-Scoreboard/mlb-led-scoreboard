import data.scoreboard_config
import time

debug_enabled = False

def set_debug_status(config):
	global debug_enabled
	debug_enabled = config.debug_enabled

def log(text):
	timestr = time.strftime("%H:%M:%S", time.localtime())
	if debug_enabled:
		print("DEBUG (" + timestr + "): " + str(text))
