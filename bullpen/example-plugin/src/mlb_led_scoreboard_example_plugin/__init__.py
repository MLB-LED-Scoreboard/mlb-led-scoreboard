from typing import TYPE_CHECKING

import bullpen.api as api

if TYPE_CHECKING:
    from RGBMatrixEmulator.emulation.canvas import Canvas


class Config(api.PluginConfig):
    def __init__(self, base: api.MLBConfig) -> None:
        self.step = base.plugin_config.get("step", 1)


class Data(api.PluginData):
    def __init__(self, config: Config) -> None:
        self.config = config
        self.counter = 0

    def update(self, force: bool = False) -> api.UpdateStatus:
        self.counter += self.config.step
        return api.UpdateStatus.SUCCESS


class Renderer(api.PluginRenderer):
    def __init__(self, config: Config, layout: api.Layout, colors: api.Color) -> None:
        self.config = config
        self.colors = colors

        self.font = layout.font("example.font")
        self.bg = (255, 0, 0)

    def wait_time(self) -> float:
        return 0.5

    def render(self, data: Data, canvas: "Canvas", graphics: api.renderer.graphics, scrolling_text_pos: int) -> None:
        canvas.Fill(*self.bg)
        graphics.DrawText(
            canvas,
            self.font["font"],
            0,
            10,
            graphics.Color(255, 255, 255),
            f"Counter: {data.counter}",
        )


def load() -> api.PLUGIN_DEFINITION:
    return Config, Data, Renderer
