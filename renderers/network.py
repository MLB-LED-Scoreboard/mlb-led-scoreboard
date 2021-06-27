try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from utils import center_text_position

NETWORK_ERROR_TEXT = "!"


def render_network_error(canvas, layout, colors):
    font = layout.font("network")
    coords = layout.coords("network")
    bg_coords = coords["background"]
    text_color = colors.graphics_color("network.text")
    bg_color = colors.color("network.background")

    # Fill in the background so it's clearly visible
    for x in range(bg_coords["width"]):
        for y in range(bg_coords["height"]):
            canvas.SetPixel(x + bg_coords["x"], y + bg_coords["y"], bg_color["r"], bg_color["g"], bg_color["b"])
    text = NETWORK_ERROR_TEXT
    x = center_text_position(text, coords["text"]["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], x, coords["text"]["y"], text_color, text)
