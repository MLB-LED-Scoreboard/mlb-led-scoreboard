These JSON files are named in correspondence to the dimensions of the LED board used when running the software. A file, located in the `ledcoords` directory with a filename `w<cols>h<rows>.json.example` tells the scoreboard that those dimensions are officially supported. This `.example` file is required and you will need to copy one of the existing files into a file that matches your dimensions.

# Custom Coordinates

You can edit these coordinates to display parts of the scoreboard in any way you choose. Simply copy the file corresponding to your board's dimensions to `w<cols>h<rows>.json`. This JSON file only needs to contain the parts you wish to override but it's often easier to just make a copy of the full example file and edit the values you want to change.

## Example
If you have a 64x32 board, copy `w64h32.json.example` to a new file called `w64h32.json`, then edit the coordinates in that file as you see fit. Your customized coordinates will always take precedence.

## Current Issues
A couple of things are not completely implemented or have some implementation details you should understand.

* Setting the `width` of the scrolling text is not currently available
* `nohit` and `perfect_game` have been added to the json but aren't currently implemented
* `bases` currently requires an even `size` value to be rendered correctly

## Performance
Larger sized fonts increase the load on the CPU and slow things down considerably. Use caution when attempting to use larger fonts.