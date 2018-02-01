# mlb-led-scoreboard
An LED scoreboard for Major League Baseball. Displays a live scoreboard for your team's game on that day.

Requires a Raspberry PI and an LED board hooked up via the GPIO pins.

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
`python main.py <team name>`
If team name isn't provided, the Cubs are used.

If you want to rotate through the games of the day, supply a `--rotate` or `-r` flag as a second argument. Currently you must also provide a starting team as the first argument, this will change in the future.

The display will go to the next game every 15 seconds.

`python main.py Cardinals --rotate`

## Example
`python main.py Cubs`

## Sources
This project relies on two libraries:
[MLBGame](https://github.com/panzarino/mlbgame) is the Python library used for retrieving live game data.
[rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) is the library used for making everything work with the LED board and is included as a submodule, so when cloning, make sure you add `--recursive`.

## 2017-2018 Offseason
Since it's currently the offseason I have the game hardcoded as one of the 2016 Cubs-Indians World Series games. I'll update to be "today's game" when the season starts otherwise this thing is useless. I can't guarantee accurate data until it starts either.

## Demo
Here are some images of it in action!

![image1](https://i.imgur.com/DmRXhlO.jpg)
![image2](https://i.imgur.com/wAit0Qt.jpg)
