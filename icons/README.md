# Qtile Bitmap Icons Setup

This directory contains bitmap and vector icons to replace emoticons in your qtile status bar.

## Available Icon Methods

### 1. SVG Vector Icons (Recommended) ⭐
Uses crisp vector SVG images that scale perfectly at any size. Currently configured with white color (#F8F0FC) for dark themes.

### 2. Image Icons (PNG files)
Uses bitmap PNG images in the status bar. Clean and professional looking.

### 3. Nerd Font Icons 
Uses Nerd Font character codes for icons. Requires a Nerd Font to be installed.

### 4. Text Symbols
Uses simple text characters as icon replacements.

### 5. Original Emoticons
The original emoticon setup (🐍, 🔼, 🔄, etc.)

## Quick Start

1. **Use SVG icons (currently active):**
   ```bash
   cd ~/.config/qtile
   python3 scripts/switch_icons.py svg
   ```

2. **Switch to bitmap images:**
   ```bash
   python3 scripts/switch_icons.py image
   ```

3. **Switch to Nerd Font icons:**
   ```bash
   python3 scripts/switch_icons.py nerd_font
   ```

4. **Switch back to emoticons:**
   ```bash
   python3 scripts/switch_icons.py emoticons
   ```

5. **Check current status:**
   ```bash
   python3 scripts/switch_icons.py status
   ```

6. **Restart qtile to see changes:**
   Press `Super+Ctrl+R` or restart qtile

## Icon Mappings

| Original | Name | PNG File | SVG File | Nerd Font | Text |
|----------|------|----------|----------|-----------|------|
| 🐍 | Python | python.png | python.svg | \ue73c | Py |
| 🔼 | Updates | arrow-up.png | arrow-up.svg | \uf0aa | ↑ |
| 🔄 | Refresh | refresh.png | refresh.svg | \uf2f1 | ⟲ |
| 📭 | Mail | mail.png | mail.svg | \uf0e0 | ✉ |
| 🎫 | Ticket | ticket.png | ticket.svg | \uf3ff | 🎟 |
| 🌡 | Temperature | thermometer.png | thermometer.svg | \uf2c9 | T° |
| 🔋 | Battery | battery.png | battery.svg | \uf240 | ⚡ |
| ⚡ | Charging | zap.png | zap.svg | \uf0e7 | ⚡ |
| 🪫 | Low Battery | battery-low.png | battery-low.svg | \uf244 | ⚠ |

## Additional Icons Available

- clock.svg/clock.png - Clock/time icon
- monitor.svg/monitor.png - Monitor/display icon  
- cpu.svg/cpu.png - CPU/processor icon
- activity.svg/activity.png - Activity/performance icon
- wifi.svg/wifi.png - WiFi/network icon
- volume.svg/volume.png - Audio/volume icon

## Customization

### Adding New Icons

1. Add SVG files to this directory (preferred)
2. Or add PNG files directly
3. Update the icon mappings in `modules/bars_with_icons.py`

### Changing Icon Colors

For SVG icons:
```bash
# Restore original colors and re-apply with new color
python3 scripts/fix_svg_colors.py restore
# Edit the script to use your preferred color, then run:
python3 scripts/fix_svg_colors.py
```

### Changing Icon Size

For PNG icons, edit `icon_size` in `scripts/download_icons.py` and re-run:
```bash
python3 scripts/improve_icons.py
```

### Using Your Own Icons

Replace any PNG file in this directory with your preferred icon (keep same filename).

## Nerd Font Setup

If you want to use Nerd Font icons:

1. Install a Nerd Font: https://www.nerdfonts.com/
2. Update the font name in `bars_with_icons.py`:
   ```python
   font="YourNerdFont Mono"  # Replace with your font name
   ```

## Troubleshooting

### Icons not appearing
- Check that PNG files exist in the icons directory
- Verify file permissions are readable
- Try switching to text mode as fallback

### Nerd Font icons showing as squares
- Ensure you have a Nerd Font installed
- Update the font name in the configuration
- Check your terminal supports the font

### Script errors
- Ensure Python 3 and required modules are installed
- Check file paths and permissions
- Review qtile logs for error messages

## Files

- `icon_reference.json` - Icon mapping reference
- `*.svg` - Vector SVG icon files (recommended)
- `*.png` - Bitmap PNG icon files  
- `*.colorbackup` - Original SVG color backups
- `../scripts/download_icons.py` - Icon downloader script
- `../scripts/switch_icons.py` - Configuration switcher
- `../scripts/fix_svg_colors.py` - SVG color adjuster
- `../scripts/fix_svgs.py` - SVG compatibility fixer
- `../modules/bars_with_icons.py` - Enhanced bars module

## Current Status

✅ **SVG icons active** with white color (#F8F0FC)  
✅ **15 vector icons** ready for use  
✅ **15 bitmap icons** available as fallback  
✅ **Color backup files** preserved for easy restoration

## Credits

Icons sourced from:
- Feather Icons (https://feathericons.com/) - MIT License
- Tabler Icons (https://tabler.io/icons/) - MIT License  
- DevIcons (https://devicon.dev/) - MIT License
