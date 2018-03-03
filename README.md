# mlb-led-scoreboard
An LED scoreboard for Major League Baseball. Displays a live scoreboard for your team's game on that day.

Requires a Raspberry PI and an LED board hooked up via the GPIO pins.

[![Join Slack](https://img.shields.io/badge/slack-join-blue.svg)](https://mlb-led-scoreboard.herokuapp.com/)

## Table of Contents
* [Features](#features)
  * [Live Games](#live-games)
  * [Pregame](#pregame)
  * [Division Standings](#division-standings)
* [Installation](#installation)
* [Usage](#usage)
  * [Configuration](#configuration)
  * [Flags](#flags)
* [Sources](#sources)
  * [Accuracy Disclaimer](#accuracy-disclaimer)
* [Help and Contributing](#help-and-contributing)

## Features

### Live Games
It can display live games in action, and optionally rotate every 15 seconds through each game of the day.

The board refreshes the list of games every 15 minutes.

![Cubs-Indians game](img/cubs-indians-demo.jpg) ![Pirates-Cubs game](img/pirates-cubs-demo.jpg) ![Giants-Brewers-wide game](img/wide-ingame-demo.jpg) ![Cubs-Braves Final](img/wide-final-demo.jpg)

Sometimes you don't get baseball though :(

![I hate offdays](img/offday.jpg)

### Pregame
If a game hasn't started yet, a pregame screen will be displayed with the probable starting pitchers.

![Pregame](img/pregame.gif) ![Pregame-wide](img/wide-pregame-demo.jpg)

### Division Standings
It can display standings for the provided division. Since the 32x32 board is too small to display wins and losses together, the wins and losses are alternated on the board every 5 seconds.

![standings-wins](img/standings-wins.jpg) ![standings-losses](img/standings-losses.jpg) ![standings-wide](img/wide-standings-demo.jpg)

## Installation
### Note: The installation steps are very much a WIP as I'm having more people test this out. This will update as more people adopt this software.
```
git clone --recursive https://github.com/ajbowler/mlb-led-scoreboard
cd matrix/bindings/python
```
Then follow the instructions [in that directory](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python#building). The README there will guide you through building the necessary binaries to run the Python samples (stuff like pulsing colors, running text on the screen, etc.)

**You cannot run this program until you have built the RGBMatrix binaries per the instructions in that README.**

A very important note not to forget is setting up the hardware you use. Make sure to edit the Makefile in the `lib/` directory to the right hardware description. I'm using `adafruit-hat` since I built this with an Adafruit HAT.

Then do the following:
```
cd .. # you should be in matrix/bindings now
sudo pip install -e python/
cd ../../ # you should be in mlb-led-scoreboard/ now
sudo pip install mlbgame pytz tzlocal
make
```
Basically, you're going to go back above the python binding directory, then run a pip install on that directory to create your own `rgbmatrix` module. Then go back up to the project directory and install `mlbgame`, the API this software uses to get baseball stats. You'll also install `pytz` and `tzlocal` for time zone conversions, so your pregame displays show the game start times in your local time zone. East Coast bias and all that...

Install anything else your Pi yells at you for. I needed `python-dev` and a few native extensions for other stuff. Outside of scope of this project but this should at least help point people in the right direction.

#### Time Zones
Make sure your Raspberry Pi's timezone is configured to your local time zone. They'll often have London time on them by default.

## Usage
`sudo python main.py` Running as root is 100% an absolute must, or the matrix won't render.

### Configuration

A default `config.json.example` file is included for reference. Copy this file to `config.json` and modify the values as needed.

```
"preferred_team"          String  Pick a team to display a game for. Example: "Cubs"
"preferred_division"      String  Pick a division to display standings for when display_standings is true. Example: "NL Central"
"display_standings"       Bool    Display standings for the provided preferred_division.
"rotate_games"            Bool    Rotate through each game of the day every 15 seconds.
"rotate_rates"            Dict    Dictionary of Floats. Each type of screen can use a different rotation rate. Valid types: "live", "pregame", "final".
                          Float   A Float can be used to set all screen types to the same rotate rate.
"scroll_until_finished"   Bool    If scrolling text takes longer than the rotation rate, wait to rotate until scrolling is done.
"slowdown_scrolling"      Bool    If your Pi is unable to handle the normal refresh rate while scrolling, this will slow it down.
"debug_enabled"           Bool    Game and other debug data is written to your console.
```

### Flags

You can configure your LED matrix with the same flags used in the [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) library. More information on these arguments can be found in the library documentation.
```
--led-rows                Display rows. 16 for 16x32, 32 for 32x32. (Default: 32)
--led-cols                Panel columns. Typically 32 or 64. (Default: 32)
--led-chain               Daisy-chained boards. (Default: 1)
--led-parallel            For Plus-models or RPi2: parallel chains. 1..3. (Default: 1)
--led-pwm-bits            Bits used for PWM. Range 1..11. (Default: 11)
--led-brightness          Sets brightness level. Range: 1..100. (Default: 100)
--led-gpio-mapping        Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm
--led-scan-mode           Progressive or interlaced scan. 0 = Progressive, 1 = Interlaced. (Default: 1)
--led-pwm-lsb-nanosecond  Base time-unit for the on-time in the lowest significant bit in nanoseconds. (Default: 130)
--led-show-refresh        Shows the current refresh rate of the LED panel.
--led-slowdown-gpio       Slow down writing to GPIO. Range: 0..4. (Default: 1)
--led-no-hardware-pulse   Don't use hardware pin-pulse generation.
--led-rgb-sequence        Switch if your matrix has led colors swapped. (Default: RGB)
--led-row-addr-type       0 = default; 1 = AB-addressed panels. (Default: 0)
--led-multiplexing        Multiplexing type: 0 = direct; 1 = strip; 2 = checker; 3 = spiral. (Default: 0)
```

## Sources
This project relies on two libraries:
[MLBGame](https://github.com/panzarino/mlbgame) is the Python library used for retrieving live game data.
[rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) is the library used for making everything work with the LED board and is included as a submodule, so when cloning, make sure you add `--recursive`.

### Accuracy Disclaimer
The scoreboard is dependent on MLB having their data correct and up to date. If you see any weird data such as wrong pitches or scores or whatever else, MLB is drunk.

## Help and Contributing
If you run into any issues and have steps to reproduce, open an issue. If you have a feature request, open an issue. If you want to contribute a small to medium sized change, open a pull request. If you want to contribute a new feature, open an issue first before opening a PR.

If you just want to talk, join the Slack channel, see the badge at the top of the README
