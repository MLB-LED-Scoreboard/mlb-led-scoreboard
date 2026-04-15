"""
Adapter for the Adafruit PioMatter library for Raspberry Pi 5.
This provides compatibility with the mlb-led-scoreboard using the new Pi 5 driver.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from driver.base import MatrixDriverBase, GraphicsBase


class PioMatterMatrixAdapter(MatrixDriverBase):
    """Adapter for the Adafruit PioMatter library (Raspberry Pi 5)."""

    def __init__(self, options):
        """Initialize using the PioMatter library."""
        import adafruit_blinka_raspberry_pi5_piomatter as piomatter

        # Extract dimensions from options
        width = options.cols * options.chain_length
        height = options.rows * options.parallel

        # Determine number of address lines based on panel rows
        # 64x32 panels typically use 1/16 scan = 4 address lines
        # 64x64 panels typically use 1/32 scan = 5 address lines
        panel_rows = options.rows  # Single panel height
        n_addr_lines = {
            16: 4,   # 1/16 scan
            32: 4,   # 1/16 scan (most common for 64x32 panels)
            64: 5    # 1/32 scan
        }.get(panel_rows, 4)  # Default to 4 address lines

        # Create geometry - use total display dimensions
        # For a single 64x32 panel: width=64, height=32
        # PioMatter's geometry describes the overall display configuration
        self._geometry = piomatter.Geometry(
            width=width,  # Total width (cols * chain)
            height=height,  # Total height (rows * parallel)
            n_addr_lines=n_addr_lines,
            rotation=piomatter.Orientation.Normal
        )

        # Create PIL canvas
        self._canvas = Image.new('RGB', (width, height), (0, 0, 0))
        self._draw = ImageDraw.Draw(self._canvas)

        # Create framebuffer - must be contiguous numpy array
        self._framebuffer = np.zeros((height, width, 3), dtype=np.uint8)

        # Initialize PioMatter (chain/parallel handled by geometry)
        
        # Determine pinout based on --led-gpio-mapping option
        # Default to Active3BGR for Seekgreat boards (colors are BGR order)
        pinout_map = {
            'adafruit-hat': piomatter.Pinout.AdafruitMatrixHat,
            'adafruit-hat-pwm': piomatter.Pinout.AdafruitMatrixHat,
            'adafruit-hat-bgr': piomatter.Pinout.AdafruitMatrixHatBGR,
            'adafruit-bonnet': piomatter.Pinout.AdafruitMatrixBonnet,
            'adafruit-bonnet-bgr': piomatter.Pinout.AdafruitMatrixBonnetBGR,
            'regular': piomatter.Pinout.Active3BGR,
            'classic': piomatter.Pinout.Active3BGR,
            'active3': piomatter.Pinout.Active3,
            'active3-bgr': piomatter.Pinout.Active3BGR,
        }
        
        # Get the mapping from options if available, default to Active3BGR
        hardware_mapping = getattr(options, 'hardware_mapping', 'active3-bgr').lower()
        pinout = pinout_map.get(hardware_mapping, piomatter.Pinout.Active3BGR)
        
        self._matrix = piomatter.PioMatter(
            colorspace=piomatter.Colorspace.RGB888Packed,
            pinout=pinout,
            framebuffer=self._framebuffer,
            geometry=self._geometry
        )
        
        # Do an initial clear to activate the display
        self._framebuffer[:] = 0
        self._matrix.show()

        self._width = width
        self._height = height
        self._double_buffer = None

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def CreateFrameCanvas(self):
        """Create a double-buffer canvas."""
        if self._double_buffer is None:
            self._double_buffer = PioMatterCanvas(self._width, self._height)
        return self._double_buffer

    def SwapOnVSync(self, canvas):
        """Swap buffers and update the display."""
        if isinstance(canvas, PioMatterCanvas):
            try:
                # Copy canvas content to framebuffer
                self._framebuffer[:] = np.asarray(canvas._image)
                # Update the display
                self._matrix.show()
            except Exception as e:
                print(f"ERROR in SwapOnVSync: {e}")
                import traceback
                traceback.print_exc()
        return canvas

    def SetImage(self, image, offset_x=0, offset_y=0):
        """Display an image on the matrix."""
        # Paste image onto canvas
        self._canvas.paste(image, (offset_x, offset_y))
        # Update framebuffer
        self._framebuffer[:] = np.asarray(self._canvas)
        # Show on display
        self._matrix.show()

    def Clear(self):
        """Clear the display."""
        self._canvas.paste(Image.new('RGB', (self._width, self._height), (0, 0, 0)))
        self._framebuffer[:] = np.asarray(self._canvas)
        self._matrix.show()


class PioMatterCanvas:
    """
    Canvas object that mimics the hzeller canvas interface but uses PIL.
    """

    def __init__(self, width, height):
        self._image = Image.new('RGB', (width, height), (0, 0, 0))
        self._draw = ImageDraw.Draw(self._image)
        self.width = width
        self.height = height

    def Clear(self):
        """Clear the canvas."""
        self._image.paste(Image.new('RGB', (self.width, self.height), (0, 0, 0)))

    def Fill(self, r, g, b):
        """Fill the entire canvas with a color."""
        self._image.paste(Image.new('RGB', (self.width, self.height), (r, g, b)))

    def SetPixel(self, x, y, r, g, b):
        """Set a single pixel."""
        self._draw.point((x, y), fill=(r, g, b))


class PioMatterColor:
    """Color object for PioMatter that mimics hzeller Color."""

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        # Aliases for compatibility
        self.red = r
        self.green = g
        self.blue = b

    def to_tuple(self):
        return (self.r, self.g, self.b)


class PioMatterFont:
    """Font object for PioMatter that mimics hzeller Font."""

    def __init__(self):
        self._font = None
        self._font_path = None

    def LoadFont(self, path):
        """Load a BDF font."""
        import os
        
        # Store the path for reference
        self._font_path = path
        self._font = None
        
        # Try to load BDF font using bdfparser library
        try:
            import bdfparser
            font = bdfparser.Font(path)
            self._font = font
            self._is_bdf = True
            print(f"Successfully loaded BDF font with bdfparser: {path}")
            return True
        except Exception as e:
            print(f"Failed to load BDF font {path} with bdfparser: {e}")
        
        # Fallback to 4x6.bdf
        try:
            import bdfparser
            fallback_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                         'assets', 'fonts', 'patched', '4x6.bdf')
            font = bdfparser.Font(fallback_path)
            self._font = font
            self._is_bdf = True
            print(f"Successfully loaded fallback BDF with bdfparser: {fallback_path}")
            return True
        except Exception as e:
            print(f"Failed to load 4x6.bdf with bdfparser: {e}")
        
        # Try loading a very small TrueType font as last resort
        try:
            from PIL import ImageFont
            for ttf_path in [
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            ]:
                if os.path.exists(ttf_path):
                    self._font = ImageFont.truetype(ttf_path, size=4)  # 4pt for smallest size
                    self._is_bdf = False
                    print(f"Using TrueType fallback at 4pt: {ttf_path}")
                    return True
        except Exception as e:
            print(f"Failed to load TrueType font: {e}")
        
        # Ultimate fallback - PIL default
        try:
            from PIL import ImageFont
            self._font = ImageFont.load_default()
            self._is_bdf = False
            print("Using PIL default font")
        except Exception:
            self._font = None
            self._is_bdf = False
        
        return True

    def CharacterWidth(self, char):
        """Get character width."""
        if self._font:
            # BDF font using bdfparser
            if hasattr(self, '_is_bdf') and self._is_bdf:
                try:
                    glyph = self._font.glyph(char)
                    return glyph.meta.get('dwx0', 4)
                except Exception:
                    return 4  # Default for missing chars
            # PIL font
            else:
                try:
                    bbox = self._font.getbbox(char)
                    return bbox[2] - bbox[0]
                except Exception:
                    return 6
        return 6  # Default fallback


class PioMatterGraphicsAdapter(GraphicsBase):
    """Graphics adapter for PioMatter using PIL drawing."""

    def __init__(self):
        pass

    def DrawText(self, canvas, font, x, y, color, text):
        """Draw text using PIL or BDF font."""
        if isinstance(canvas, PioMatterCanvas):
            try:
                pil_color = color.to_tuple() if isinstance(color, PioMatterColor) else color
                
                # Check if this is a BDF font (using bdfparser) or PIL font
                if hasattr(font, '_is_bdf') and font._is_bdf and font._font:
                    # Render BDF font pixel by pixel
                    current_x = x
                    for char in text:
                        try:
                            glyph = font._font.glyph(char)
                            bitmap = glyph.draw()
                            
                            # Get glyph properties from metadata
                            bbxoff = glyph.meta.get('bbxoff', 0)
                            bbyoff = glyph.meta.get('bbyoff', 0)
                            dwx0 = glyph.meta.get('dwx0', bitmap.width())
                            
                            # Get bitmap as list of strings ('0' and '1' chars)
                            pixels = bitmap.todata(1)
                            
                            # Draw glyph bitmap
                            for row_idx, row in enumerate(pixels):
                                for col_idx, pixel_char in enumerate(row):
                                    if pixel_char == '1':  # Check if character is '1'
                                        px = current_x + bbxoff + col_idx
                                        py = y - bbyoff - (len(pixels) - row_idx - 1)
                                        canvas._draw.point((px, py), fill=pil_color)
                            current_x += dwx0
                        except Exception as e:
                            # Character not found, skip with default spacing
                            current_x += 4
                    return current_x - x  # Return width
                else:
                    # Use PIL font rendering
                    canvas._draw.text((x, y - 10), text, fill=pil_color, font=font._font if hasattr(font, '_font') else None)
                    return len(text) * 6  # Approximate width
            except Exception as e:
                print(f"ERROR in DrawText: {e}")
                import traceback
                traceback.print_exc()
                return 0

    def DrawLine(self, canvas, x1, y1, x2, y2, color):
        """Draw a line using PIL."""
        if isinstance(canvas, PioMatterCanvas):
            pil_color = color.to_tuple() if isinstance(color, PioMatterColor) else color
            canvas._draw.line([(x1, y1), (x2, y2)], fill=pil_color, width=1)

    def Color(self, r, g, b):
        """Create a color object."""
        return PioMatterColor(r, g, b)

    def Font(self):
        """Create a font object."""
        return PioMatterFont()
