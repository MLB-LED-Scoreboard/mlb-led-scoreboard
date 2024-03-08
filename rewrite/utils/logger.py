import logging

logger = logging.getLogger("mlbled")
fmter = logging.Formatter("{levelname} ({asctime}): {message}", style="{", datefmt="%H:%M:%S")
strmhdl = logging.StreamHandler()
strmhdl.setFormatter(fmter)
logger.addHandler(strmhdl)
logger.propagate = False

info = logger.info
warning = logger.warning
error = logger.error
log = logger.debug
exception = logger.exception
