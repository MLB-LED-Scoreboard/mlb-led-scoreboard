#!/usr/bin/env python3
"""
HomeKit bridge for the MLB LED Scoreboard.

Exposes the scoreboard as a HomeKit lightbulb with on/off and brightness
controls. Launches main.py as a subprocess and communicates state via
a shared JSON file.

Usage:
    sudo python3 homekit_bridge.py [--led-* args for main.py]
"""

import logging
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_LIGHTBULB

from homekit_control import write_control_state

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("homekit_bridge")

PERSIST_DIR = Path.home() / ".homekit-scoreboard"
PERSIST_FILE = PERSIST_DIR / "accessory.state"


class ScoreboardLightbulb(Accessory):
    category = CATEGORY_LIGHTBULB

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._on = True
        self._brightness = 100

        svc = self.add_preload_service("Lightbulb", chars=["On", "Brightness"])
        self.char_on = svc.configure_char("On", value=self._on, setter_callback=self._set_on)
        self.char_brightness = svc.configure_char("Brightness", value=self._brightness, setter_callback=self._set_brightness)

        # Write initial state
        write_control_state(self._on, self._brightness)

    def _set_on(self, value):
        self._on = bool(value)
        log.info("HomeKit: on = %s", self._on)
        write_control_state(self._on, self._brightness)

    def _set_brightness(self, value):
        self._brightness = int(value)
        log.info("HomeKit: brightness = %d", self._brightness)
        write_control_state(self._on, self._brightness)


def main():
    # Ensure persistence directory exists
    PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    # Start the scoreboard subprocess, passing through all CLI args
    scoreboard_cmd = [sys.executable, str(Path(__file__).parent / "main.py")] + sys.argv[1:]
    log.info("Starting scoreboard: %s", " ".join(scoreboard_cmd))
    scoreboard_proc = subprocess.Popen(scoreboard_cmd)

    # Set up the HomeKit accessory driver
    driver = AccessoryDriver(
        port=51826,
        persist_file=str(PERSIST_FILE),
        pincode=b"123-45-678",
    )
    accessory = ScoreboardLightbulb(driver, "MLB Scoreboard")
    driver.add_accessory(accessory)

    def shutdown(signum, frame):
        log.info("Received signal %s, shutting down...", signum)
        driver.stop()
        scoreboard_proc.terminate()
        try:
            scoreboard_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            scoreboard_proc.kill()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    log.info("HomeKit bridge starting on port 51826 (pincode: 123-45-678)")
    log.info("Open the Home app and add an accessory to pair.")

    try:
        driver.start()
    finally:
        # Ensure scoreboard is stopped when the driver exits
        if scoreboard_proc.poll() is None:
            scoreboard_proc.terminate()
            try:
                scoreboard_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                scoreboard_proc.kill()


if __name__ == "__main__":
    main()
