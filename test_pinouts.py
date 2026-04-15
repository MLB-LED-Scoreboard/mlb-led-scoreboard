#!/usr/bin/env python3
"""Test different pinouts to find the right one for your board."""

import adafruit_blinka_raspberry_pi5_piomatter as piomatter
import numpy as np
import time

# Test parameters
width = 64
height = 32
n_addr_lines = 4

# Available pinouts to test
pinouts_to_test = [
    ('AdafruitMatrixHat', piomatter.Pinout.AdafruitMatrixHat),
    ('AdafruitMatrixBonnet', piomatter.Pinout.AdafruitMatrixBonnet),
    ('Active3', piomatter.Pinout.Active3),
    ('AdafruitMatrixHatBGR', piomatter.Pinout.AdafruitMatrixHatBGR),
    ('AdafruitMatrixBonnetBGR', piomatter.Pinout.AdafruitMatrixBonnetBGR),
    ('Active3BGR', piomatter.Pinout.Active3BGR),
]

print(f"Testing {len(pinouts_to_test)} pinouts on {width}x{height} display...")
print("Watch your display - it should flash RED for each pinout that works.\n")

for name, pinout in pinouts_to_test:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    try:
        # Create geometry
        geometry = piomatter.Geometry(
            width=width,
            height=height,
            n_addr_lines=n_addr_lines,
            rotation=piomatter.Orientation.Normal
        )
        
        # Create framebuffer
        framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Initialize display
        matrix = piomatter.PioMatter(
            colorspace=piomatter.Colorspace.RGB888Packed,
            pinout=pinout,
            framebuffer=framebuffer,
            geometry=geometry
        )
        
        print(f"✓ {name} initialized successfully")
        
        # Test 1: Fill RED
        print("  Testing RED...")
        framebuffer[:, :] = [255, 0, 0]  # RGB Red
        matrix.show()
        time.sleep(2)
        
        # Test 2: Fill GREEN
        print("  Testing GREEN...")
        framebuffer[:, :] = [0, 255, 0]  # RGB Green
        matrix.show()
        time.sleep(2)
        
        # Test 3: Fill BLUE
        print("  Testing BLUE...")
        framebuffer[:, :] = [0, 0, 255]  # RGB Blue
        matrix.show()
        time.sleep(2)
        
        # Clear
        framebuffer[:, :] = 0
        matrix.show()
        
        print(f"✓ {name} completed - did you see RED/GREEN/BLUE flashes?")
        
        # Cleanup
        del matrix
        
    except Exception as e:
        print(f"✗ {name} failed: {e}")
    
    time.sleep(1)

print("\n" + "="*60)
print("Test complete!")
print("Which pinout showed colors correctly on your display?")
print("="*60)
