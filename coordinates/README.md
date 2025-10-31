These JSON files are named in correspondence to the dimensions of the LED board used when running the software. A file, located in the `coordinates` directory with a filename `w<cols>h<rows>.example.json` tells the scoreboard that those dimensions are officially supported. This `.example` file is required and you will need to copy one of the existing files into a file that matches your dimensions.

# Custom Coordinates
You can edit these coordinates to display parts of the scoreboard in any way you choose. Simply copy the file corresponding to your board's dimensions to `w<cols>h<rows>.json`. This JSON file only needs to contain the parts you wish to override but it's often easier to just make a copy of the full example file and edit the values you want to change.

## Example
If you have a 64x32 board, copy `w64h32.example.json` to a new file called `w64h32.json`, then edit the coordinates in that file as you see fit. Your customized coordinates will always take precedence.

>!WARNING
> **DO NOT** remove `.example` files! **Copy** the files instead.
>
> These are checked by the software to determine which matrix dimensions are supported. If you remove the file, the scoreboard may fail to start.

## Fonts
Any scoreboard element that prints text can accept a `"font_name"` attribute. Supported fonts need to be named with `<width>x<height>.bdf` (or `<width>x<height>B.bdf` for bold fonts). The font loader will search `assets/` first for the specified font and then it will fall back to searching `matrix/fonts/` if one was not found.

## States
The layout can have a couple of different states where things are rendered differently. Adding an object named for the layout state and giving it the same properties from the parent object will change the positioning of that parent object only when that state is found. For instance, when a game enters the `Warmup` state, the text `Warmup` appears under the time and the scrolling text is moved down.
* `warmup` will	only render on the `pregame` screen and appears when a game enters the `Warmup` status. This usually happens 15-20 minutes before a game begins.
* `nohit` and `perfect_game` will only render on the live game screen and appears when a game returns that it is currently a no hitter or perfect game and the `innings_until_display` of `nohitter` has passed.
* The `line_score` section configures the line score (RHE) on the game screen.
  * Runs are always displayed.
  * `show_hits_and_errors` toggles displaying hits and errors.
  * `compress_digits` will reduce the space between digits when the number of runs or hits is > 9.
  * `spacing` is the number of pixels between the runs/hits and hits/errors.
  * When the line score is high (greater than 3 total digits), use `teams.name.shorten_on_high_line_score` to shorten team names to prevent overflow.

## Pitch Data
* `enabled` (true/false) Turn feature on/off
* `mph` (true/false) When rendering pitch speed add mph after (99 mph)
* `desc_length` (short/long) The short or long pitch type description, you can change both the short and long description to your liking in data/pitches as long as you do not change the index value.

## Play Result
* `enabled` (true/false) Turn feature on/off
* `desc_length` (short/long) The short or long play result description.

## Team Records During Games
Team records can be displayed on the team banner during most game states, such as pregame, live, and postgame.
* `enabled` (true/false) Turn feature on/off
* `position` (absolute/relative) Defines origin of the text. When `absolute`, the origin is always `(0, 0)`. When `relative`, the origin is relative to the end of the team name in the banner.

## Updates
The software develops and releases features with full support for the default layouts, so custom layouts may look unsatisfactory if you update to later versions of the scoreboard. If you as a user decide to create a custom layout file, you are responsible for tweaking the coordinates to your liking with each update.

## Current Issues
A couple of things are not completely implemented or have some implementation details you should understand.

* `bases` currently requires an even `size` value to be rendered correctly
* Not all options are enabled on all board sizes by default. For example pitch count and pitch type are not enabled by default on boards smaller than 64x64. Options are "disabled" by forcing them to render outside the board, by setting X and Y coordinates less than 0 or greater than the height or width of the board.

