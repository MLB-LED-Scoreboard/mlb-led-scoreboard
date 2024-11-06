These JSON files are used to determine the colors for pretty much every element that's renderered.

# Custom Colors

You can edit these colors to display parts of the scoreboard in any way you choose. Simply copy the file corresponding to the colors you wish to customize to the same filename without the `.example` extension. These JSON files only need to contain the parts you wish to override but it's often easier to just make a copy of the full example file and edit the values you want to change.

## Examples
If you want to edit the color of some of the teams, copy `teams.json.example` to a new file called `teams.json`, then edit the `"r"`, `"g"` and `"b"` values for the colors you wish to change in that new file. If you want to customize the color of the scrolling text on the final screen, copy `scoreboard.json.example` to `scoreboard.json` and edit the `"final"->"scrolling_text"` keys to your liking. Your customized colors will always take precedence.
