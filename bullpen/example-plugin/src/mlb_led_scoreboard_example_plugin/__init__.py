from typing import TYPE_CHECKING

import bullpen

if TYPE_CHECKING:
    from RGBMatrixEmulator.emulation.canvas import Canvas
    from RGBMatrixEmulator import graphics


class Config(bullpen.Config):
    def __init__(self, config_json) -> None:
        self.config_json = config_json


class Data(bullpen.PluginData):
    def __init__(self, config: Config) -> None:
        self.config = config
        self.counter = 0

    def update(self) -> bullpen.UpdateStatus:
        self.counter += 1
        return bullpen.UpdateStatus.SUCCESS


class Renderer(bullpen.Renderer):
    def __init__(self, config: Config, layout: bullpen.Layout, colors: bullpen.Color, scrolling_speed: float) -> None:
        self.config = config
        self.layout = layout
        self.colors = colors
        self.scrolling_speed = scrolling_speed

    def wait_time(self) -> float:
        return self.scrolling_speed

    def render(self, data: Data, canvas: "Canvas", graphics: "graphics", scrolling_text_pos: int) -> int:
        canvas.Fill(255, 0, 0)
        graphics.DrawText(
            canvas,
            self.layout.font("network")["font"],
            0,
            10,
            self.colors.graphics_color("network.text"),
            f"Counter: {data.counter}",
        )
        return 0


def load() -> tuple[type[Config], type[Data], type[Renderer]]:
    return Config, Data, Renderer
