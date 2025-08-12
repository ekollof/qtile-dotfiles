# Dynamic SVG Icons Usage Guide

This guide explains how to use the dynamic SVG icon generation system in your qtile configuration. The system provides theme-aware, scalable icons that automatically adapt to your color scheme and system state.

## Quick Start

### Enable SVG Icons

Add these settings to your `qtile_config.py`:

```python
@property
def use_svg_bar_manager(self) -> bool:
    """Enable enhanced SVG bar manager"""
    return True

@property
def svg_icon_method(self) -> str:
    """Choose icon rendering method"""
    return "svg_dynamic"  # Options: svg_dynamic, svg_static, svg, image, nerd_font, text
```

### Restart Qtile

After enabling SVG icons, restart qtile to see the new dynamic icons in your bar.

## Icon Methods

### svg_dynamic (Recommended)
- **Description**: Generates icons in real-time based on system state
- **Features**: Battery level indicators, WiFi strength, volume levels, CPU/memory usage
- **Example**: Battery icon changes color and fill based on actual charge level

### svg_static
- **Description**: Uses pre-generated themed static icons
- **Features**: Fast loading, consistent appearance
- **Use case**: When you prefer consistent icons over dynamic feedback

### svg
- **Description**: Recolors existing SVG files with current theme
- **Features**: Uses your existing SVG icon files
- **Use case**: When you have custom SVG icons you want to theme

## Configuration Examples

### Basic Configuration

```python
# In qtile_config.py
@property
def use_svg_bar_manager(self) -> bool:
    return True

@property
def svg_icon_method(self) -> str:
    return "svg_dynamic"

@property
def svg_icon_size(self) -> int:
    return 24  # Base size (automatically DPI-scaled)
```

### Advanced Configuration

```python
# Custom icon directory
@property
def svg_icon_directory(self) -> str:
    return f"{self.home}/.config/qtile/custom_icons"

# Performance tuning
@property
def svg_cache_enabled(self) -> bool:
    return True

@property
def svg_update_interval(self) -> int:
    return 5  # Update dynamic icons every 5 seconds
```

## Dynamic Icon Features

### Battery Icons
- **Green**: 75-100% charge
- **Blue**: 50-74% charge  
- **Yellow**: 25-49% charge
- **Orange**: 10-24% charge
- **Red**: Below 10% charge
- **Lightning bolt**: Charging indicator

### WiFi Icons
- **Signal strength**: 0-3 bars based on connection quality
- **Disconnected**: Grayed out with X overlay
- **Connected**: Colored based on signal strength

### Volume Icons
- **High volume**: Speaker with 3 arcs
- **Medium volume**: Speaker with 2 arcs
- **Low volume**: Speaker with 1 arc
- **Muted**: Speaker with red X

### System Monitoring Icons
- **CPU**: Chip icon with usage-colored center
- **Memory**: RAM stick with usage fill indicator
- **Network**: Ethernet connector with activity arrows

## Customization

### Creating Custom Icons

```python
from modules.svg_utils import SVGBuilder, IconGenerator

# Create custom icon generator
generator = IconGenerator(color_manager, size=32)

# Generate custom battery icon
def custom_battery_icon(level: int) -> str:
    builder = SVGBuilder(32, 32)
    
    # Your custom battery design
    builder.add_rect(4, 8, 24, 16, fill="none", stroke="#ffffff", stroke_width=2)
    builder.add_rect(28, 12, 4, 8, fill="#ffffff")
    
    # Custom fill based on level
    fill_width = (level / 100) * 22
    fill_color = "#00ff00" if level > 50 else "#ff0000"
    builder.add_rect(5, 9, fill_width, 14, fill=fill_color)
    
    return builder.build()
```

### Color Theming

```python
# Custom color overrides
custom_colors = {
    "foreground": "#ffffff",
    "background": "#000000", 
    "accent": "#3366cc",
    "warning": "#ffaa00",
    "error": "#ff3333",
}

# Apply to existing icon
themed_icon = svg_manipulator.theme_colorize(svg_icon, custom_colors)
```

### Icon Scaling

```python
# Scale icon for high DPI displays
scaled_icon = svg_manipulator.scale_svg(svg_icon, 2.0)  # 2x scaling

# DPI-aware scaling (automatic)
from modules.dpi_utils import scale_size
icon_size = scale_size(24)  # Automatically scales based on DPI
```

## Integration Examples

### Custom Widget with Dynamic Icon

```python
class CustomWidget(widget.base.InLoopPollText):
    def __init__(self, **config):
        super().__init__(**config)
        self.icon_generator = IconGenerator(color_manager)
        
    def poll(self):
        # Get system data
        cpu_usage = self.get_cpu_usage()
        
        # Generate dynamic icon
        icon_path = self.create_dynamic_cpu_icon(cpu_usage)
        
        return f"CPU: {cpu_usage:.1f}%"
        
    def create_dynamic_cpu_icon(self, usage):
        svg_content = self.icon_generator.cpu_icon(usage / 100)
        icon_path = Path("~/.config/qtile/icons/dynamic/cpu_current.svg")
        icon_path.write_text(svg_content)
        return str(icon_path)
```

