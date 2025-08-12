# Scripts Directory

This directory contains utility scripts for managing and customizing the qtile configuration.

## Available Scripts

### 🔤 `test_font_sizes.py`
**Test different font sizes before applying changes**

```bash
python3 scripts/test_font_sizes.py
```

**Features:**
- Shows how different font sizes look with your current DPI
- Displays both raw and DPI-scaled values
- Provides recommendations based on your display
- Shows current configuration settings

**Usage:**
1. Run the script to see available font size combinations
2. Choose the size that looks best for your setup
3. Edit `qtile_config.py` and modify the `preferred_fontsize` and `preferred_icon_fontsize` properties
4. Restart qtile with `Super+Ctrl+R`

### 🖼️ Icon Management Scripts
(Legacy scripts for the old icon system - mostly superseded by the new dynamic system)

#### `download_icons.py`
Download and process icons from various sources.

#### `fix_svg_colors.py` 
Adjust SVG icon colors to match your theme.

#### `switch_icons.py`
Switch between different icon systems (SVG, PNG, Nerd Font, etc.).

#### `improve_icons.py`
Enhance and optimize existing icons.

#### `preview_icons.py` 
Preview icons before applying them.

#### `show_dpi_info.py`
Display DPI information for your current setup.

## Quick Start

### Font Size Customization
```bash
# 1. Test different sizes
python3 scripts/test_font_sizes.py

# 2. Edit qtile_config.py - change these values:
def preferred_fontsize(self) -> int:
    return 14  # Larger text (was 12)

def preferred_icon_fontsize(self) -> int:
    return 18  # Larger icons (was 16)

# 3. Restart qtile
# Press Super+Ctrl+R
```

### Icon System (Legacy)
```bash
# Check current icon system
python3 scripts/switch_icons.py status

# Switch to different icon types
python3 scripts/switch_icons.py svg      # Vector icons
python3 scripts/switch_icons.py image    # Bitmap icons  
python3 scripts/switch_icons.py dynamic  # Modern dynamic system
```

## DPI Scaling

All scripts are DPI-aware and will automatically scale values for high-resolution displays. Use `show_dpi_info.py` to check your current DPI settings.

## Notes

- The **dynamic icon system** (new) automatically generates themed icons and is the recommended approach
- The **legacy icon scripts** are still available for compatibility and advanced customization
- Always restart qtile after making configuration changes
- Font size changes are immediately effective after restart
