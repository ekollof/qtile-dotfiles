# Modern Qtile Configuration

A comprehensive, modular Qtile configuration with **centralized settings**, enhanced monitor detection, robust color management, and layout-aware key bindings.

## ✨ Features

### 🎛️ **Centralized Configuration**

- **Single Configuration File**: All settings in `qtile_config.py` for easy management
- **Type Hints**: Better development experience with IDE autocompletion
- **Logical Organization**: Settings grouped by function (layout, apps, colors, etc.)
- **Easy Customization**: Change terminal, browser, layouts, or any setting in one place

### 🖥️ **Multi-Monitor Support**

- **Automatic Detection**: Dynamic screen detection for X11 and Wayland
- **Hotplug Support**: Automatically reconfigures when monitors are connected/disconnected
- **Manual Control**: `Super+Ctrl+S` to manually reconfigure screens
- **4+ Monitor Support**: Tested with complex multi-monitor setups

### 🎨 **Robust Color Management**

- **Pywal/Wallust Integration**: Automatic color scheme loading with validation
- **Backup System**: Multiple fallback levels (current → last good → backup → defaults)
- **File Monitoring**: Real-time color updates with hash-based change detection
- **Error Recovery**: Graceful handling of corrupted or missing color files

### ⌨️ **Layout-Aware Key Bindings**

- **Universal Tiling**: All windows default to tiling (proper tiling WM behavior)
- **Smart Resizing**: Grow/shrink commands adapt to current layout
- **Universal Navigation**: Consistent focus and window movement across all layouts
- **Layout Switching**: Quick access to all layouts (Tile, Max, BSP, MonadTall, Matrix)
- **Error-Free**: No command failures in incompatible layouts (e.g., resize in Max)
- **Post-Restart Consistency**: All windows automatically re-tile after `Super+Shift+R`

### 📋 **AwesomeWM-Style Hotkey Display**

- **Visual Guide**: `Super+S` shows categorized list of all shortcuts
- **Dynamic Theming**: Automatically matches current color scheme
- **Smart Categorization**: Groups by function (Window Management, Layout, System, etc.)
- **Multiple Backends**: Rofi (preferred) → dmenu → notifications

### 🪟 **Universal Window Management**

- **Universal Tiling**: ALL windows default to tiling (proper tiling WM philosophy)
- **Smart Floating Rules**: Only system dialogs, utilities, and transients float
- **Post-Restart Consistency**: Windows automatically re-tile after qtile restart
- **Precise Window Gaps**: Clean 4px spacing between windows
- **Perfect Window Splits**: 50/50 tile splits, 60/40 MonadTall ratios
- **No App-Specific Code**: Works consistently for any application type

### 🏗️ **Modular Architecture**

- **Clean Structure**: Organized modules for bars, colors, groups, keys, screens
- **Easy Customization**: Modify individual components without touching core config
- **Maintainable**: Clear separation of concerns and comprehensive documentation

## 🚀 Quick Start

### Prerequisites

```bash
# Essential
sudo pacman -S qtile python-psutil

# Recommended for full functionality
sudo pacman -S rofi dmenu picom dunst unclutter xrandr
```

### Installation

```bash
# Backup existing config (if any)
mv ~/.config/qtile ~/.config/qtile.backup

# Clone this configuration
git clone https://github.com/ekollof/qtile-dotfiles.git ~/.config/qtile

# Start qtile (or restart if already running)
qtile cmd-obj -o cmd -f restart
```

## 🎛️ **Easy Customization**

All configuration is centralized in `qtile_config.py` - change any setting in one place!

### **Change Applications**

```python
# Edit qtile_config.py
@property
def terminal(self) -> str:
    return "alacritty"  # Change from "st"

@property 
def browser(self) -> str:
    return "firefox"    # Change from "brave"
```

### **Adjust Window Gaps**

```python
@property
def layout_defaults(self) -> Dict[str, Any]:
    return {
        'margin': 8,        # Change from 4px to 8px gaps
        'border_width': 2,  # Thicker borders
    }
```

### **Customize Workspaces**

```python
@property
def groups(self) -> List[tuple]:
    return [
        ('1:term', {'layout': 'tile'}),
        ('2:web', {'layout': 'max'}),
        ('3:code', {'layout': 'monadtall'}),
        # Add your own workspaces
    ]
```

### **Add Applications**

```python
@property
def applications(self) -> Dict[str, str]:
    return {
        'launcher': 'dmenu_run',           # Change launcher
        'file_manager': 'thunar',          # Add file manager
        'screenshot': 'flameshot gui',     # Add screenshot tool
        # ... existing apps
    }
```

## ⌨️ Key Bindings

### Essential

| Key | Action |
|-----|--------|
| `Super+Return` | Terminal |
| `Super+W` | Browser |
| `Super+P` | Application launcher |
| `Super+Q` | Close window |
| `Super+S` | **Show hotkey guide** |

