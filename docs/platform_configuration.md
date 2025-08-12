# Platform-Specific Configuration for Qtile

This document explains how to use the platform-specific configuration system in this qtile setup. The system automatically detects your operating system and applies appropriate application defaults and command overrides.

## Overview

The platform configuration system provides:
- Automatic platform detection (Linux, OpenBSD, FreeBSD, NetBSD)
- Platform-specific application preferences
- Command overrides for different operating systems
- Fallback mechanisms when preferred applications aren't available

## How It Works

### Platform Detection

The system uses Python's `platform.system()` to detect your operating system:

```python
from modules.platform_utils import get_platform_info

platform = get_platform_info()
print(f"Running on: {platform.system}")
print(f"Is BSD: {platform.is_bsd}")
print(f"Is Linux: {platform.is_linux}")
```

### Application Selection

Applications are automatically selected based on availability and platform preferences:

#### Terminal Emulators
- **Linux**: `st` → `alacritty` → `kitty` → `gnome-terminal` → `xterm`
- **OpenBSD**: `xterm` → `st` → `urxvt` → `gnome-terminal`
- **FreeBSD**: `st` → `alacritty` → `xterm` → `gnome-terminal`
- **NetBSD**: `xterm` → `st` → `urxvt`

#### Web Browsers
- **Linux**: `brave` → `firefox` → `chromium` → `google-chrome`
- **OpenBSD**: `firefox` → `chromium` → `iridium`
- **FreeBSD**: `firefox` → `chromium` → `brave`
- **NetBSD**: `firefox` → `seamonkey`

#### Application Launchers
- **Linux**: `rofi` → `dmenu` → `albert` → `ulauncher`
- **OpenBSD**: `dmenu` → `rofi`
- **FreeBSD**: `rofi` → `dmenu`
- **NetBSD**: `dmenu`

## Configuration Examples

### Accessing Platform-Specific Settings

```python
from qtile_config import get_config

config = get_config()

# Get platform-aware terminal
terminal = config.terminal  # Returns best available terminal for your OS

# Get platform-aware browser
browser = config.browser    # Returns best available browser for your OS

# Get all applications
apps = config.applications
print(f"Launcher: {apps['launcher']}")
print(f"Lock command: {apps['lock_session']}")
```

### Platform-Specific Commands

Different platforms use different commands for system operations:

#### Session Locking
- **Linux**: `loginctl lock-session`
- **BSD systems**: `xlock`

#### Audio Mixing
- **Linux**: `pavucontrol`
- **OpenBSD/NetBSD**: `mixerctl`
- **FreeBSD**: `mixer`

#### Screenshots
- **Linux**: `flameshot gui`
- **OpenBSD**: `xwd | xwdtopnm | pnmtopng`
- **FreeBSD**: `scrot`
- **NetBSD**: `xwd`

#### Network Management
- **Linux**: `nm-connection-editor`
- **OpenBSD**: `wiconfig`
- **FreeBSD**: `bsdconfig networking`
- **NetBSD**: `ifconfig`

## Key Bindings

The platform-specific applications are automatically used in key bindings:

- `Super + Return`: Launch terminal (platform-specific)
- `Super + w`: Launch browser (platform-specific)
- `Super + p`: Launch application launcher (platform-specific)
- `Alt + Ctrl + l`: Lock session (platform-specific command)

## Adding Custom Overrides

### Method 1: Modify platform_utils.py

Edit `modules/platform_utils.py` to add new applications or commands:

```python
# In _load_platform_configs method
terminal_preferences = {
    "linux": ["st", "alacritty", "kitty", "gnome-terminal", "xterm"],
    "openbsd": ["xterm", "st", "urxvt", "gnome-terminal"],
    # Add your custom preferences here
    "youros": ["your-terminal", "fallback-terminal"],
}
```

### Method 2: Runtime Overrides

Add overrides at runtime:

```python
from qtile_config import get_config

config = get_config()

# Add a custom command override
config.platform_config.add_override("custom_command", "my-custom-app")

# Access it later
custom_app = config.platform_config.get_command("custom_command", "fallback")
```

### Method 3: Environment-Based Overrides

You can create environment-specific configurations:

```python
import os
from qtile_config import get_config

config = get_config()

# Override based on hostname or environment variables
if os.uname().nodename == "workstation":
    config.platform_config.add_override("terminal", "alacritty")
elif os.environ.get("DISPLAY_SERVER") == "wayland":
    config.platform_config.add_override("terminal", "foot")
```

## Debugging Platform Configuration

### Check Platform Detection

```python
from modules.platform_utils import get_platform_info

platform = get_platform_info()
info = platform.get_system_info()

print("System Information:")
for key, value in info.items():
    print(f"  {key}: {value}")
```

### Check Available Applications

```python
from modules.platform_utils import get_platform_config

platform_config = get_platform_config()

# Check if specific commands are available
print(f"Has rofi: {platform_config.platform.has_command('rofi')}")
print(f"Has dmenu: {platform_config.platform.has_command('dmenu')}")

# Get the best launcher for this platform
launcher = platform_config.get_application("launcher")
print(f"Selected launcher: {launcher}")
```

### Check All Overrides

```python
from qtile_config import get_platform_overrides

overrides = get_platform_overrides()
print("Platform-specific overrides:")
for key, value in overrides.items():
    print(f"  {key}: {value}")
```

## Common Issues and Solutions

### Application Not Found

If your preferred application isn't being selected:

1. Check if it's installed: `which your-app`
2. Add it to the preferences list in `platform_utils.py`
3. Verify the application name matches the executable name

### Command Override Not Working

If a command override isn't being applied:

1. Check the command exists: `which base-command`
2. Verify the override is defined for your platform
3. Check for typos in the command name

### Platform Not Detected Correctly

If your platform isn't being detected:

1. Check `platform.system()` output: `python3 -c "import platform; print(platform.system())"`
2. Add support for your platform in `platform_utils.py`
3. Use runtime overrides as a workaround

## Integration with Existing Code

The platform system is designed to be backwards compatible. Your existing configuration will continue to work, but you can gradually adopt platform-specific features:

```python
# Old way (still works)
terminal = "st"

# New way (platform-aware)
from qtile_config import get_config
config = get_config()
terminal = config.terminal  # Automatically selects best terminal for your OS
```

## Best Practices

1. **Test on Multiple Platforms**: If you have access to different operating systems, test your configuration on each
2. **Provide Fallbacks**: Always specify fallback applications/commands
3. **Use Portable Paths**: Use `pathlib` instead of hardcoded paths
4. **Check Command Availability**: The system automatically checks if commands exist before using them
5. **Document Custom Overrides**: If you add custom overrides, document them for future reference

## Future Enhancements

Planned improvements include:
- Desktop environment detection and specific overrides
- Distribution-specific overrides (e.g., different commands for Arch vs Ubuntu)
- User preference files for easier customization
- GUI configuration tools