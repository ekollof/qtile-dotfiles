# Modern Qtile Configuration

A comprehensive, modular Qtile configuration with enhanced monitor detection, robust color management, and layout-aware key bindings.

## ✨ Features

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
- **Smart Resizing**: Grow/shrink commands adapt to current layout
- **Universal Navigation**: Consistent focus and window movement across all layouts
- **Layout Switching**: Quick access to all layouts (Tile, Max, BSP, MonadTall, Matrix)
- **Error-Free**: No command failures in incompatible layouts (e.g., resize in Max)

### 📋 **AwesomeWM-Style Hotkey Display**
- **Visual Guide**: `Super+S` shows categorized list of all shortcuts
- **Dynamic Theming**: Automatically matches current color scheme
- **Smart Categorization**: Groups by function (Window Management, Layout, System, etc.)
- **Multiple Backends**: Rofi (preferred) → dmenu → notifications

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
git clone <your-repo-url> ~/.config/qtile

# Start qtile (or restart if already running)
qtile cmd-obj -o cmd -f restart
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
| `Super+J/K/H/L` | Focus up/down/left/right |
| `Super+Shift+J/K/H/L` | Move window |
| `Super+Shift+L/H` | **Smart grow/shrink** (adapts to layout) |
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

```
qtile/
├── config.py                 # Main configuration file
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
    ├── COLOR_MANAGEMENT.md
    ├── HOTKEY_DISPLAY.md
    ├── MONITOR_DETECTION.md
    └── FEATURES.md
```

## 🔧 Customization

### Adding New Key Bindings
Edit `modules/keys.py`:
```python
Key([self.mod], "y", lazy.spawn("your-app"), desc="Launch your app"),
```

### Modifying Layouts
Edit `modules/groups.py`:
```python
# Add new layout
layout.YourLayout(
    margin=2,
    border_width=1,
    # ... your settings
),
```

### Changing Colors
The system automatically loads from pywal, but you can override in `modules/colors.py`:
```python
def _load_default_colors(self):
    return {
        "special": {
            "background": "#your-bg-color",
            # ... your colors
        }
    }
```

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
# Check color file status
python3 -c "from modules.colors import get_color_file_status; print(get_color_file_status())"

# Validate current colors
python3 -c "from modules.colors import validate_current_colors; validate_current_colors()"
```

**Key bindings not working:**
- Check qtile logs: `tail -f ~/.local/share/qtile/qtile.log`
- Verify key binding syntax in `modules/keys.py`
- Use `Super+S` to see all configured shortcuts

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
- [Color Management](docs/COLOR_MANAGEMENT.md) - Advanced color system features
- [Monitor Detection](docs/MONITOR_DETECTION.md) - Multi-monitor setup and troubleshooting
- [Hotkey Display](docs/HOTKEY_DISPLAY.md) - AwesomeWM-style hotkey guide
- [Features](docs/FEATURES.md) - Complete feature overview

## 🎯 Design Philosophy

This configuration prioritizes:
- **Reliability**: Robust error handling and graceful degradation
- **Consistency**: Layout-aware commands that work everywhere
- **Usability**: Clear visual feedback and comprehensive hotkey guide
- **Maintainability**: Modular structure and thorough documentation
- **Flexibility**: Easy customization without breaking core functionality

Built for daily use in demanding multi-monitor development environments.
