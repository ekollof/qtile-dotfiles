# Monitor Detection and Hotplug Support

This document describes the monitor detection improvements and hotplug support in the Qtile configuration.

## Issues Fixed

### 1. Static Screen Detection
- **Problem**: Screen count was only detected at Qtile startup
- **Solution**: Added dynamic screen detection that can be triggered by monitor hotplug events

### 2. Autostart Loop
- **Problem**: The autostart script was running in an endless loop, preventing proper initialization
- **Solution**: Improved lockfile mechanism with PID validation

### 3. Screen Change Handling
- **Problem**: Screen changes only triggered a restart after 60 seconds
- **Solution**: Enhanced screen change hook with immediate detection and configuration update

## New Features

### Automatic Monitor Detection
- Detects both X11 and Wayland displays
- Robust fallback mechanisms for different display servers
- Improved timeout handling for better reliability

### Manual Screen Reconfiguration
- **Keyboard shortcut**: `Mod4 + Ctrl + S` to manually reconfigure screens
- **Script**: `/home/ekollof/.config/qtile/reconfigure_screens.py` for external triggering
- **Function**: `manually_reconfigure_screens()` in config.py

### Better Hotplug Support
- Monitors screen change events
- Automatically updates screen configuration when monitors are connected/disconnected
- Prevents restart loops with improved timing logic

## Usage

### When You Plug in a New Monitor
1. **Automatic**: The system should detect the change within 2-5 seconds and reconfigure automatically
2. **Manual**: If automatic detection doesn't work, press `Mod4 + Ctrl + S`
3. **Script**: Run `/home/ekollof/.config/qtile/reconfigure_screens.py` from terminal
4. **Fallback**: Press `Mod4 + Ctrl + R` to restart Qtile completely

### Troubleshooting

#### Monitor Not Detected
1. Check if the monitor is properly connected and powered on
2. Try: `xrandr --query` (X11) or `wlr-randr` (Wayland) to see if the system detects it
3. Use manual reconfiguration: `Mod4 + Ctrl + S`

#### Autostart Issues
1. Check `/home/ekollof/.config/qtile/autostart.log` for errors
2. Look for lock files in `/tmp/qtile_autostart.*` - remove if stale
3. Restart Qtile: `Mod4 + Ctrl + R`

#### Screen Layout Issues
1. Use `autorandr -c` to apply saved display configuration
2. Check available profiles: `autorandr --list`
3. Save current setup: `autorandr --save <profile_name>`

## Technical Details

### Screen Detection Order
1. **Wayland**: Uses `wlr-randr --json` to get display information
2. **X11**: Uses `xrandr --query` to detect active displays, falls back to `--listmonitors`
3. **Fallback**: Defaults to 1 screen if detection fails

### Timing and Safety
- Startup delay: 30 seconds before processing screen changes (prevents restart loops)
- Detection delay: 2 seconds after screen change event (allows system to settle)
- Lock timeout: Improved PID-based validation for autostart script

### Configuration Files Modified
- `modules/screens.py`: Enhanced screen detection and refresh capabilities
- `modules/hooks.py`: Improved screen change handling
- `modules/keys.py`: Added manual screen reconfiguration keybinding
- `autostart.sh`: Fixed lockfile mechanism
- `config.py`: Added manual reconfiguration function and logger import

## Future Improvements

- Monitor-specific configuration (different bars per monitor)
- Saved display profiles integration
- Better error reporting and user feedback
- Monitor position and orientation detection
