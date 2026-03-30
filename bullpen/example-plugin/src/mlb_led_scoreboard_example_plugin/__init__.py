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
        self.layout = layout
        self.colors = colors

    def wait_time(self) -> float:
        return 0.5

    def render(self, data: Data, canvas: "Canvas", graphics: api.renderer.graphics, scrolling_text_pos: int) -> None:
        canvas.Fill(255, 0, 0)
        graphics.DrawText(
            canvas,
            self.layout.font("network")["font"],
            0,
            10,
            self.colors.graphics_color("network.text"),
            f"Counter: {data.counter}",
        )


def load() -> tuple[type[Config], type[Data], type[Renderer]]:
    return Config, Data, Renderer
