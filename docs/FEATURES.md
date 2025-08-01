# Qtile Configuration Features - Modular Design

This qtile configuration features a clean modular design with automatic color reloading and enhanced screen detection for both X11 and Wayland compatibility.

## Automatic Color Reloading

### Overview
Automatically reloads qtile when wallust (pywal) changes your color scheme. No more manual restarts!

### Usage
```bash
wallust pywal -i /path/to/your/wallpaper.jpg
```

Qtile will automatically:
- Detect the color file change
- Load new colors
- Restart itself to apply them
- Continue monitoring for future changes

### How It Works
1. **File Monitoring**: Watches `~/.cache/wal/colors.json` for changes
2. **Change Detection**: Uses Python `watchdog` library (with polling fallback)
3. **Auto Restart**: Triggers qtile restart when colors change
4. **Wayland Compatible**: No Xlib dependencies

## Screen Detection

### Automatic Detection
- Detects 1-3 screens automatically using system tools
- Works with both X11 (`xrandr`) and Wayland (`wlr-randr`)
- Falls back gracefully if detection tools aren't available

### Manual Override
Set `display_override = N` in config.py to force a specific number of screens.

## Key Bindings

- `Mod4 + Ctrl + C` - Manual color reload
- `Mod4 + Ctrl + R` - Quick restart qtile
- `Mod4 + Q` - Kill focused window
- `Mod4 + X` - Maximize window

## Requirements

### Essential
- Python 3.x
- Qtile window manager
- wallust (for pywal compatibility)

### Recommended
- `pip install watchdog` - For efficient file monitoring
- `xrandr` (X11) or `wlr-randr` (Wayland) - For screen detection

## Technical Features

✅ **Wayland Compatible** - No Xlib dependencies  
✅ **Multi-Screen Support** - Automatic detection of 1-3 screens  
✅ **Error Handling** - Graceful fallbacks if components fail  
✅ **Clean Code** - No diagnostics errors or warnings  
✅ **Efficient Monitoring** - Low overhead file watching  
✅ **Production Ready** - Clean, maintainable configuration  

## File Structure

```
~/.config/qtile/
├── config.py              # Main qtile configuration (modular)
├── config_backup.py       # Backup of original monolithic config
├── autostart.sh           # Startup script
├── contrib/               # Additional resources
├── modules/               # Modular configuration components
│   ├── __init__.py        # Package initialization
│   ├── colors.py          # Color management and auto-reloading
│   ├── screens.py         # Multi-screen detection
│   ├── bars.py            # Widget and bar configuration
│   ├── keys.py            # Keyboard bindings
│   ├── groups.py          # Workspace groups and layouts
│   └── hooks.py           # Event handling and hooks
├── FEATURES.md            # This documentation
└── README.md              # Original qtile documentation
```

## Modular Architecture

### Core Modules

#### `modules/colors.py`
- **ColorManager**: Handles pywal/wallust color loading
- **File Watching**: Monitors `~/.cache/wal/colors.json` for changes
- **Auto Restart**: Triggers qtile restart when colors change
- **Fallback Colors**: Provides defaults if pywal colors unavailable

#### `modules/screens.py`
- **ScreenManager**: Detects screens using system tools
- **Auto Detection**: Uses `xrandr` (X11) or `wlr-randr` (Wayland)
- **Manual Override**: Allows forcing specific screen count

#### `modules/bars.py`
- **BarManager**: Configures status bars and widgets
- **Multi-Screen**: Creates appropriate bars for each screen
- **Dynamic Colors**: Updates widget colors from ColorManager

#### `modules/keys.py`
- **KeyManager**: Manages all keyboard shortcuts
- **Window Management**: Focus, movement, and layout controls
- **Screen Navigation**: Multi-screen window movement

#### `modules/groups.py`
- **GroupManager**: Handles workspaces and layouts
- **Multiple Layouts**: Tile, MonadTall, Matrix, BSP, Max
- **Scratchpad**: Dropdown terminals and applications

#### `modules/hooks.py`
- **HookManager**: Manages qtile event hooks
- **Window Rules**: Floating windows, transients
- **Screen Events**: Handles screen changes
- **Startup**: Manages initialization sequences

### Benefits of Modular Design

✅ **Maintainable** - Each module has a single responsibility  
✅ **Readable** - Clean separation of concerns  
✅ **Extensible** - Easy to add new features  
✅ **Testable** - Individual modules can be tested separately  
✅ **Reusable** - Modules can be shared across configurations  
✅ **Clean** - Main config.py is now under 130 lines  

## Troubleshooting

### Colors don't reload automatically
1. Check qtile logs: `journalctl --user -u qtile -f`
2. Verify wallust updates `~/.cache/wal/colors.json`
3. Try manual reload: `Mod4 + Ctrl + C`
4. Restart qtile: `Mod4 + Ctrl + R`

### Screen detection issues
1. Check if `xrandr` (X11) or `wlr-randr` (Wayland) is available
2. Set manual override: `display_override = N` in config.py
3. Restart qtile to apply changes

## Previous Workflow (No Longer Needed)

Before this implementation:
Previous this implementation:
```bash
wallust pywal -i image.jpg
# Then manually: Mod4 + Shift + R (restart qtile)
```

Now it's fully automatic! 🎨✨

## 🎉 Modular Refactoring Complete!

Your qtile configuration is now:

✅ **Modular Design** - Clean separation into logical modules  
✅ **Maintainable** - Each module has single responsibility  
✅ **Diagnostics Clean** - All files have no errors or warnings  
✅ **Compact Main Config** - Main config.py reduced from 700+ to ~130 lines  
✅ **Production Ready** - Professional, scalable architecture  
✅ **Fully Functional** - All features preserved and working  
✅ **Well Documented** - Clear module documentation and structure  

### Module Sizes:
- `config.py`: ~130 lines (was 700+)
- `colors.py`: ~230 lines
- `bars.py`: ~170 lines  
- `keys.py`: ~130 lines
- `groups.py`: ~140 lines
- `screens.py`: ~80 lines
- `hooks.py`: ~100 lines

### Key Features Preserved:
- ✅ Automatic wallust color reloading
- ✅ Wayland compatibility (no Xlib)
- ✅ Multi-screen auto-detection
- ✅ Clean error handling
- ✅ Manual reload keybinding (`Mod4 + Ctrl + C`)
- ✅ All original functionality intact

### Benefits of Modular Structure:
- **Easier maintenance** - Find and fix issues quickly
- **Better organization** - Related code grouped together
- **Simpler debugging** - Isolate problems to specific modules
- **Future extensibility** - Add features without cluttering main config
- **Code reusability** - Share modules across different configs

**Your qtile configuration is now professionally structured and highly maintainable!** 🎨✨