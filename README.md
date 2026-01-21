# LG TV CLI

Control your LG WebOS TV from the command line. A comprehensive CLI tool for managing LG Smart TVs with WebOS, built with Python and PyWebOSTV.

## Features

- **TV Discovery**: Automatically find LG TVs on your network
- **Power Control**: Turn TV on/off, screen on/off
- **Volume & Audio**: Control volume, mute, and audio output sources
- **App Management**: Launch apps, list installed applications
- **Input Switching**: Switch between HDMI inputs and TV channels
- **Media Playback**: Control play, pause, stop, rewind, fast forward
- **Remote Control**: Send button presses (navigation, numbers, colors)
- **Keyboard Input**: Type text into TV input fields
- **Mouse/Pointer**: Control TV cursor with mouse commands
- **System Info**: Get detailed TV information and current state
- **Multi-TV Support**: Save and manage multiple TVs

## Installation

### Option 1: Install from Source (Recommended)

```bash
git clone https://github.com/yourusername/lgtvcli.git
cd lgtvcli
pip install .
```

For development:
```bash
pip install -e .
```

### Option 2: Direct Installation

```bash
pip install git+https://github.com/yourusername/lgtvcli.git
```

### Option 3: Using pipx (Isolated Installation)

```bash
pipx install git+https://github.com/yourusername/lgtvcli.git
```

### Requirements

- Python 3.8 or higher
- LG TV with webOS 2.0 or higher
- TV and computer on the same network
- "LG Connect Apps" enabled in TV Network settings

## Quick Start

### 1. Discover TVs on Your Network

```bash
lgtv discover
```

### 2. Pair with Your TV

```bash
lgtv pair 192.168.1.100
```

Accept the pairing request on your TV when prompted.

### 3. Control Your TV

```bash
# Power control
lgtv power off
lgtv power on

# Volume
lgtv volume up
lgtv volume set 50
lgtv volume mute

# Launch apps
lgtv app launch Netflix

# Switch inputs
lgtv input set HDMI_1
```

## Command Reference

### Discovery & Configuration

#### Discover TVs
```bash
lgtv discover [--timeout SECONDS]
```
Find LG TVs on your local network.

#### Pair with TV
```bash
lgtv pair IP [--name NAME]
```
Pair with a TV and save configuration. You'll need to accept the pairing request on your TV.

#### List Configured TVs
```bash
lgtv config list
```

#### Set Default TV
```bash
lgtv config set-default NAME
```

#### Remove TV
```bash
lgtv config remove NAME
```

### Power Management

```bash
lgtv power on           # Turn TV on (requires MAC address)
lgtv power off          # Turn TV off
lgtv power screen-off   # Turn screen off (energy saving)
lgtv power screen-on    # Turn screen on
lgtv power status       # Check if TV is on
```

**Note**: `power on` uses Wake-on-LAN and requires the TV's MAC address. If not auto-detected during pairing, add it manually to `~/.config/lgtv/config.json`.

### Volume & Audio

```bash
# Volume control
lgtv volume up          # Increase volume by 1
lgtv volume down        # Decrease volume by 1
lgtv volume set 50      # Set volume to 50 (0-100)
lgtv volume mute        # Toggle mute
lgtv volume status      # Show current volume

# Audio output
lgtv audio list         # List available audio outputs
lgtv audio set OUTPUT   # Set audio output (tv_speaker, external_optical, etc.)
lgtv audio status       # Show current audio output
```

### Application Management

```bash
lgtv app list           # List installed apps
lgtv app launch NAME    # Launch app by name (e.g., "Netflix")
lgtv app current        # Show currently running app
lgtv app close APP_ID   # Close app by ID
```

### Input & Channel Control

```bash
# Input sources
lgtv input list         # List available inputs
lgtv input set SOURCE   # Switch input (e.g., HDMI_1, HDMI_2)

# TV channels
lgtv channel up         # Next channel
lgtv channel down       # Previous channel
lgtv channel set NUM    # Set specific channel
lgtv channel list       # List all channels
lgtv channel info       # Show current channel and program info
```

### Media Playback

