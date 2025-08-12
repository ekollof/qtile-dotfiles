# Icons Directory Structure

This directory contains the modern dynamic icon system for the qtile configuration.

## Directory Structure

### `icons/` (Static Source Icons)
- **Source icons** that are version controlled
- Contains original SVG/PNG files for reference
- Safe to modify and commit

### `icons/themed/` (Generated - Ignored)
- **Dynamically generated** themed icons
- Colors match your current theme automatically  
- **Not tracked in git** - regenerated on each system
- Created automatically when qtile starts

### `icons/dynamic/` (Generated - Ignored)
- **Runtime generated** icons based on system state
- Battery levels, network status, CPU usage, etc.
- **Not tracked in git** - created as needed
- Cached for performance

## Platform-Specific Mascots 🎨

The `platform` icon automatically shows the appropriate mascot for your OS:

- 🐧 **Linux**: Tux the penguin (black/white with colored beak)
- 🐡 **OpenBSD**: Puffy the pufferfish (colorful spikes and fins)
- 👹 **FreeBSD**: Beastie the daemon (red body with dark horns)
- 🏁 **NetBSD**: Flag logo (multi-colored stripes)
- 🍎 **macOS**: Apple logo (gradient with green leaf)
- 🪟 **Windows**: Four-pane logo (blue/green/yellow/red)
- 🖥️ **Unknown**: Generic computer (detailed monitor)

All mascots use **6-9 themed colors** and adapt to your color scheme!

## Dynamic Icon Features

### Multi-Color Theming
- Icons automatically use colors from your current theme
- **6-9 colors per icon** for proper contrast and depth
- Professional quality with highlights, shadows, and details

### System Integration  
- **Battery icons** show charge level and charging status
- **Network icons** indicate connection strength and activity
- **Volume icons** reflect current audio state
- **CPU/Memory icons** show usage levels with color coding

### Auto-Generation
Icons are created automatically:
- **On qtile startup** - themed icons generated
- **On color change** - icons regenerated with new colors
- **Runtime** - dynamic icons created as needed

## Legacy Icon Methods (Still Available)

The old icon system is still supported as fallback:

### 1. SVG Vector Icons
Uses crisp vector SVG images that scale perfectly.

### 2. Image Icons (PNG files) 
Uses bitmap PNG images in the status bar.

### 3. Nerd Font Icons
Uses Nerd Font character codes for icons.

### 4. Text Symbols
Uses simple text characters as icon replacements.

## Switching Icon Systems

```bash
cd ~/.config/qtile

# Use modern dynamic system (default)
python3 scripts/switch_icons.py dynamic

# Use static SVG icons  
python3 scripts/switch_icons.py svg

# Use bitmap images
python3 scripts/switch_icons.py image

# Use Nerd Font icons
python3 scripts/switch_icons.py nerd_font

# Check current status
python3 scripts/switch_icons.py status
```

## Manual Icon Regeneration

Icons regenerate automatically, but you can force it:

```python
from modules.bars import EnhancedBarManager
from modules.colors import color_manager
from qtile_config import get_config

config = get_config()
bar_manager = EnhancedBarManager(color_manager, config)
bar_manager.refresh_themed_icons()
```

## Why Generated Icons Are Ignored

Generated icons are **system-specific**:
- Different colors per user's theme
- Different mascots per operating system  
- Different system states (battery, network, etc.)
- Would cause merge conflicts between users

Only the **source code** that generates the icons is tracked in git.

## Available Icon Types

| Icon Name | Description | Colors Used | Dynamic |
|-----------|-------------|-------------|---------|
| platform | OS mascot | 6-9 themed colors | No |
| battery_* | Battery states | Level-based colors | Yes |
| wifi_* | Network strength | Signal-based colors | Yes |
| volume_* | Audio levels | Level-based colors | Yes |
| cpu_* | Processor load | Usage-based colors | Yes |
| memory_* | RAM usage | Usage-based colors | Yes |
| mail | Email indicator | Theme colors | No |
| updates | Update indicator | Warning colors | No |
| refresh | Refresh action | Accent colors | No |

## Credits

- **Platform Mascots**: Custom SVG implementations of official OS mascots
- **Dynamic System**: Built with modern Python 3.10+ features
- **Legacy Icons**: Feather Icons, Tabler Icons, DevIcons (MIT License)
