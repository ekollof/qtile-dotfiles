# Hotkey Display Feature

This feature provides an AwesomeWM-style hotkey display that shows all configured keyboard shortcuts in a popup window.

## ✅ **Features**

### Visual Display
- **Popup Window**: Beautiful rofi-based popup with custom theming
- **Categorization**: Automatic grouping by function (Window Management, Layout, System, etc.)
- **Color Integration**: Dynamically uses current pywal/wallust colors
- **Clear Formatting**: Readable key combinations (Super+Shift+R instead of mod4+shift+r)

### Smart Categorization
- **Window Management**: Focus, move, close, floating controls
- **Layout Control**: Layout switching, tiling, maximizing
- **Group/Workspace**: Group switching and window movement
- **System**: Qtile restart, quit, color reload, screen reconfiguration
- **Applications**: Terminal, browser, and application launchers
- **Screen/Display**: Multi-monitor controls

### Multiple Fallbacks
- **Primary**: Rofi with custom theme
- **Secondary**: Dmenu with color matching
- **Tertiary**: Notification with basic shortcuts

## 🚀 **Usage**

### Activation
```
Super+S    Show hotkey display popup
```

### Navigation
- **Escape/Enter**: Close the popup
- **Arrow Keys**: Navigate through the list (rofi only)
- **Type**: Filter shortcuts by typing (rofi only)

## 🎨 **Appearance**

### Theming
The hotkey display automatically adapts to your current color scheme:
- **Background**: Uses pywal background color
- **Foreground**: Uses pywal foreground color  
- **Accent**: Uses pywal blue/accent color for highlights
- **Transparency**: Semi-transparent background for desktop visibility

### Layout
```
=== Window Management ===
Super+J                   Move focus down
Super+K                   Move focus up
Super+Q                   Close window
Super+F                   Toggle floating

=== System ===
Super+Shift+R             Restart Qtile
Super+Ctrl+C              Reload colors
Super+Ctrl+S              Reconfigure screens
```

## 🔧 **Configuration**

### Dependencies
- **Preferred**: `rofi` - Advanced display with theming
- **Fallback**: `dmenu` - Simple menu display
- **Final**: `notify-send` - Basic notification

### Installation
```bash
# Arch Linux
sudo pacman -S rofi

# Ubuntu/Debian  
sudo apt install rofi

# Fedora
sudo dnf install rofi
```

### Customization
The hotkey display automatically inherits your qtile color scheme, but you can customize the rofi theme in `modules/hotkeys.py`:

```python
def _get_rofi_theme(self):
    # Modify the rofi theme here
    colors = self._get_colors()
    return f"""
    * {{
        font: "Your Font 12";
        width: 1400;  # Adjust width
    }}
    """
```

## 🛠 **Technical Details**

### Key Detection
- Automatically extracts all configured key bindings
- Parses modifiers and key combinations
- Generates human-readable descriptions

### Color Integration
- Reads current pywal/wallust colors
- Falls back to sensible defaults if no color scheme
- Updates theme dynamically when colors change

### Error Handling
- Graceful degradation through multiple display methods
- Proper timeout handling for rofi/dmenu
- Comprehensive logging for troubleshooting

## 📋 **Categories**

### Window Management
- Focus navigation (Super+J/K)
- Window movement (Super+Shift+J/K)
- Window resizing (Super+H/L)
- Floating toggle (Super+F)
- Window closing (Super+Q)

### Layout Control
- Layout switching (Super+Tab)
- Specific layouts (Super+T for tile, Super+M for max)
- Stack manipulation

### System
- Qtile restart (Super+Shift+R)
- Qtile quit (Super+Shift+Q)
- Color reload (Super+Ctrl+C)
- Screen reconfiguration (Super+Ctrl+S)

### Applications
- Terminal (Super+Return)
- Browser (Super+W)
- Application launcher (Super+P)
- Password manager (Super+Shift+P)

## 🧪 **Testing**

### Test the Feature
```bash
# Test hotkey display generation
python3 /home/ekollof/.config/qtile/test_hotkey_display.py

# Test in running qtile
# Press Super+S to show popup
```

### Troubleshooting
```bash
# Check if rofi is installed
which rofi

# Check if dmenu is available
which dmenu

# View qtile logs for errors
tail -f ~/.local/share/qtile/qtile.log

# Test color integration
python3 -c "from modules.hotkeys import HotkeyDisplay; print(HotkeyDisplay(None)._get_colors())"
```

## 🔄 **Comparison with AwesomeWM**

### Similarities
- **Keybinding**: Super+S activation
- **Popup Display**: Modal window showing shortcuts
- **Categorization**: Organized by function
- **Visual Appeal**: Clean, readable layout

### Enhancements
- **Color Integration**: Automatically matches your theme
- **Better Categorization**: More intelligent grouping
- **Multiple Fallbacks**: Works even without rofi
- **Dynamic Updates**: Reflects actual configured shortcuts

The hotkey display brings the convenience of AwesomeWM's hotkey viewer to Qtile with enhanced theming and better integration with the overall configuration system.
