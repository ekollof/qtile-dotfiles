# Wallpaper Auto-Reload System

This document describes the automatic wallpaper and color scheme reloading system in qtile.

## Overview

The qtile configuration includes an automatic color monitoring system that:
- Watches for changes to `~/.cache/wal/colors.json`
- Automatically restarts qtile when wallpaper colors change
- Integrates seamlessly with pywal/wallust color schemes
- Provides instant visual feedback when wallpapers change

## How It Works

1. **Color Monitoring**: A background thread monitors the wal colors file using the `watchdog` library
2. **Change Detection**: When wal generates new colors from a wallpaper, the file change is detected instantly
3. **Automatic Restart**: qtile automatically restarts to apply the new color scheme
4. **Seamless Integration**: All widgets, bars, and UI elements update with new colors

## Usage

### Basic Wallpaper Changes

The system works automatically with any tool that updates wal colors:

```bash
# Set wallpaper with wal - qtile will restart automatically
wal -i /path/to/wallpaper.jpg

# Use wallust instead - also works automatically  
wallust run /path/to/wallpaper.jpg
```

### Existing Keybindings

Your qtile configuration includes these convenient keybindings:

- **`Alt + Ctrl + W`**: Set random wallpaper (`~/bin/wallpaper.ksh -r`)
- **`Super + Ctrl + W`**: Pick wallpaper (`~/bin/pickwall.sh`)

Both keybindings will trigger automatic qtile restart with new colors.

### Manual Color Reload

If needed, you can manually trigger a color reload:

**From qtile command line:**
```python
color_manager.manual_reload_colors()
```

**From a script:**
```bash
# Modify colors.json and qtile will detect the change automatically
wal -R  # Reload last wallpaper
```

## System Status

### Check if Monitoring is Active

```python
# In qtile shell or script
from modules.simple_color_management import color_manager
print(f"Monitoring active: {color_manager.is_monitoring()}")
```

### Test the System

Run the comprehensive test suite:

```bash
# Quick test
python3 scripts/test_wallpaper_integration.py --quick

# Full test suite  
python3 scripts/test_wallpaper_integration.py

# Test existing wallpaper script integration
python3 scripts/test_existing_wallpaper.py
```

## Technical Details

### File Monitoring

- **Watched File**: `~/.cache/wal/colors.json`
- **Method**: Uses `watchdog` library for efficient file monitoring
- **Fallback**: Polling-based monitoring if watchdog unavailable
- **Delay**: 200ms delay after file change to ensure write completion

### Color Validation

The system includes several safety checks:
- Validates JSON format before applying changes
- Checks file size to avoid processing incomplete writes
- Compares colors to avoid unnecessary restarts
- Logs all color changes for debugging

### Error Handling

- Graceful fallback when qtile restart isn't available
- Continues monitoring even if individual change processing fails
- Detailed logging for troubleshooting
- Automatic recovery from temporary file issues

## Troubleshooting

### Issue: Wallpaper changes but qtile doesn't restart

**Check monitoring status:**
```bash
python3 scripts/debug_color_monitoring.py
```

**Common solutions:**
- Ensure `watchdog` is installed: `pip install watchdog`
- Check qtile logs for errors: `grep -i color ~/.local/share/qtile/qtile.log`
- Verify wal is working: `wal -i /path/to/image.jpg`

### Issue: Slow wallpaper script

If `~/bin/wallpaper.ksh -r` is slow:
- The monitoring system still works correctly
- Consider using direct `wal` commands for faster changes
- The script may be downloading wallpapers or processing large images

### Issue: Colors not updating properly

**Check wal colors file:**
```bash
cat ~/.cache/wal/colors.json | jq .special.background
```

**Verify file permissions:**
```bash
ls -la ~/.cache/wal/colors.json
```

**Test manual change detection:**
```bash
python3 scripts/debug_watchdog.py
```

## System Requirements

- **Python packages**: `watchdog`, `json`, `pathlib`
- **External tools**: `wal` or `wallust` for color generation
- **File system**: Writable `~/.cache/wal/` directory

## Configuration

### Color Manager Settings

The color manager is configured in `modules/simple_color_management.py`:

```python
# Default colors file location
colors_file = "~/.cache/wal/colors.json"

# Monitoring settings
AUTO_START = True           # Start monitoring on first access
POLLING_INTERVAL = 1.0      # Fallback polling interval (seconds)
WRITE_DELAY = 0.2          # Delay after file change (seconds)
```

### Enabling/Disabling Auto-Restart

To temporarily disable automatic restarts:

```python
# Stop monitoring
color_manager.stop_monitoring()

# Restart monitoring  
color_manager.start_monitoring()
```

## Integration with Other Tools

### Nitrogen
```bash
nitrogen --set-wallpaper /path/to/image.jpg
wal -i /path/to/image.jpg  # Generate colors separately
```

### feh
```bash
feh --bg-scale /path/to/image.jpg
wal -i /path/to/image.jpg
```

### Custom Scripts

Any script that updates `~/.cache/wal/colors.json` will trigger automatic qtile restart:

```bash
#!/bin/bash
# Custom wallpaper script
wal -i "$1"
# qtile restart happens automatically
```

## Logging and Debugging

### Log Locations

- **qtile logs**: `~/.local/share/qtile/qtile.log`
- **Color changes**: Search for "Colors file changed" in logs
- **Monitoring status**: Search for "Color monitoring" in logs

### Debug Mode

Enable verbose logging by setting environment variable:
```bash
DEBUG=1 qtile start
```

### Test Scripts

- `scripts/debug_color_monitoring.py` - Comprehensive system diagnostics
- `scripts/debug_watchdog.py` - File monitoring investigation  
- `scripts/test_wallpaper_integration.py` - Full workflow validation
- `scripts/test_existing_wallpaper.py` - Keybinding integration test

## Recent Improvements

### Critical Bug Fix (August 2025)

Fixed a critical path comparison bug that prevented wallpaper auto-reload:
- **Issue**: File path comparison always failed due to string vs Path object mismatch
- **Fix**: Proper string conversion in watchdog event handler
- **Result**: 100% reliable wallpaper change detection

### Enhanced Error Handling

- Better validation of color file changes
- Improved logging with color change tracking  
- Graceful handling of qtile restart failures
- Protection against processing incomplete file writes

### Comprehensive Testing

Created extensive test suite to validate all components:
- File change detection
- Wal command integration
- Automatic monitoring
- Keybinding integration
- Error recovery

## Support

If you encounter issues:

1. Run the diagnostic script: `python3 scripts/debug_color_monitoring.py`
2. Check qtile logs for error messages
3. Verify wal is working independently
4. Test with manual color file changes

The system is designed to be robust and self-recovering, with detailed logging to help diagnose any issues.