### Script Integration

```python
# Add to script widget configuration
script_configs = [
    {
        'script_path': '~/bin/custom_monitor.sh',
        'icon_generator': lambda: icon_generator.cpu_icon(get_cpu_usage()),
        'update_interval': 5,
        'name': 'custom monitor'
    }
]
```

## Performance Optimization

### Caching

The system automatically caches generated icons to improve performance:

```bash
# Cache locations
~/.config/qtile/icons/dynamic/     # Real-time generated icons
~/.config/qtile/icons/themed/      # Themed static icons
```

### Update Intervals

Configure update frequencies for dynamic icons:

```python
# Faster updates for critical information
battery_update_interval = 30      # Battery: every 30 seconds
volume_update_interval = 1        # Volume: every second
cpu_update_interval = 5           # CPU: every 5 seconds
network_update_interval = 5       # Network: every 5 seconds
```

### Resource Usage

- **Memory**: ~1-2MB for icon cache
- **CPU**: <1% for icon generation
- **Disk**: ~100KB for cached icons

## Troubleshooting

### Icons Not Appearing

1. **Check SVG support**:
   ```bash
   python3 scripts/test_svg_icons.py
   ```

2. **Verify configuration**:
   ```python
   from modules.bar_factory import get_bar_manager_status
   status = get_bar_manager_status(config)
   print(status)
   ```

3. **Check file permissions**:
   ```bash
   ls -la ~/.config/qtile/icons/
   ```

### Fallback Behavior

The system gracefully falls back through these methods:
1. svg_dynamic → svg_static → svg → image → nerd_font → text

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('qtile').setLevel(logging.DEBUG)
```

### Common Issues

#### "SVG support not available"
- **Cause**: Missing dependencies or import errors
- **Solution**: Run test script to identify specific issues

#### "Icons appear as text"
- **Cause**: SVG files not found or corrupted
- **Solution**: Regenerate icon cache or check file paths

#### "Icons not updating"
- **Cause**: Cache not refreshing
- **Solution**: Clear dynamic icon cache directory

## Testing

### Run Test Suite

```bash
cd ~/.config/qtile
python3 scripts/test_svg_icons.py
```

### Manual Testing

```python
# Test icon generation
from modules.svg_utils import IconGenerator
from modules.colors import color_manager

generator = IconGenerator(color_manager)
battery_svg = generator.battery_icon(75)
print("✓ Icon generation working")

# Test bar manager
from modules.bar_factory import create_bar_manager
from qtile_config import get_config

config = get_config()
bar_manager = create_bar_manager(color_manager, config)
print(f"✓ Using {type(bar_manager).__name__}")
```

## Migration Guide

### From Static Icons

1. **Enable SVG system**:
   ```python
   use_svg_bar_manager = True
   svg_icon_method = "svg"  # Start with existing SVG files
   ```

2. **Test compatibility**:
   ```bash
   python3 scripts/test_svg_icons.py
   ```

3. **Gradually enable dynamic features**:
   ```python
   svg_icon_method = "svg_dynamic"  # Enable dynamic generation
   ```

### From Text/Emoji Icons

1. **Enable with fallback**:
   ```python
   use_svg_bar_manager = True
   svg_icon_method = "text"  # Keep current icons initially
   ```

2. **Test SVG generation**:
   ```python
   svg_icon_method = "svg_static"  # Try static SVG icons
   ```

3. **Enable full features**:
   ```python
   svg_icon_method = "svg_dynamic"  # Full dynamic system
   ```

## Best Practices

### Icon Design
- Use vector graphics for scalability
- Keep designs simple for small sizes
- Ensure good contrast with theme colors
- Test on different DPI settings

### Performance
- Use appropriate update intervals
- Cache static icons when possible
- Monitor resource usage in system monitor

### Maintenance
- Regularly update icon cache when themes change
- Test icons after qtile updates
- Keep backup of working configuration

## Advanced Features

### Custom Icon Builders

```python
def create_temperature_icon(temp_celsius: float) -> str:
    builder = SVGBuilder(24, 24)
    
    # Thermometer bulb
    builder.add_circle(12, 20, 3, fill="#ff0000")
    
    # Thermometer tube
    builder.add_rect(11, 4, 2, 16, fill="#ffffff", stroke="#000000")
    
    # Temperature indicator
    fill_height = min(16, (temp_celsius / 100) * 16)
    fill_color = "#ff0000" if temp_celsius > 80 else "#00ff00"
    builder.add_rect(11, 20 - fill_height, 2, fill_height, fill=fill_color)
    
    return builder.build()
```

### Theme Integration

```python
def update_icons_on_theme_change():
    """Call this when color theme changes"""
    from modules.bar_factory import update_bar_manager_icons
    
    # Get current bar manager
    bar_manager = get_current_bar_manager()
    
    # Update all dynamic icons
    update_bar_manager_icons(bar_manager)
```

This system provides a powerful, flexible way to create beautiful, theme-aware icons that enhance your qtile experience while maintaining excellent performance and compatibility.