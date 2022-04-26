# Fonts

The scoreboard attempts to render a backwards K (`ꓘ` -- unicode A4D8) whenever a batter strikes out looking.

The scoreboard patches all the default fonts found in `rpi-rgb-led-matrix`. You can find patched fonts located in `assets/fonts/patched`.

If you are using a custom font, most likely it does not include this special character.

## Including `ꓘ`

If you would like to add `uniA4D8` support for a custom font you are using, it's usually as simple as horizontally mirroring the standard K character (italic fonts typically do not work well). In BDF fonts, you can do this as follows. `4x6.bdf` will be used as an example.

1. Locate the K `STARTCHAR` tag in your font file:

```
STARTCHAR K
ENCODING 75
SWIDTH 1000 0
DWIDTH 4 0
BBX 3 5 0 0
BITMAP
A0
A0
C0
A0
A0
ENDCHAR
```

2. Create a copy of this character, changing the `STARTCHAR` and `ENCODING` to the correct values:

```
STARTCHAR uniA4D8
ENCODING 42200
SWIDTH 1000 0
DWIDTH 4 0
BBX 3 5 0 0
BITMAP
A0
A0
C0
A0
A0
ENDCHAR
```

3. Horizontally mirror the bitmap. You can convert the hex values by hand, or find one of the tools exist to convert this for you. Bear in mind the latest BDF 2.2 specification was introduced in 1993, so tooling may be limited.

4. Increment the `CHARS` tag to include the correct number of characters.

```
CHARS 206 -> CHARS 207
```

5. Save the file and restart the scoreboard.