### Window Management

| Key | Action |
|-----|--------|
| `Super+H/J/K/L` | Focus left/down/up/right |
| `Super+Shift+H/J/K/L` | Move window left/down/up/right |
| `Super+Ctrl+H/L` | **Smart resize** (shrink/grow, adapts to layout) |
| `Super+Ctrl+J/K` | **Smart resize** (vertical, adapts to layout) |
| `Super+N` | **Normalize/reset layout** (works in all layouts) |
| `Super+F` | Toggle floating |
| `Super+Shift+F` | Toggle fullscreen |

### Layouts

| Key | Action |
|-----|--------|
| `Super+Tab` | Next layout |
| `Super+T` | Tile layout |
| `Super+M` | Max layout |
| `Super+B` | BSP layout |
| `Super+Ctrl+T` | MonadTall layout |
| `Super+Ctrl+M` | Matrix layout |

### System

| Key | Action |
|-----|--------|
| `Super+Shift+R` | Restart qtile |
| `Super+Shift+Q` | Quit qtile |
| `Super+Ctrl+C` | Reload colors |
| `Super+Ctrl+S` | **Reconfigure screens** |
| `Super+Ctrl+F` | **Force retile all windows** |

> 💡 **Tip**: Press `Super+S` to see all shortcuts with descriptions!

## 🎨 Color Schemes

### Automatic Color Loading

The configuration automatically loads colors from:

1. `~/.cache/wal/colors.json` (pywal/wallust)
2. `~/.cache/wal/last_good_colors.json` (backup)
3. `~/.cache/wal/backups/` (timestamped backups)
4. Built-in defaults (fallback)

### Manual Color Reload

```bash
# After changing wallpaper/colors
qtile cmd-obj -o cmd -f function -a manual_color_reload
# Or use: Super+Ctrl+C
```

## 🖥️ Monitor Management

### Automatic Detection

- Monitors are automatically detected on startup
- Hotplug events trigger automatic reconfiguration
- Supports both X11 and Wayland display protocols

### Manual Control

```bash
# Reconfigure screens manually
qtile cmd-obj -o cmd -f reconfigure_screens
# Or use: Super+Ctrl+S

# External script
python3 ~/.config/qtile/reconfigure_screens.py
```

## 📁 Project Structure

```text
qtile/
├── qtile_config.py           # 🎛️ CENTRAL CONFIGURATION (edit this!)
├── config.py                 # Main qtile entry point
├── autostart.sh             # Startup applications
├── reconfigure_screens.py   # External screen reconfiguration
├── modules/                  # Modular components
│   ├── bars.py              # Status bars and widgets
│   ├── colors.py            # Color management system
│   ├── groups.py            # Workspaces and layouts
│   ├── hooks.py             # Event hooks and automation
│   ├── hotkeys.py           # Hotkey display system
│   ├── keys.py              # Key bindings (layout-aware)
│   └── screens.py           # Screen detection and management
├── contrib/                  # Additional configurations
│   └── dunst/dunstrc        # Notification daemon config
└── docs/                    # Documentation
    ├── CENTRALIZED_CONFIG.md # Configuration system guide
    ├── COLOR_MANAGEMENT.md  # Color system features
    ├── HOTKEY_DISPLAY.md    # Hotkey guide setup
    ├── MONITOR_DETECTION.md # Multi-monitor guide
    ├── TILE_LAYOUT_FIX.md   # Window layout improvements
    └── FEATURES.md          # Complete feature overview
```

> 💡 **Want to customize something?** Start with `qtile_config.py` - it contains all the settings!

## 🔧 Customization

### Easy Configuration Changes

Everything is configured in `qtile_config.py` - no need to hunt through multiple files!

```bash
# Edit the central configuration
nvim ~/.config/qtile/qtile_config.py

# Test your changes
python3 -c "from qtile_config import get_config; print('Config OK')"

# Apply changes
qtile cmd-obj -o cmd -f restart
```

### **Adding New Key Bindings**

```python
# In qtile_config.py applications section:
@property
def applications(self) -> Dict[str, str]:
    return {
        'your_app': 'your-command',  # Add your application
        # ... existing apps
    }

# Key binding automatically created in keys.py
```

### **Modifying Layouts**

```python
# In qtile_config.py:
@property
def tile_layout(self) -> Dict[str, Any]:
    return {
        'ratio': 0.6,              # Change split ratio
        'ratio_increment': 0.05,   # Smaller adjustments
        # ... other tile settings
    }
```

### **Changing Colors**

The system automatically loads from pywal, but you can override defaults:

```python
# In qtile_config.py:
@property
def default_colors(self) -> Dict[str, Dict[str, str]]:
    return {
        "special": {
            "background": "#your-bg-color",
            "foreground": "#your-fg-color",
        }
        # ... your custom colors
    }
```

