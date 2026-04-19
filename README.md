# BrightSign LED Control

A MicroPython application for controlling NeoPixel LED panels on BrightSign hardware. This system processes JSON commands via stdin to create dynamic color effects, gradients, and animations asynchronously.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for commands, colors, gradients, panels, and more.
- **Asynchronous Processing**: Uses asyncio for non-blocking command processing and animations.
- **Rich Color Support**: Supports RGB, HSL, hex colors, and named colors with automatic gamma correction.
- **Gradient Effects**: Linear and radial gradients with CSS-compatible size modes.
- **Panel Management**: Flexible panel configuration with aspect ratios and row definitions.
- **Command-Based Interface**: JSON commands sent via stdin for easy integration and scripting.

## Project Structure

- `main.py`: Main entry point; initializes hardware and starts the async command loop.
- `Commands.py`: Command registry and handler functions (e.g., `processColourCmd`, `processGradCmd`).
- `Colours.py`: Color classes (`RgbColour`, `HslColour`) and parsing (`parseColour`).
- `Gradient.py`: Gradient implementations (`LinearGrad`, `RadialGrad`).
- `ColourStop.py`: Color stop parsing and interpolation.
- `GetFadeFunc.py`: Fade interpolation modes with HSL/RGB options.
- `NeoPanel.py`: Panel abstraction with rows and slices.
- `Panel.py`: Panel registry and rendering utilities.
- `lib/colorsys.py`: Color space conversion functions.

## Hardware Requirements

- ESP32 microcontroller (e.g., ESP32-S2)
- NeoPixel LED strips/panels
- MicroPython firmware installed on the device

## Installation

1. Flash MicroPython firmware to your ESP32 device.
2. Upload the project files to the device.
3. Connect NeoPixel LEDs to GPIO pin 16 (configurable in `main.py`).

## Usage

Run `main.py` on the MicroPython device:

```bash
# On the device
import main
```

Send JSON commands via stdin to control the LEDs. Commands are processed asynchronously.

### Basic Commands

#### Set Solid Color
```json
{"cmd": "colour", "colour": "red", "panel": "main"}
```

#### Linear Gradient
```json
{"cmd": "grad", "type": "linear", "angle": 45, "stops": [{"colour": "red"}, {"colour": "blue"}]}
```

#### Radial Gradient
```json
{"cmd": "grad", "type": "radial", "center": [0.5, 0.5], "size": "farthest-corner", "stops": [{"colour": "red"}, {"colour": "blue"}]}
```

#### Animated Fade
```json
{"cmd": "fade", "time": 2, "inter": "hsl", "via": "longer", "stops": [{"colour": "green"}, {"colour": "purple"}]}
```

### Color Formats

- Named colors: `"red"`, `"blue"`, etc.
- Hex: `"#ff0000"`, `"#00ff00"`
- RGB: `"rgb(255 0 0)"`
- HSL: `"hsl(120 100 50)"`

## Configuration

Panel configurations are defined in `leds.json`, a JSON file that specifies LED strips, pins, and panel layouts. `main.py` loads this file on startup.

### leds.json Structure

```json
{
  "leds": [
    {
      "pin": 16,
      "count": 256,
      "panels": {
        "main": {
          "slice": [0, 128],
          "aspect": 1.0,
          "spans": [[0, 7], [8, 15], [16, 23]]
        },
        "secondary": {
          "slice": [128, 128],
          "aspect": 0.5,
          "spans": [[0, 16], [16, 16]]
        }
      }
    }
  ]
}
```

- `pin`: GPIO pin number for the NeoPixel strip
- `count`: Total number of LEDs on the strip
- `panels`: Object mapping panel names to configurations
  - `slice`: [start_index, length] of the LED range for this panel
  - `aspect`: Aspect ratio (width/height) for gradient calculations
  - `spans`: Array of [start, end] indices for each row in the panel (end can be less than start for reversed rows)

### Panel Configuration

Panels are automatically registered from `leds.json` using `AddPanel`. Commands can target specific panels with the `"panel"` field.

Example panel definition:
```python
nps = NeoPanel(np, 1, [(0,2), (5,3), (6,8)])  # 3 rows with different LED counts
AddPanel("main", nps)
```

Commands can target specific panels: `{"cmd": "colour", "colour": "red", "panel": "main"}`

### Development and Testing

- Use `demo_desktop.py` for desktop simulation with a GUI window.
- Send commands via stdin or pipe from files/scripts.
- Debug with `print()` statements; no logging framework.

## API Reference

### Commands

- `colour` / `color`: Set solid color
- `grad`: Apply gradient (linear or radial)
- `fade`: Animate color fade
- `size`: Placeholder for size commands

### Gradient Types

- **Linear**: `{"type": "linear", "angle": degrees}`
- **Radial**: `{"type": "radial", "center": [x, y], "size": "mode"}`

Size modes: `"closest-side"`, `"farthest-side"`, `"closest-corner"`, `"farthest-corner"`

### Color Interpolation

- `inter`: `"rgb"` or `"hsl"`
- `via`: `"shorter"`, `"longer"`, `"increasing"`, `"decreasing"` (for HSL fades)

## Contributing

- Follow the modular structure; add new commands in `Commands.py`.
- Update `.github/copilot-instructions.md` for AI coding guidelines.
- Test on actual hardware and with `demo_desktop.py`.

## License

[Add license information here]