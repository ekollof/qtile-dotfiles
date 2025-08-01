# Centralized Configuration System

## 📋 **Overview**

All qtile configuration is now centralized in `qtile_config.py` for easy management and consistency across modules.

## 🎯 **Benefits**

### **Before (Scattered Configuration)**
- ❌ Settings spread across multiple files
- ❌ Hardcoded values throughout modules
- ❌ Difficult to find and change settings
- ❌ Inconsistent behavior between modules
- ❌ No type hints or documentation

### **After (Centralized Configuration)**
- ✅ All settings in one file (`qtile_config.py`)
- ✅ Easy to modify any behavior
- ✅ Consistent configuration across all modules
- ✅ Type hints for better development experience
- ✅ Logical grouping of related settings
- ✅ Comprehensive documentation

## 📁 **Configuration Structure**

```python
qtile_config.py                 # Central configuration file
├── Core Settings              # Mod keys, terminal, browser
├── Application Commands       # Launcher, password manager, etc.
├── Layout Settings           # Margins, ratios, behavior
├── Floating Window Rules     # What windows should float
├── Workspace/Group Settings  # Workspaces and scratchpads
├── Color Management         # Color file paths and defaults
├── Monitor/Screen Settings  # Screen detection behavior
├── Autostart Settings       # Startup script configuration
├── Bar/Widget Settings      # Status bar configuration
└── Hotkey Display Settings  # Hotkey guide appearance
```

## 🛠️ **Common Customizations**

### **Change Terminal or Browser**
```python
@property
def terminal(self) -> str:
    return "alacritty"  # Change from "st"

@property 
def browser(self) -> str:
    return "firefox"    # Change from "brave"
```

### **Modify Layout Settings**
```python
@property
def layout_defaults(self) -> Dict[str, Any]:
    return {
        'margin': 6,        # Change gap between windows
        'border_width': 2,  # Change border thickness
    }

@property
def tile_layout(self) -> Dict[str, Any]:
    return {
        'ratio': 0.6,       # Change from 50/50 to 60/40 split
        'ratio_increment': 0.05,  # Smaller resize increments
    }
```

### **Add New Applications**
```python
@property
def applications(self) -> Dict[str, str]:
    return {
        'launcher': 'dmenu_run',           # Change from rofi
        'file_manager': 'thunar',          # Add new application
        'screenshot': 'flameshot gui',     # Add screenshot tool
        # ... existing apps
    }
```

### **Customize Workspaces**
```python
@property
def groups(self) -> List[tuple]:
    return [
        ('1:term', {'layout': 'tile'}),    # Change names/layouts
        ('2:web', {'layout': 'max'}),
        ('3:code', {'layout': 'monadtall'}),
        ('4:files', {'layout': 'tile'}),
        # Add more workspaces as needed
    ]
```

### **Add Floating Rules**
```python
@property
def floating_rules(self) -> List[Dict[str, str]]:
    return [
        # Existing rules...
        {'wm_class': 'your-app'},          # Add new floating app
        {'title': 'Preferences'},         # Float by title
        {'wm_class': 'Steam'},            # Float Steam windows
    ]
```

### **Configure Electron Apps**
```python
@property
def electron_apps(self) -> List[str]:
    return [
        # Existing apps...
        'your-electron-app',  # Add new electron app to force tile
        'custom-app',         # Any app with electron in the name
    ]
```

## 📊 **Current Configuration**

### **Core Settings**
- **Mod Key**: `mod4` (Super/Windows key)
- **Alt Key**: `mod1` (Alt key)
- **Terminal**: `st`
- **Browser**: `brave`

### **Layout Settings**
- **Margin**: `4px` (gap between windows)
- **Border Width**: `1px`
- **Tile Ratio**: `0.5` (50/50 split)
- **MonadTall Ratio**: `0.6` (60/40 split)
- **BSP**: Fair distribution with golden ratio

### **Applications**
- **Launcher**: `rofi -show run`
- **Password Manager**: `~/bin/getpass`
- **Clipboard**: `clipmenu`
- **Lock Screen**: `loginctl lock-session`

### **Workspaces**
- **9 workspaces**: 1:chat through 9:doc
- **2 scratchpads**: notepad and ncmpcpp
- **Default layout**: tile (except chat=max)

### **Window Rules**
- **30 floating rules**: Small utilities, dialogs, calculators
- **13 electron apps**: Forced to tile (VSCode, Discord, etc.)
- **9 force floating apps**: System utilities via hooks

## 🔧 **Module Integration**

### **How Modules Use Config**
```python
# In any module:
from qtile_config import get_config

class SomeManager:
    def __init__(self, color_manager):
        self.config = get_config()
        self.mod = self.config.mod_key        # Use centralized mod key
        self.terminal = self.config.terminal  # Use centralized terminal
        # ... rest of module uses self.config.*
```

### **Benefits for Development**
- **Type Hints**: IDE can provide autocompletion
- **Documentation**: Docstrings explain each setting
- **Consistency**: All modules use same configuration source
- **Maintainability**: Easy to find and change any setting

## 🚀 **Quick Customization Guide**

### **1. Edit Settings**
```bash
nvim ~/.config/qtile/qtile_config.py
```

### **2. Test Configuration**
```bash
cd ~/.config/qtile
python3 -c "from qtile_config import get_config; print('Config OK')"
```

### **3. Apply Changes**
```bash
# Restart qtile
qtile cmd-obj -o cmd -f restart
```

## 📝 **Example: Complete Customization**

```python
# In qtile_config.py - customize for your setup:

@property
def terminal(self) -> str:
    return "alacritty"  # Your preferred terminal

@property
def browser(self) -> str:
    return "firefox"    # Your preferred browser

@property
def layout_defaults(self) -> Dict[str, Any]:
    return {
        'margin': 8,        # Bigger gaps
        'border_width': 2,  # Thicker borders
    }

@property
def applications(self) -> Dict[str, str]:
    return {
        'launcher': 'dmenu_run',
        'file_manager': 'pcmanfm',
        'screenshot': 'maim -s | xclip -selection clipboard -t image/png',
        # ... your custom applications
    }
```

The centralized configuration makes qtile much easier to customize and maintain! 🎯
