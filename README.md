# mlb-led-scoreboard
An LED scoreboard for Major League Baseball. Displays a live scoreboard for your team's game on that day.

Requires a Raspberry PI and an LED board hooked up via the GPIO pins.

## Installation
Go into the matrix submodule and edit the `HARDWARE_DESC?` setting in `lib/Makefile` based on the docs. I used `adafruit-hat` since I'm using an Adafruit HAT.

Then just run `make` to get the rgbmatrix binaries.

## Usage
`python main.py <team name>`
If team name isn't provided, the Cubs are used.

## Example
`python main.py Cubs`

## Demo
Here are some images of it in action!

![image1](https://i.imgur.com/DmRXhlO.jpg)
![image2](https://i.imgur.com/wAit0Qt.jpg)


### 2017-2018 Offseason
Since it's currently the offseason I have the game hardcoded as one of the 2016 Cubs-Indians World Series games. I'll update to be "today's game" when the season starts otherwise this thing is useless.
