These JSON files are named in correspondence to the dimensions of the LED board used when running the software. In cases where only one of the two coordinates (x or y) are provided, this means that the other is set programmatically, usually through centering text or a loop depending on the piece being rendered.

# Custom Coordinates

You can edit these coordinates to display parts of the scoreboard in any way you choose. Simply copy the file corresponding to your board's dimensions to `w<cols>h<rows>.json`.

## Example
If you have a 64x32 board, copy `w64h32.json.example` to a new file called `w64h32.json`, then edit the coordinates in that file as you see fit. Your customized coordinates will always take precedence.
