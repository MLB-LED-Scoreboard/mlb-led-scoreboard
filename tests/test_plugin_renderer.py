import time
import unittest
from typing import Optional
from unittest.mock import MagicMock, patch

from bullpen.api import PluginRenderer, PluginData, UpdateStatus
from renderers.main import MainRenderer, timer_cond


class StubData(PluginData):
    def __init__(self, config=None):
        pass

    def update(self, force: bool = False) -> UpdateStatus:
        return UpdateStatus.SUCCESS


class BasePlugin(PluginRenderer[StubData]):
    def __init__(self, config=None, layout=None, colors=None):
        pass

    def wait_time(self) -> float:
        return 0

    def render(self, data, canvas, graphics, scrolling_text_pos) -> Optional[int]:
        return None


class TestPluginDataIsActive(unittest.TestCase):
    def test_is_active_true_by_default(self):
        self.assertTrue(StubData().is_active)

    def test_is_active_can_be_set_false(self):
        data = StubData()
        data.is_active = False
        self.assertFalse(data.is_active)


class TestDrawPluginScreen(unittest.TestCase):
    def _make_renderer(self, plugin, data=None):
        matrix = MagicMock()
        canvas = MagicMock()
        canvas.width = 64
        matrix.CreateFrameCanvas.return_value = canvas
        matrix.SwapOnVSync.return_value = canvas

        stub_data = data or StubData()
        mock_data = MagicMock()
        mock_data.config.rotation_screen_rules = {}
        mock_data.network_issues = False
        mock_data.plugin_data = {"test": stub_data}

        return MainRenderer(matrix, mock_data, {"test": plugin}), stub_data

    def test_render_loop_skipped_when_is_active_false(self):
        plugin = BasePlugin()
        plugin.render = MagicMock(return_value=None)
        r, data = self._make_renderer(plugin)
        data.is_active = False

        with patch("driver.graphics", MagicMock(), create=True):
            r._MainRenderer__draw_plugin_screen("test", lambda: True)

        plugin.render.assert_not_called()

    def test_render_loop_skipped_when_can_render_false(self):
        class NoRenderPlugin(BasePlugin):
            def can_render(self, data):
                return False

        plugin = NoRenderPlugin()
        plugin.render = MagicMock(return_value=None)
        r, _ = self._make_renderer(plugin)

        with patch("driver.graphics", MagicMock(), create=True):
            r._MainRenderer__draw_plugin_screen("test", lambda: True)

        plugin.render.assert_not_called()

    def test_render_loop_runs_when_active_and_can_render(self):
        call_count = 0

        class ActivePlugin(BasePlugin):
            def render(self, data, canvas, graphics, pos):
                nonlocal call_count
                call_count += 1
                return None

        plugin = ActivePlugin()
        r, _ = self._make_renderer(plugin)

        with patch("driver.graphics", MagicMock(), create=True):
            r._MainRenderer__draw_plugin_screen("test", timer_cond(0.05))

        self.assertGreater(call_count, 0)

    def test_reset_called_after_loop(self):
        plugin = BasePlugin()
        plugin.reset = MagicMock()
        r, _ = self._make_renderer(plugin)

        with patch("driver.graphics", MagicMock(), create=True):
            r._MainRenderer__draw_plugin_screen("test", lambda: False)

        plugin.reset.assert_called_once()


if __name__ == "__main__":
    unittest.main()
