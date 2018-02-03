# mlb-led-scoreboard
An LED scoreboard for Major League Baseball. Displays a live scoreboard for your team's game on that day.

Requires a Raspberry PI and an LED board hooked up via the GPIO pins.

## Features

### Live Games
It can display live games in action, and optionally rotate every 15 seconds through each game of the day.

![Cubs-Indians game](img/cubs-indians-demo.jpg) ![Pirates-Cubs game](img/pirates-cubs-demo.jpg)

### Division Standings
It can display standings for the provided division. Since the 32x32 board is too small to display wins and losses together, the wins and losses are alternated on the board every 5 seconds.

I've got a shitty camera for this board so squint if it's not too clear. It looks much better in person ¯\\___(ツ)___/¯

![standings-wins](img/standings-wins.jpg) ![standings-losses](img/standings-losses.jpg)

## Installation
```
git clone --recursive https://github.com/ajbowler/mlb-led-scoreboard
pip install mlbgame
```
Install anything else your Pi yells at you for. I needed `python-dev` and a few native extensions for other stuff. Outside of scope of this project but this should at least help point people in the right direction.

### Build the RGBMatrix binaries
Go into the matrix submodule and edit the `HARDWARE_DESC?` setting in `lib/Makefile` based on the docs. I used `adafruit-hat` since I'm using an Adafruit HAT.

Go back up to the root directory (`mlb-led-scoreboard/`) and run `make` to get the RGBMatrix binaries.

## Usage
`python main.py` You might have to sudo for the matrix to work.

## Example
If you want to just display the game for your team that day, just supply that team. If it's a team like Red Sox, encase it in quotes "Red Sox" so the team is picked up as one command line argument.

`python main.py -t Cubs` or `python main.py -t "Red Sox"`

Passing in a `-r` or `--rotate` flag will rotate through each game of the day every 15 seconds. If you passed a team in, it will start with that game, otherwise it will start with the first game in the list that MLB returned.

To display the standings for a division, supply your division's name.

`python main.py -s "NL Central"` Make sure you follow the format of `NL/AL West/Central/East`

See below for more usage options.

### Flags
```
-h, --help                Show this help message and exit
-t TEAM, --team TEAM      Pick a team to display a game for. Example: "Cubs"
-r, --rotate              Rotate through each game of the day every 15 seconds
-s, --standings DIVISION  Display standings for the provided division. Example: "NL Central"
```

## Sources
This project relies on two libraries:
[MLBGame](https://github.com/panzarino/mlbgame) is the Python library used for retrieving live game data.
[rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) is the library used for making everything work with the LED board and is included as a submodule, so when cloning, make sure you add `--recursive`.

## 2017-2018 Offseason
Since it's currently the offseason I'm hardcoding everything to random games for testing purposes. I'll update to be "today's game" when the season starts otherwise this thing is useless. I can't guarantee accurate data until it starts either.
