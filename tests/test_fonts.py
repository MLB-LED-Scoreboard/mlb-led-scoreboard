import os, re, unittest
from data.config.layout import Layout, FONTNAME_DEFAULT, FONTNAME_KEY, DIR_FONT_PATCHED

class TestLayout(unittest.TestCase):

    def test_get_font_object_structure(self):
        layout = Layout({
            "defaults": {
                FONTNAME_KEY: FONTNAME_DEFAULT
            },
            "test": {
                FONTNAME_KEY: "4x6"
            }
        }, 32, 32)

        font_dict = layout.font("test")

        self.assertEqual(font_dict["size"], { "width": 4, "height": 6 })

        # Will be an absolute path, OS-dependent
        font_path = str(os.path.abspath("assets/fonts/patched/4x6.bdf"))
        self.assertIn(font_path, font_dict["path"])
        # BDF metadata that is nice to have, but not critical what it contains
        self.assertIn("bdf_headers", font_dict)
        # Handled differently in HW/Sw
        self.assertIn("font", font_dict)

    def test_font_sizes_parsed_correctly(self):
        pattern = re.compile("((\\d+).*x(\\d+).*\\.bdf)")

        for font in os.listdir(DIR_FONT_PATCHED):
            res = re.search(pattern, font)

            if res:
                fn = res.group(1)
                x = res.group(2)
                y = res.group(3)

                with self.subTest(font=font):
                    layout = Layout({
                        "defaults": {
                            FONTNAME_KEY: FONTNAME_DEFAULT
                        },
                        "test": {
                            FONTNAME_KEY: fn.split(".bdf")[0]
                        }
                    }, 32, 32)

                    font_dict = layout.font("test")

                    self.assertEqual(font_dict["size"], { "width": int(x), "height": int(y) })