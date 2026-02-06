# Modern Qtile Configuration

A comprehensive, **DPI-aware** qtile configuration with **centralized settings**, platform detection, dynamic SVG icons, and robust cross-platform compatibility. Built for demanding multi-monitor environments with zero-hassle configuration management.

## ✨ Features

### 🎛️ **Centralized Configuration**

- **Single Configuration File**: All settings in `qtile_config.py` for easy management
- **Type Hints**: Better development experience with IDE autocompletion
- **Logical Organization**: Settings grouped by function (layout, apps, colors, etc.)
- **Easy Customization**: Change terminal, browser, layouts, or any setting in one place
- **DPI-Aware Settings**: Automatic scaling for fonts, bars, margins on high-DPI displays

### 📐 **DPI Awareness & High-DPI Support**

- **Automatic DPI Detection**: Multiple detection methods (xdpyinfo, xrandr, .Xresources, environment)
- **Intelligent Scaling**: All UI elements scale based on display DPI (96-240+ DPI supported)
- **Font Management**: Smart font fallbacks with DPI-appropriate sizing
- **Configurable Base Sizes**: Easy adjustment of font sizes and bar heights in `qtile_config.py`
- **Cross-Platform**: Works on X11 and Wayland with different DPI detection methods

### 🖼️ **Dynamic SVG Icon System**

- **Theme-Aware Icons**: Icons automatically match your pywal/wallust color scheme
- **Dynamic Generation**: Real-time icon creation based on system state
- **Scalable Vector Graphics**: Perfect scaling at any DPI or resolution
- **Fallback System**: Graceful degradation (SVG → PNG → Nerd Font → Text)
- **Memory Efficient**: Icons cached and generated on-demand
- **State Indicators**: Battery charging/discharging, network status, updates available

### 🖥️ **Multi-Monitor Support**

- **Automatic Detection**: Dynamic screen detection for X11 and Wayland
- **Hotplug Support**: Automatically reconfigures when monitors are connected/disconnected
- **Manual Control**: `Super+Ctrl+S` to manually reconfigure screens
- **4+ Monitor Support**: Tested with complex multi-monitor setups
- **DPI-Aware Scaling**: Each monitor's DPI handled independently

### 🎨 **Robust Color Management**

- **Pywal/Wallust Integration**: Automatic color scheme loading with validation
- **Backup System**: Multiple fallback levels (current → last good → backup → defaults)
- **File Monitoring**: Real-time color updates with hash-based change detection
- **Error Recovery**: Graceful handling of corrupted or missing color files
- **Theme Consistency**: Icons and UI elements automatically update with colors

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
- **DPI-Aware**: Popup windows scale appropriately for high-DPI displays

### 🪟 **Universal Window Management**

- **Universal Tiling**: ALL windows default to tiling (proper tiling WM philosophy)
- **Smart Floating Rules**: Only system dialogs, utilities, and transients float
- **Post-Restart Consistency**: Windows automatically re-tile after qtile restart
- **DPI-Scaled Gaps**: Clean spacing that scales with display resolution
- **Perfect Window Splits**: 50/50 tile splits, 60/40 MonadTall ratios
- **No App-Specific Code**: Works consistently for any application type

### 🏗️ **Modular Architecture**

- **Clean Structure**: Organized modules for bars, colors, groups, keys, screens
- **Easy Customization**: Modify individual components without touching core config
- **Maintainable**: Clear separation of concerns and comprehensive documentation
- **Platform Utilities**: Cross-platform compatibility layer
- **Font Management**: Intelligent font detection and fallback system

### 🔧 **Platform Detection & Compatibility**

- **Cross-Platform**: Native support for Linux and all BSD variants
- **Intelligent Detection**: Platform-specific application preferences
- **Command Availability**: Automatic fallbacks when tools aren't available
- **Environment Adaptation**: Desktop environment and compositor detection
- **Application Mapping**: Platform-appropriate defaults (terminals, browsers, etc.)

