# Custom Colors

These JSON files are used to determine the colors for pretty much every element that's renderered.

You can edit these colors to display parts of the scoreboard in any way you choose. Simply copy the file corresponding to the colors you wish to customize to the same filename without the `.example` extension. These JSON files only need to contain the parts you wish to override but it's often easier to just make a copy of the full example file and edit the values you want to change.

> [!WARNING]
> **DO NOT** edit or remove `.example.json` or `.schema.json` files!
>
> These are checked by the software to determine default colors. If you remove the file, the scoreboard may fail to start.

## Examples
If you want to edit the color of some of the teams, copy `teams.example.json` to a new file called `teams.json`, then edit the `"r"`, `"g"` and `"b"` values for the colors you wish to change in that new file. If you want to customize the color of the scrolling text on the final screen, copy `scoreboard.example.json` to `scoreboard.json` and edit the `"final"->"scrolling_text"` keys to your liking. Your customized colors will always take precedence.