```bash
lgtv media play         # Play
lgtv media pause        # Pause
lgtv media stop         # Stop
lgtv media rewind       # Rewind
lgtv media forward      # Fast forward
```

### Remote Control

```bash
lgtv button BUTTON      # Send button press
```

Available buttons:
- Navigation: `home`, `back`, `up`, `down`, `left`, `right`, `ok`, `enter`
- Menu: `menu`, `info`, `exit`, `dash`
- Colors: `red`, `green`, `yellow`, `blue`
- Numbers: `0` through `9`, `asterisk`

```bash
lgtv notify "MESSAGE"   # Show notification on TV
```

### Keyboard Input

```bash
lgtv keyboard "text"    # Type text into TV input field
```

**Note**: The on-screen keyboard must be visible for this to work. Use this to type into search fields, login forms, etc.

### Mouse/Pointer Control

```bash
lgtv mouse move DX DY   # Move cursor by relative offset
lgtv mouse click        # Send mouse click
```

Example:
```bash
lgtv mouse move 100 50  # Move cursor right 100px, down 50px
lgtv mouse click        # Click at current position
```

### System Information

```bash
lgtv info system        # Get TV model, firmware, webOS version
lgtv info current       # Get current state (app, channel, volume)
lgtv inspect            # Detailed TV state inspection
```

### Global Options

All commands support these options:

```bash
--tv NAME               # Use specific configured TV
--ip ADDRESS            # Use IP directly (bypass configuration)
--timeout SECONDS       # Connection timeout (default: 10)
```

Example:
```bash
lgtv --tv bedroom power off
lgtv --ip 192.168.1.100 volume set 30
```

## Configuration

Configuration is stored at `~/.config/lgtv/config.json`:

```json
{
  "default_tv": "living-room",
  "tvs": {
    "living-room": {
      "name": "Living Room TV",
      "ip": "192.168.1.100",
      "mac": "AA:BB:CC:DD:EE:FF",
      "key": "stored-pairing-key",
      "model": "OLED55C9PUA"
    }
  }
}
```

You can manually edit this file to add MAC addresses or manage multiple TVs.

## Troubleshooting

### TV Not Discovered

1. Ensure your TV is turned on
2. Enable "LG Connect Apps" in TV Settings → Network → LG Connect Apps
3. Verify your computer and TV are on the same network
4. Try manual pairing with IP: `lgtv pair <ip-address>`

### Connection Refused

- Make sure "LG Connect Apps" is enabled in TV Network settings
- Check that the TV is on and connected to network
- Verify the IP address is correct

### Authentication Failed

- Re-pair with the TV: `lgtv pair <ip-address>`
- Delete the stored configuration and pair again

### Wake-on-LAN Not Working

- Ensure you have the TV's MAC address configured
- TV must be connected via Ethernet (Wi-Fi may not support WoL)
- Enable Wake-on-LAN in TV network settings

### Screenshot/HTML Capture

Unfortunately, screenshot capture and HTML/DOM access are **not available** through the LG WebOS external API. These features require:
- Developer mode on the TV
- LG Developer tools (ares-inspect)
- Only work for apps you've deployed, not general TV content

The `lgtv inspect` command shows all available state information instead.

## Supported TV Models

Any LG Smart TV with webOS 2.0 or higher, including:

- webOS 2.0 (2015 models)
- webOS 3.0 (2016 models)
- webOS 3.5 (2017 models)
- webOS 4.0 (2018 models)
- webOS 4.5 (2019 models)
- webOS 5.0 (2020 models)
- webOS 6.0 (2021 models)
- webOS 22 (2022 models)
- webOS 23 (2023 models and later)

## Development

### Setup Development Environment

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black lgtv/
```

## Resources

Research and documentation sources:

- [LG webOS TV Developer](https://webostv.developer.lge.com/)
- [PyWebOSTV GitHub](https://github.com/supersaiyanmode/PyWebOSTV)
- [LGWebOSRemote](https://github.com/klattimer/LGWebOSRemote)
- [lgtv2 Node.js library](https://github.com/hobbyquaker/lgtv2)
- [webostv Go CLI](https://github.com/snabb/webostv)
- [Home Assistant LG webOS Integration](https://www.home-assistant.io/integrations/webostv/)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
