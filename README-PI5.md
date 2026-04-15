# Raspberry Pi 5 Support for MLB LED Scoreboard

This fork adds support for Raspberry Pi 5 using the Adafruit PioMatter library alongside the existing hzeller driver for Pi 4 and earlier.

## What's New

- **Dual Driver Support**: Works with both Raspberry Pi 4 (hzeller) and Pi 5 (PioMatter)
- **Automatic Detection**: Use `--pi5` flag to enable Pi 5 mode
- **Abstraction Layer**: Clean driver interface that can support future hardware

## Hardware Requirements

### For Raspberry Pi 5:
- Raspberry Pi 5 (4GB or 8GB recommended)
- RGB Matrix HAT/Adapter (Seekgreat Rev 3.8, Adafruit RGB Matrix Bonnet/HAT, or compatible)
- HUB75 RGB LED Matrix Panel (tested with 64x32)
- 5V Power Supply (4-5A per panel)
- MicroSD card (16GB+ recommended)

**Note:** This fork has been tested and confirmed working with the Seekgreat RGB Matrix Adapter Board Rev 3.8.

### For Raspberry Pi 4 and Earlier:
- Same as original project (see main README.md)

## Installation

### 1. Basic Setup (Same for all Pi versions)

```bash
# Clone this repository
git clone https://github.com/YOUR_USERNAME/mlb-led-scoreboard.git
cd mlb-led-scoreboard

# Run the base installation
sudo ./install.sh
```

### 2. Raspberry Pi 5 Specific Setup

If you're using a Raspberry Pi 5, install the additional dependencies:

```bash
# Install Pi 5 dependencies
pip3 install -r requirements-pi5.txt

# Verify PIO device access
ls -l /dev/pio0

# If pio0 doesn't exist, update your firmware
sudo apt update && sudo apt upgrade -y
sudo reboot

# If pio0 exists but has wrong permissions, add udev rule:
echo 'SUBSYSTEM=="*-pio", GROUP="gpio", MODE="0660"' | sudo tee /etc/udev/rules.d/99-pio.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Running the Scoreboard

### On Raspberry Pi 5:

```bash
# Default (uses Active3 pinout for Seekgreat and similar boards)
sudo python3 main.py --pi5 --led-rows=32 --led-cols=64

# For Adafruit HAT/Bonnet, specify the hardware mapping:
sudo python3 main.py --pi5 --led-rows=32 --led-cols=64 --led-gpio-mapping=adafruit-hat
```

### On Raspberry Pi 4 and Earlier:

```bash
sudo python3 main.py --led-rows=32 --led-cols=64 --led-gpio-mapping=adafruit-hat
```

## Configuration

The `--pi5` flag tells the software to use the PioMatter driver instead of the hzeller driver.

### Hardware Pinout Mapping:

The default pinout is `active3` which works with:
- Seekgreat RGB Matrix Adapter Board Rev 3.8
- Most generic RGB Matrix HATs

For Adafruit boards, use:
```bash
--led-gpio-mapping=adafruit-hat     # For Adafruit Matrix HAT
--led-gpio-mapping=adafruit-bonnet  # For Adafruit Matrix Bonnet
```

**Testing Your Board:** If you're unsure which pinout to use, run:
```bash
sudo python3 test_pinouts.py
```
This will cycle through all available pinouts and flash colors to help you identify the correct one.

### Common Options:

```bash
--led-rows=32          # Height of your panel (16 or 32)
--led-cols=64          # Width of your panel (32 or 64)
--led-chain=2          # Number of panels chained together
--led-brightness=75    # Brightness level (1-100)
--led-gpio-mapping=adafruit-hat  # Hardware mapping
```

## Differences Between Pi 4 and Pi 5 Drivers

| Feature | Pi 4 (hzeller) | Pi 5 (PioMatter) |
|---------|----------------|------------------|
| Library | rpi-rgb-led-matrix | Adafruit Blinka PioMatter |
| Performance | Excellent | Good (newer, still optimizing) |
| Text Rendering | BDF fonts | PIL/TrueType fonts |
| Hardware | Direct GPIO | RP1 PIO subsystem |

## Troubleshooting

### Pi 5 Issues:

**Matrix doesn't light up:**
- Check that `/dev/pio0` exists
- Verify power supply is adequate
- Check wiring matches Adafruit guide
- Try running with `sudo`

**Permission denied on /dev/pio0:**
```bash
sudo usermod -a -G gpio $USER
# Then log out and back in
```

**Import error for piomatter:**
```bash
pip3 install --upgrade Adafruit-Blinka-Raspberry-Pi5-Piomatter
```

**Text positioning looks wrong:**
- Pi 5 uses PIL for rendering which has different baseline behavior
- You may need to adjust y-coordinates in custom renderers

### Pi 4 Issues:

See the main README.md for Pi 4 troubleshooting.

## Development

### Architecture

The driver abstraction is in `driver/`:
- `base.py` - Abstract base classes for drivers
- `hzeller_adapter.py` - Wrapper for Pi 4 (rgbmatrix)
- `piomatter_adapter.py` - Wrapper for Pi 5 (PioMatter)
- `__init__.py` - Driver factory and mode selection

### Adding Support for New Hardware

1. Create a new adapter in `driver/your_adapter.py`
2. Implement `MatrixDriverBase` and `GraphicsBase`
3. Add a new `DriverMode` in `driver/mode.py`
4. Update `driver/__init__.py` to detect and load your driver

## Known Limitations

### Pi 5:
- BDF font support is limited (uses PIL fonts as fallback)
- Some hzeller-specific features may not be available
- Performance may be slightly lower than Pi 4

### Both:
- Both drivers cannot be used simultaneously (would require different hardware setups)

## Credits

- Original MLB LED Scoreboard: https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard
- hzeller rpi-rgb-led-matrix: https://github.com/hzeller/rpi-rgb-led-matrix
- Adafruit PioMatter: https://github.com/adafruit/Adafruit_Blinka_Raspberry_Pi5_Piomatter

## License

Same as original project - see LICENSE.md

## Contributing

Contributions welcome! Please test on both Pi 4 and Pi 5 if possible.

1. Fork the repo
2. Create a feature branch
3. Test your changes
4. Submit a pull request
