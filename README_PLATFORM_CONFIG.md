# Platform-Specific Configuration System

This qtile configuration includes an automatic platform detection and configuration system that adapts your desktop environment based on your operating system.

## What It Does

The system automatically:
- Detects your OS (Linux, OpenBSD, FreeBSD, NetBSD)
- Selects the best available applications for your platform
- Applies platform-specific command overrides
- Provides fallbacks when preferred applications aren't available

## Key Benefits

✅ **Cross-Platform Compatibility**: Same config works on Linux and BSD  
✅ **Smart Application Selection**: Automatically picks the best available terminal, browser, etc.  
✅ **Zero Configuration**: Works out of the box with sensible defaults  
✅ **Easy Customization**: Simple override system for custom preferences  

## Quick Example

### Before (Manual Configuration)
```python
# Had to manually change for each system
terminal = "st"           # Works on Linux, might not be on OpenBSD
browser = "brave"         # Available on Linux, not on OpenBSD
lock_cmd = "loginctl lock-session"  # Linux-specific
```

### After (Platform-Aware)
```python
from qtile_config import get_config
config = get_config()

# Automatically selects best available for your OS
terminal = config.terminal    # "st" on Linux, "xterm" on OpenBSD
browser = config.browser      # "brave" on Linux, "firefox" on OpenBSD  
lock_cmd = config.applications["lock_session"]  # "loginctl" on Linux, "xlock" on BSD
```

## Platform Defaults

| Application | Linux | OpenBSD | FreeBSD | NetBSD |
|-------------|-------|---------|---------|--------|
| **Terminal** | st → alacritty → kitty | xterm → st → urxvt | st → alacritty → xterm | xterm → st → urxvt |
| **Browser** | brave → firefox → chromium | firefox → chromium → iridium | firefox → chromium → brave | firefox → seamonkey |
| **Launcher** | rofi → dmenu → albert | dmenu → rofi | rofi → dmenu | dmenu |
| **Lock Screen** | loginctl lock-session | xlock | xlock | xlock |

## Testing Your Configuration

Run the included test script to see what's detected on your system:

```bash
cd ~/.config/qtile
python3 scripts/test_platform_config.py
```

This shows:
- Your detected platform
- Which applications are available
- What gets selected automatically
- Cross-platform comparison

## Key Files

- `modules/platform_utils.py` - Core platform detection and configuration
- `qtile_config.py` - Main config with platform integration
- `docs/platform_configuration.md` - Detailed documentation
- `scripts/test_platform_config.py` - Test and validation script

## Usage in Key Bindings

Your existing key bindings automatically use platform-specific applications:

- `Super + Return` - Launch terminal (platform-specific)
- `Super + w` - Launch browser (platform-specific)  
- `Super + p` - Launch launcher (rofi on Linux, dmenu on most BSD)
- `Alt + Ctrl + l` - Lock session (loginctl on Linux, xlock on BSD)

## Custom Overrides

### Runtime Override
```python
from qtile_config import get_config
config = get_config()
config.platform_config.add_override("terminal", "my-preferred-terminal")
```

### Add New Application Type
Edit `modules/platform_utils.py` to add preferences for new application types.

## Backwards Compatibility

This system is fully backwards compatible. Your existing configuration continues to work, but you can gradually adopt platform-specific features where beneficial.

## Getting Help

- **Detailed Guide**: See `docs/platform_configuration.md`
- **Test Script**: Run `python3 scripts/test_platform_config.py`
- **Debug**: Check what's available with the test script
- **Issues**: The system logs details about application selection and failures

## Example Output

```
Platform: linux
Terminal: st
Browser: brave
Launcher: rofi -show run
Lock command: loginctl lock-session
```

The same config on OpenBSD might show:
```
Platform: openbsd
Terminal: xterm
Browser: firefox
Launcher: dmenu
Lock command: xlock
```

---

This platform configuration system makes your qtile setup truly portable across Unix-like systems while maintaining optimal application choices for each platform.