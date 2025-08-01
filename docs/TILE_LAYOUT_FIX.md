# Tile Layout Configuration Fix

## 🐛 **Issue Fixed**
The Tile layout was not splitting windows evenly when new windows were spawned. This was due to missing configuration parameters.

## ✅ **Solution Applied**

### **Tile Layout Improvements**
```python
layout.Tile(
    margin=4,               # NEW: 4px gap between windows (was 2px)
    border_width=1,
    border_focus=colordict["special"]["foreground"],
    border_normal=colordict["special"]["background"],
    ratio=0.5,              # NEW: 50/50 split by default
    ratio_increment=0.1,    # NEW: 10% increment when resizing
    master_match=None,      # NEW: No specific master window rules
    expand=True,            # NEW: Allow windows to expand to fill space
    master_length=1,        # NEW: One window in master pane
    shift_windows=True,     # NEW: Allow shifting between panes
)
```

### **MonadTall Layout Improvements**
```python
layout.MonadTall(
    margin=4,                         # NEW: 4px gap between windows
    ratio=0.6,                        # Main window takes 60% width
    min_ratio=0.25,                   # Minimum 25% width
    max_ratio=0.85,                   # Maximum 85% width
    change_ratio=0.05,                # 5% change increments
    change_size=20,                   # 20px size changes
    new_client_position='after_current',  # Better window placement
)
```

### **BSP Layout Improvements**
```python
layout.Bsp(
    margin=4,               # NEW: 4px gap between windows
    fair=True,              # Even space distribution
    grow_amount=10,         # 10px grow/shrink increments
    lower_right=True,       # New windows in lower right
    ratio=1.6,             # Golden ratio for aesthetics
)
```

### **Matrix Layout Improvements**
```python
layout.Matrix(
    margin=4,               # NEW: 4px gap between windows
    border_width=1,
    # Automatic grid arrangement
)
```

## � **Window Spacing**

### **Gap Configuration**
All tiling layouts now use consistent 4px margins for clean window separation:

```python
margin=4,               # 4px gap around each window
border_width=1,         # 1px border for window focus indication
```

### **Visual Spacing**
- **Between Windows**: ~4px visible gap
- **Screen Edges**: 4px margin from screen borders
- **Border Focus**: 1px colored border on focused window
- **Professional Look**: Clean, modern spacing without being excessive

### **Layout-Specific Behavior**
| Layout | Gap Behavior |
|--------|--------------|
| **Tile** | Even gaps between main and secondary panes |
| **MonadTall** | Consistent spacing around main window and sidebar |
| **BSP** | Equal gaps in all binary splits |
| **Matrix** | Grid spacing with gaps between all cells |
| **Max** | No gaps (fullscreen) |
| **Floating** | 1px borders, manual positioning |

## �🎯 **What This Fixes**

### **Before (Problems)**
- ❌ New windows created uneven splits
- ❌ First window took entire screen space
- ❌ Manual resizing was imprecise
- ❌ No consistent window placement

### **After (Solutions)**
- ✅ **Even Splits**: New windows create 50/50 splits by default
- ✅ **Proper Ratios**: First window takes appropriate space (50% Tile, 60% MonadTall)
- ✅ **Precise Resizing**: 10% increments for predictable sizing
- ✅ **Smart Placement**: New windows placed logically
- ✅ **Expandable**: Windows expand to fill available space
- ✅ **Clean Gaps**: 4px margins create professional spacing between windows

## 🔧 **How It Works**

### **Tile Layout Behavior**
1. **First Window**: Takes 50% of screen (instead of 100%)
2. **Second Window**: Gets remaining 50% (even split)
3. **Additional Windows**: Stack in secondary pane
4. **Resizing**: `Super+Shift+L/H` adjusts in 10% increments

### **MonadTall Layout Behavior**
1. **Main Window**: Takes 60% of screen width
2. **Secondary Windows**: Share remaining 40% vertically
3. **New Windows**: Placed after current window
4. **Resizing**: 5% increments with min/max limits

### **BSP Layout Behavior**
1. **Fair Distribution**: All windows get equal space
2. **Smart Splits**: Uses golden ratio for aesthetics
3. **Predictable Placement**: New windows in lower-right
4. **Fine Control**: 10px grow/shrink increments

## 🎮 **Usage Guide**

### **Window Management**
| Action | Key | Result |
|--------|-----|--------|
| **Grow main** | `Super+Shift+L` | Increase main window size |
| **Shrink main** | `Super+Shift+H` | Decrease main window size |
| **Reset layout** | `Super+N` | Return to default ratios |
| **Toggle split** | `Super+Shift+Return` | Switch pane arrangements (Tile) |

### **Layout Switching**
| Layout | Key | Best For |
|--------|-----|----------|
| **Tile** | `Super+T` | Even splits, traditional tiling |
| **MonadTall** | `Super+Ctrl+T` | Main window + sidebar |
| **BSP** | `Super+B` | Automatic binary splits |
| **Matrix** | `Super+Ctrl+M` | Grid arrangement |
| **Max** | `Super+M` | Full-screen focus |

## 🧪 **Testing**

### **Verify the Fix**
1. **Switch to Tile layout**: `Super+T`
2. **Open first window**: `Super+Return` (terminal)
3. **Open second window**: `Super+Return` (another terminal)
4. **Expected**: Two windows side-by-side, 50/50 split
5. **Test resizing**: `Super+Shift+L` and `Super+Shift+H`

### **Compare Layouts**
- **Tile**: Side-by-side splits, manual control
- **MonadTall**: Main window + stacked sidebar
- **BSP**: Automatic binary space partitioning

## 🔄 **Migration Notes**

### **No Breaking Changes**
- All existing key bindings work the same
- Layout behavior is improved, not changed
- Backwards compatible with existing workflows

### **New Benefits**
- More predictable window sizing
- Better use of screen space
- Consistent behavior across all layouts
- Fine-grained resize control

The tile layout now behaves like a proper tiling window manager should, with even splits and predictable window placement!