### 🐡 **Comprehensive BSD Support**

> **Note**: Official qtile packages are not yet available in OpenBSD ports. Use custom ports from [ekollof/openbsd-ports](https://github.com/ekollof/openbsd-ports).

#### OpenBSD Features

- **Native Package Updates**: Custom update widget using OpenBSD's sophisticated package version comparison (Dewey decimal system)
- **Battery Monitoring**: Custom battery widget using `apm` command with status indicators (charging ↑, discharging ↓, critical !, full =)
- **Multi-Version Packages**: Proper handling of packages with multiple concurrent versions (lua, python, ruby, etc.)
- **Mirror Detection**: Automatic detection of package mirror from `/etc/installurl` or fallback to CDN
- **Current vs Release**: Supports both OpenBSD-current (snapshots) and release versions

#### FreeBSD & NetBSD

- **Package Management**: Native `pkg` and `pkgin` integration
- **System Information**: BSD-specific `sysctl` integration
- **Hardware Detection**: Platform-appropriate tools and commands

#### Common BSD Features

- **Robust Error Handling**: Graceful fallback when BSD-specific commands are unavailable
- **Platform Detection**: Dual verification (platform + uname + tool existence) prevents false positives
- **Application Overrides**: BSD-specific application preferences and paths

## 🚀 Quick Start

### Automated Installation (Recommended)

The easiest way to install qtile and all dependencies is using the provided install script:

```bash
# Clone this configuration
git clone https://github.com/ekollof/qtile-dotfiles.git ~/.config/qtile

# Run the automated install script
cd ~/.config/qtile
./install.sh
```

The install script will:
- ✅ Detect your OS (Linux, OpenBSD, FreeBSD, NetBSD)
- ✅ Install all required system dependencies
- ✅ Install qtile and qtile-extras via pipx
- ✅ Set up desktop session entry
- ✅ Verify the installation

**Supported systems:**
- **Linux**: Ubuntu, Debian, Linux Mint, Arch, Manjaro, Fedora, RHEL/CentOS
- **BSD**: OpenBSD, FreeBSD, NetBSD

**Note**: The script uses `pipx` to install qtile, which is the recommended method for distributions without qtile packages (Ubuntu, Mint, etc.).

### Manual Installation

If you prefer to install manually or need to customize the installation:

#### Prerequisites

**Arch Linux:**

```bash
# Essential packages
sudo pacman -S qtile python-psutil

# Recommended for full functionality
sudo pacman -S rofi dmenu picom unclutter xrandr xscreensaver feh

# Optional: High-DPI support tools
sudo pacman -S xorg-xdpyinfo xorg-xrandr
```

**Ubuntu/Debian/Linux Mint (using pipx):**

```bash
# System dependencies
sudo apt-get install python3 python3-pip python3-venv pipx \
    python3-dev libpangocairo-1.0-0 python3-cairocffi python3-xcffib \
    libxcb-cursor0 libxcb-render0-dev libffi-dev libcairo2 libpango-1.0-0 \
    xterm feh picom xscreensaver rofi unclutter xsettingsd autorandr \
    flameshot network-manager-gnome pavucontrol

# Install qtile and qtile-extras via pipx
pipx install qtile --include-deps
pipx inject qtile qtile-extras
pipx inject qtile watchdog psutil

# Ensure pipx bin is in PATH
pipx ensurepath
```

**Fedora/RHEL/CentOS (using pipx):**

```bash
# System dependencies
sudo dnf install python3 python3-pip pipx python3-devel cairo cairo-devel \
    pango pango-devel gdk-pixbuf2 libffi-devel xcb-util-cursor \
    xterm feh picom xscreensaver rofi unclutter xsettingsd autorandr \
    flameshot NetworkManager-applet pavucontrol

# Install qtile and qtile-extras via pipx
pipx install qtile --include-deps
pipx inject qtile qtile-extras
pipx inject qtile watchdog psutil

# Ensure pipx bin is in PATH
pipx ensurepath
```

**OpenBSD:**

```bash
# NOTE: Official qtile packages are not yet available in OpenBSD ports
# Use custom ports from: https://github.com/ekollof/openbsd-ports

# Install custom qtile and qtile-extras ports first, then:

# Essential dependencies
doas pkg_add py3-psutil

# Recommended for full functionality  
doas pkg_add rofi dmenu picom dunst unclutter

# DPI detection tools (if available)
doas pkg_add xrandr xdpyinfo

# Battery and package monitoring (usually included)
# apm - for battery monitoring
# pkg_add - for package update checking
```

**FreeBSD:**

```bash
# Essential packages
pkg install qtile py39-psutil

# Recommended for full functionality
pkg install rofi dmenu picom dunst unclutter xrandr
```

**NetBSD:**

```bash
# Essential packages
pkgin install qtile py39-psutil

# Recommended for full functionality
pkgin install rofi dmenu picom dunst unclutter
```

# Test configuration
qtile check

# Test DPI detection (optional)
python3 ~/.config/qtile/scripts/show_dpi_info.py

# Start qtile (or restart if already running)
qtile cmd-obj -o cmd -f restart
```

### First Boot

1. **Check DPI Detection**: Run `python3 scripts/show_dpi_info.py` to verify scaling
2. **Test Hotkeys**: Press `Super+S` to see all available shortcuts
3. **Verify Colors**: Colors should load automatically from pywal/wallust
4. **Test Icons**: Status bar should show dynamic SVG icons that match your theme

## 🎛️ **Easy Customization**

All configuration is centralized in `qtile_config.py` - change any setting in one place! The configuration is **DPI-aware** and automatically scales for high-resolution displays.

### **Change Font Sizes (DPI-Aware)**

```python
# Edit qtile_config.py
@property
def preferred_fontsize(self) -> int:
    return 16  # Base font size (automatically DPI-scaled)

@property 
def preferred_icon_fontsize(self) -> int:
    return 20  # Base icon size (automatically DPI-scaled)

@property
def preferred_bar_height(self) -> int:
    return 32  # Base bar height (automatically DPI-scaled)
```

**Test font sizes first:**

```bash
# See how different sizes look on your display
python3 scripts/test_font_sizes.py

# Check your current DPI scaling
python3 scripts/show_dpi_info.py
```

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

### **Adjust Window Gaps (DPI-Scaled)**

```python
@property
def layout_defaults(self) -> Dict[str, Any]:
    return {
        'margin': scale_size(8),        # DPI-scaled gaps (base: 8px)
        'border_width': scale_size(2),  # DPI-scaled borders (base: 2px)
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

### **Configure Icon System**

```python
@property
def icon_method(self) -> str:
    return "svg_dynamic"  # Options: "svg_dynamic", "svg_static", "svg", "image", "nerd_font", "text"

@property
def svg_icon_size(self) -> int:
    return 24  # Base icon size (DPI-scaled automatically)
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

### **DPI-Specific Overrides**

The configuration automatically detects and scales for different DPI levels:

- **Standard DPI** (< 120): No scaling
- **High DPI** (120-179): 1.25-1.875x scaling  
- **Very High DPI** (180-239): 1.875-2.5x scaling
- **Ultra High DPI** (240+): 2.5x+ scaling

Manual overrides:

```python
# Force specific DPI scaling (rarely needed)
from modules.dpi_utils import DPIManager
dpi_manager = DPIManager()
dpi_manager._dpi = 144.0  # Force 1.5x scaling
```

## ⌨️ Key Bindings

### Essential

| Key | Action |
|-----|--------|
| `Super+Return` | Terminal |
| `Super+W` | Browser |
| `Super+P` | Application launcher |
| `Super+Q` | Close window |
| `Super+S` | **Show hotkey guide** (all shortcuts) |

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

### System & Advanced

| Key | Action |
|-----|--------|
| `Super+Shift+R` | Restart qtile |
| `Super+Shift+Q` | Quit qtile |
| `Super+Ctrl+C` | **Reload colors** |
| `Super+Ctrl+S` | **Reconfigure screens** |
| `Super+Ctrl+F` | **Force retile all windows** |

### Mouse Integration

| Action | Effect |
|--------|-------|
| **Mouse Warp Focus** | When enabled, cursor automatically moves to focused window |
| **Floating Drag** | Drag floating windows with mouse |
| **Resize Floating** | Resize floating windows by dragging edges |

> 💡 **Tip**: Press `Super+S` to see all shortcuts with descriptions categorized by function!

## 🎨 Color Schemes & Dynamic Icons

### Automatic Color Loading

The configuration automatically loads colors from:

1. `~/.cache/wal/colors.json` (pywal/wallust)
2. `~/.cache/wal/last_good_colors.json` (backup)
3. `~/.cache/wal/backups/` (timestamped backups)
4. Built-in defaults (fallback)

### Dynamic SVG Icons

Icons automatically update to match your color scheme:

- **Battery**: Shows charging/discharging state with color-coded indicators
- **Network**: Different icons for WiFi strength and ethernet
- **Updates**: System-specific package update counts
- **Temperature**: Color changes based on CPU temperature
- **System**: Platform mascots (Tux for Linux, Puffy for OpenBSD, etc.)

### Manual Color Reload

```bash
# After changing wallpaper/colors
qtile cmd-obj -o cmd -f function -a manual_color_reload
# Or use: Super+Ctrl+C

# Test icon generation
python3 -c "from modules.svg_utils import get_svg_utils; print('SVG system ready')"
```

## 🖥️ Monitor Management & DPI

### Automatic Detection

- **Multi-DPI Support**: Each monitor's DPI detected independently
- **Hotplug Events**: Automatic reconfiguration when monitors change
- **Display Protocols**: Supports both X11 and Wayland
- **Scaling Consistency**: UI elements scale appropriately per monitor

### Manual Control

```bash
# Reconfigure screens manually
qtile cmd-obj -o cmd -f reconfigure_screens
# Or use: Super+Ctrl+S

# External script
python3 ~/.config/qtile/reconfigure_screens.py

# Check current DPI settings
python3 ~/.config/qtile/scripts/show_dpi_info.py
```

### DPI Detection Methods

1. **xdpyinfo**: X11 display information (preferred)
2. **xrandr**: X11 monitor query
3. **~/.Xresources**: Manual DPI override (`Xft.dpi: 144`)
4. **Environment**: `QT_SCALE_FACTOR` and similar variables
5. **Fallback**: 96 DPI default

## 📁 Project Structure

```text
qtile/
├── qtile_config.py              # 🎛️ CENTRAL CONFIGURATION (edit this!)
├── config.py                    # Main qtile entry point
├── autostart.sh                # Startup applications
├── reconfigure_screens.py      # External screen reconfiguration
├── modules/                     # Modular components (25 modules)
│   ├── bars.py                 # Status bars and widgets (DPI-aware)
│   ├── client_hooks.py         # Client/window event handling
│   ├── color_management.py     # Advanced color management system
│   ├── colors.py               # Color management system
│   ├── commands.py             # Consolidated window/system commands
│   ├── config_validator.py     # Configuration validation system
│   ├── dependency_container.py # Dependency injection container
│   ├── dpi_utils.py            # DPI detection and scaling
│   ├── font_utils.py           # Font management and fallbacks
│   ├── groups.py               # Workspaces and layouts
│   ├── hook_manager.py         # Hook management orchestration
│   ├── hooks.py                # Hook system entry point
│   ├── hotkey_system.py        # Hotkey display system core
│   ├── hotkeys.py              # Hotkey display system entry point
│   ├── key_bindings.py         # Key binding definitions
│   ├── key_manager.py          # Key management orchestration
│   ├── keys.py                 # Key system entry point
│   ├── lifecycle_hooks.py      # Startup/screen lifecycle hooks
│   ├── notifications.py        # Notification system
│   ├── platform.py             # Cross-platform compatibility
│   ├── screens.py              # Screen detection and management
│   ├── svg_utils.py            # Dynamic SVG icon generation
│   └── window_manager.py       # Window management utilities
├── scripts/                    # Utility scripts
│   ├── show_dpi_info.py       # DPI detection testing
│   ├── test_font_sizes.py     # Font size preview
│   ├── qtile_log_monitor.py   # Log monitoring tool
│   ├── generate_docs.py       # Documentation generation
│   ├── audit_compliance.py    # Code quality auditing
│   └── count_updates.py       # Update counting utilities
├── icons/                      # Icon resources
│   ├── dynamic/               # Generated dynamic icons
│   ├── themed/                # Theme-aware icon cache
│   └── demo/                  # Example icons
├── contrib/                    # Additional configurations
│   └── dunst/dunstrc          # Notification daemon config
└── docs/                      # Comprehensive documentation
    ├── html/                  # Generated API documentation
    ├── CENTRALIZED_CONFIG.md  # Configuration system guide
    ├── COLOR_MANAGEMENT.md   # Color system features
    ├── DPI_AWARENESS.md      # High-DPI setup guide
    ├── HOTKEY_DISPLAY.md     # Hotkey guide setup
    ├── MONITOR_DETECTION.md  # Multi-monitor guide
    ├── PLATFORM_SUPPORT.md  # Cross-platform features
    └── FEATURES.md           # Complete feature overview
```

> 💡 **Want to customize something?** Start with `qtile_config.py` - it contains all the DPI-aware settings!

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

**DPI/Font size problems:**

```bash
# Check DPI detection
python3 scripts/show_dpi_info.py

# Test font sizes before changing config
python3 scripts/test_font_sizes.py

# Manual DPI override in ~/.Xresources
echo "Xft.dpi: 144" >> ~/.Xresources
xrdb ~/.Xresources

# Force qtile to re-detect DPI
qtile cmd-obj -o cmd -f restart
```

**Screen detection not working:**

```bash
# Check display detection
xrandr --query  # X11
wlr-randr       # Wayland (if available)

# Test screen detection
python3 -c "from modules.screens import get_screen_count; print(f'Detected: {get_screen_count()}')"

# Manual reconfiguration
qtile cmd-obj -o cmd -f reconfigure_screens
```

**Color loading issues:**

```bash
# Test color loading
python3 -c "from modules.colors import get_colors; colors = get_colors(); print(f'Colors loaded: {len(colors.get(\"colors\", {}))} entries')"

# Check color files
ls -la ~/.cache/wal/

# Manual color reload
python3 -c "from modules.colors import manual_color_reload; manual_color_reload()"

# Test SVG icon generation
python3 -c "from modules.svg_utils import get_svg_utils; svg = get_svg_utils(); print('SVG system ready')"
```

**Configuration problems:**

```bash
# Test configuration syntax
python3 -c "from qtile_config import get_config; print('Config loaded successfully')"

# Check DPI awareness
python3 -c "from qtile_config import get_config; c=get_config(); print(f'DPI: {c.dpi_info}')"

# Check platform detection
python3 -c "from qtile_config import get_config; c=get_config(); print(f'Platform: {c.platform_info.system}')"

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
- Check for conflicts: No duplicates should exist

**Platform-specific issues:**

```bash
# Test platform detection
python3 -c "from modules.platform_utils import get_platform_info; pi = get_platform_info(); print(f'Platform: {pi.system}, BSD: {pi.is_bsd}')"

# Check application availability
python3 -c "from modules.platform_utils import get_platform_config; pc = get_platform_config(); print('Platform config loaded')"

# Test font detection
python3 -c "from modules.font_utils import get_available_font; print(f'Font: {get_available_font(\"BerkeleyMono Nerd Font Mono\")}')"
```

**BSD-specific issues:**

```bash
# OpenBSD: Install qtile using custom ports (required as of August 2025)
# 1. Clone the ports repository:
git clone https://github.com/ekollof/openbsd-ports.git
# 2. Follow the build instructions in the repository

# Test OpenBSD package widget
python3 -c "from modules.bars import EnhancedBarManager; print('Package manager detected')"

# Test battery monitoring (OpenBSD)
apm -l  # Should show percentage (0-100)
apm -b  # Should show status (0=high, 1=low, 2=critical, 3=charging, 4=absent)

# Check package mirror (OpenBSD)
cat /etc/installurl  # Should show your package mirror

# FreeBSD package testing
pkg version -v | head -5

# NetBSD package testing  
pkgin list | head -5

# Verify BSD platform detection
python3 -c "import platform; print('Platform:', platform.system()); import subprocess; print('uname:', subprocess.check_output(['uname']).decode().strip())"

# Check qtile logs for BSD widget debug info
tail -f ~/.local/share/qtile/qtile.log | grep -i "bsd\|apm\|battery\|package"
```

**Icon/SVG issues:**

```bash
# Test SVG icon generation
python3 -c "from modules.svg_utils import create_themed_icon_cache; create_themed_icon_cache(); print('SVG cache created')"

# Check icon method configuration
python3 -c "from qtile_config import get_config; c = get_config(); print(f'Icon method: {c.icon_method}')"

# Regenerate icon cache
rm -rf ~/.config/qtile/icons/dynamic/
rm -rf ~/.config/qtile/icons/themed/
qtile cmd-obj -o cmd -f restart
```

### Log Files & Debugging

- **Qtile**: `~/.local/share/qtile/qtile.log`
- **Autostart**: `~/.config/qtile/autostart.log`  
- **DPI Detection**: Run `python3 scripts/show_dpi_info.py`
- **Font Testing**: Run `python3 scripts/test_font_sizes.py`
- **Log Monitoring**: `python3 scripts/qtile_log_monitor.py`

### Debug Mode

```bash
# Enable debug logging
python3 scripts/qtile_log_monitor.py --level debug

# Check configuration loading in debug mode
QTILE_DEBUG=1 qtile cmd-obj -o cmd -f restart

# Verbose DPI detection
python3 -c "import logging; logging.basicConfig(level=logging.DEBUG); from modules.dpi_utils import get_dpi_manager; dpi = get_dpi_manager(); print(f'DPI: {dpi.dpi}')"
```

## 🤝 Contributing

This is a personal configuration, but contributions are welcome:

### How to Contribute

- **Report Issues**: File detailed bug reports with system information
- **Suggest Features**: Propose improvements or new functionality  
- **Submit Pull Requests**: Bug fixes and feature implementations
- **Documentation**: Help improve guides and examples
- **Testing**: Verify compatibility on different platforms and DPI settings

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ekollof/qtile-dotfiles.git
cd qtile-dotfiles

# Test configuration
python3 -c "from qtile_config import get_config; print('Config OK')"

# Generate documentation (if modified)
python3 scripts/generate_docs.py

# Test on different DPI settings
python3 scripts/show_dpi_info.py
python3 scripts/test_font_sizes.py
```

### Platform Testing

When contributing, please test on:

- **Linux**: Arch, Ubuntu, Fedora with different DEs
- **BSD**: OpenBSD, FreeBSD, NetBSD if available
- **DPI**: Standard (96), High (144), Very High (192+)
- **Displays**: Single, dual, multi-monitor setups

### Code Standards

- Follow the [project guidelines](/.github/copilot-instructions.md)
- Use Python 3.10+ features and type hints
- Document functions with doxygen-compatible docstrings
- Ensure cross-platform compatibility
- Test DPI scaling on different displays

## 📚 Documentation

Comprehensive documentation available in the `docs/` directory:

- [**Centralized Configuration**](docs/CENTRALIZED_CONFIG.md) - Complete configuration guide
- [**DPI Awareness**](docs/DPI_AWARENESS.md) - High-DPI setup and scaling guide  
- [**Platform Support**](docs/PLATFORM_SUPPORT.md) - Cross-platform compatibility features
- [Color Management](docs/COLOR_MANAGEMENT.md) - Advanced color system features
- [Monitor Detection](docs/MONITOR_DETECTION.md) - Multi-monitor setup and troubleshooting
- [Hotkey Display](docs/HOTKEY_DISPLAY.md) - AwesomeWM-style hotkey guide
- [Features](docs/FEATURES.md) - Complete feature overview

## 🎯 Design Philosophy

This configuration prioritizes:

- **DPI Awareness**: Automatic scaling for any display resolution
- **Centralized Management**: All settings in one place (`qtile_config.py`)
- **Cross-Platform**: Native support for Linux and BSD systems
- **Reliability**: Robust error handling and graceful degradation
- **Consistency**: Layout-aware commands that work everywhere
- **Usability**: Clear visual feedback and comprehensive hotkey guide
- **Maintainability**: Modular structure and thorough documentation
- **Flexibility**: Easy customization without breaking core functionality
- **Performance**: Efficient SVG icon generation and caching

## 🆕 What's New

### **Recent Major Improvements**

- ✅ **Module Consolidation**: Reduced from 34 to 25 modules through intelligent consolidation
- ✅ **DPI Awareness**: Automatic scaling for all UI elements on high-DPI displays
- ✅ **Dynamic SVG Icons**: Theme-aware, scalable icons that match your color scheme
- ✅ **Platform Detection**: Native support for Linux, OpenBSD, FreeBSD, NetBSD
- ✅ **Font Management**: Intelligent font detection and fallback system
- ✅ **Centralized Configuration**: All settings now in `qtile_config.py`
- ✅ **Universal Tiling**: ALL windows default to tiling (proper tiling WM behavior)
- ✅ **Post-Restart Consistency**: Windows automatically re-tile after `Super+Shift+R`
- ✅ **Smart Floating Rules**: Only system dialogs and utilities float
- ✅ **Layout-Aware Commands**: Resize and normalize work perfectly in all layouts
- ✅ **Enhanced Hotkey Display**: Modular system with improved categorization
- ✅ **Cross-Platform Compatibility**: BSD-specific widgets and commands

### **Configuration Highlights**

- **DPI-Aware Scaling**: Automatic font, icon, and spacing adjustments
- **49+ key bindings** with layout-aware smart commands (no conflicts)
- **5 layouts** (Tile, MonadTall, BSP, Matrix, Max) with perfect ratios
- **30+ floating rules** for system utilities and dialogs
- **Universal tiling** for all applications (no app-specific code)
- **9 workspaces** with logical naming and layout assignments  
- **Dynamic window gaps** that scale with display DPI
- **Automatic retiling** after qtile restart
- **SVG icon cache** with theme integration
- **Platform-specific widgets** (BSD package updates, battery monitoring)

### **Technical Improvements**

- **Modular Architecture**: Clean separation of concerns across 25 consolidated modules
- **Error Recovery**: Comprehensive fallback systems for all components
- **Performance**: Efficient caching and lazy loading
- **Documentation**: Complete API documentation with Doxygen
- **Testing**: Utility scripts for configuration validation
- **Compatibility**: Support for Python 3.10+ features
- **Code Quality**: Ruff linting and formatting applied throughout

Built for daily use in demanding multi-monitor, high-DPI development environments with comprehensive cross-platform support! 🚀