### **Adding Window Rules**

```python
# In qtile_config.py:
@property
def floating_rules(self) -> List[Dict[str, str]]:
    return [
        {'wm_class': 'your-app'},      # Float specific app
        {'title': 'Preferences'},     # Float by window title
        # ... existing rules
    ]

# Force apps to always float:
@property
def force_floating_apps(self) -> List[str]:
    return [
        'your-floating-app',  # Add to force floating
        # ... existing apps
    ]
```

**Note**: By default, ALL windows tile unless explicitly in floating rules. This is proper tiling WM behavior!

## 🛠️ Troubleshooting

### Common Issues

**Screen detection not working:**

```bash
# Check xrandr output
xrandr --query

# Test screen detection
python3 -c "from modules.screens import get_screen_count; print(f'Detected: {get_screen_count()}')"

# Manual reconfiguration
qtile cmd-obj -o cmd -f reconfigure_screens
```

**Color loading issues:**

```bash
# Test color loading
python3 -c "from modules.colors import get_colors; print('Colors loaded:', len(get_colors().get('colors', {})), 'color entries')"

# Manual color reload
python3 -c "from modules.colors import manual_color_reload; manual_color_reload()"
```

**Configuration problems:**

```bash
# Test configuration syntax
python3 -c "from qtile_config import get_config; print('Config loaded successfully')"

# Check specific settings
python3 -c "from qtile_config import get_config; c=get_config(); print(f'Terminal: {c.terminal}, Browser: {c.browser}')"
```

**Window tiling not working after restart:**

```bash
# Force retile all windows manually
qtile cmd-obj -o cmd -f function -a manual_retile_all
# Or use: Super+Ctrl+F

# Check window floating rules
python3 -c "from modules.hooks import create_hook_manager; from modules.colors import color_manager; hm = create_hook_manager(color_manager); print('Hook manager loaded')"
```

**Key bindings not working:**

- Check qtile logs: `tail -f ~/.local/share/qtile/qtile.log`
- Verify configuration: `python3 -c "from modules.keys import create_key_manager; print('Keys OK')"`
- Use `Super+S` to see all configured shortcuts
- Check for conflicts: No duplicates should exist (49 unique bindings)

### Log Files

- **Qtile**: `~/.local/share/qtile/qtile.log`
- **Autostart**: `~/.config/qtile/autostart.log`

## 🤝 Contributing

This is a personal configuration, but feel free to:

- Report issues or suggest improvements
- Fork and adapt for your own use
- Share interesting modifications

## 📚 Documentation

Detailed documentation available in the `docs/` directory:

- [**Centralized Configuration**](docs/CENTRALIZED_CONFIG.md) - Complete configuration guide
- [Color Management](docs/COLOR_MANAGEMENT.md) - Advanced color system features
- [Monitor Detection](docs/MONITOR_DETECTION.md) - Multi-monitor setup and troubleshooting
- [Hotkey Display](docs/HOTKEY_DISPLAY.md) - AwesomeWM-style hotkey guide
- [Tile Layout Fix](docs/TILE_LAYOUT_FIX.md) - Window layout improvements and spacing
- [Features](docs/FEATURES.md) - Complete feature overview

## 🎯 Design Philosophy

This configuration prioritizes:

- **Centralized Management**: All settings in one place (`qtile_config.py`)
- **Reliability**: Robust error handling and graceful degradation
- **Consistency**: Layout-aware commands that work everywhere
- **Usability**: Clear visual feedback and comprehensive hotkey guide
- **Maintainability**: Modular structure and thorough documentation
- **Flexibility**: Easy customization without breaking core functionality

## 🆕 What's New

### **Recent Major Improvements**

- ✅ **Centralized Configuration**: All settings now in `qtile_config.py`
- ✅ **Universal Tiling**: ALL windows default to tiling (proper tiling WM behavior)
- ✅ **Post-Restart Consistency**: Windows automatically re-tile after `Super+Shift+R`
- ✅ **Perfect Window Gaps**: Clean 4px spacing between all windows
- ✅ **Smart Floating Rules**: Only system dialogs and utilities float
- ✅ **Layout-Aware Commands**: Resize and normalize work perfectly in all layouts
- ✅ **Improved Hotkey Display**: Descriptive labels (not just "Spawn")
- ✅ **No Key Conflicts**: 49 unique key bindings with no duplicates

### **Configuration Highlights**

- **49 key bindings** with layout-aware smart commands (no conflicts)
- **5 layouts** (Tile, MonadTall, BSP, Matrix, Max) with perfect ratios
- **30 floating rules** for system utilities and dialogs
- **Universal tiling** for all applications (no app-specific code)
- **9 workspaces** with logical naming and layout assignments
- **4px window gaps** for professional appearance
- **Automatic retiling** after qtile restart

Built for daily use in demanding multi-monitor development environments with zero-hassle configuration management! 🚀
