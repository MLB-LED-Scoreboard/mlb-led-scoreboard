These JSON files are named in correspondence to the dimensions of the LED board used when running the software. 

# Custom Coordinates

You can edit these coordinates to display parts of the scoreboard in any way you choose. Simply copy the file corresponding to your board's dimensions to `w<cols>h<rows>.json`.

## Example
If you have a 64x32 board, copy `w64h32.json.example` to a new file called `w64h32.json`, then edit the coordinates in that file as you see fit. This JSON file only needs to contain the parts you wish to override but it's often easier to just make a copy of the full example file and edit the values you want to change. Your customized coordinates will always take precedence.

## Current Issues
A couple of things are not completely implemented but are planned for a near future release.

* Setting the `width` of the scrolling text is not currently available
* `nohit` and `perfect_game` have been added to the json but aren't currently implemented