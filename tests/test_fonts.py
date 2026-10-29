import os, re, unittest
from data.config.layout import Layout, FONTNAME_DEFAULT, FONTNAME_KEY, DIR_FONT_PATCHED


class TestLayout(unittest.TestCase):

    def test_font_sizes_parsed_correctly(self):
        pattern = re.compile("((\\d+).*x(\\d+).*\\.bdf)")

        for font in os.listdir(DIR_FONT_PATCHED):
            res = re.search(pattern, font)

            if res:
                fn = res.group(1)
                x = res.group(2)
                y = res.group(3)

                with self.subTest(font=font):
                    layout = Layout(
                        {"defaults": {FONTNAME_KEY: FONTNAME_DEFAULT}, "test": {FONTNAME_KEY: fn.split(".bdf")[0]}},
                        32,
                        32,
                    )

                    font = layout.font("test")

                    self.assertEqual(font.width, int(x))
                    self.assertEqual(font.height, int(y))
