# Qtile Notification System

This document describes the libnotify-compatible notification system integrated into your qtile configuration.

## Overview

Your qtile configuration now includes a comprehensive notification system that provides:

- **Built-in notification server** - Qtile acts as a libnotify-compatible notification daemon
- **Status bar integration** - Notifications appear in your status bar
- **D-Bus compatibility** - Works with standard Linux notification tools like `notify-send`
- **Cross-platform support** - Compatible with Linux and BSD systems
- **Configurable behavior** - Timeout, urgency levels, and appearance can be customized

## Features

### ✅ What's Enabled

1. **Notification Widget** - Added to your status bar automatically
2. **Libnotify Compatibility** - `notify-send` commands will work
3. **Built-in Test Functions** - Key bindings to test the system
4. **Startup Notifications** - System events are announced
5. **Theme Integration** - Notifications match your color scheme

### 🎛️ Configuration

Notification settings are configured in `qtile_config.py`:

```python
@property
def notification_settings(self) -> dict[str, Any]:
    return {
        "enabled": True,                    # Enable notification system
        "default_timeout": 5000,           # Default timeout (5 seconds)
        "default_timeout_low": 3000,       # Low priority timeout
        "default_timeout_urgent": 0,       # Urgent notifications never timeout
        "enable_sound": False,             # Disable notification sounds
        "show_in_bar": True,              # Show notifications in status bar
        "max_notification_length": 100,   # Maximum text length
        "enable_actions": True,           # Enable notification buttons
        "libnotify_compatible": True,     # Enable D-Bus compatibility
    }
```

## Key Bindings

The following key bindings are available for testing notifications:

| Key Combination | Function | Description |
|----------------|----------|-------------|
| `Super + Ctrl + N` | Test Notification | Send a test notification |
| `Super + Ctrl + Shift + N` | Test Urgent | Send an urgent notification |
| `Super + Ctrl + Alt + N` | Status Check | Show notification system status |

## Usage Examples

### Command Line Usage

Once the system is running, you can send notifications from the command line:

```bash
# Basic notification
notify-send "Hello" "This is a test notification"

# Notification with timeout (in milliseconds)
notify-send -t 5000 "Title" "This notification lasts 5 seconds"

# Urgent notification
notify-send -u critical "Important" "This is urgent!"

# Notification with icon
notify-send -i dialog-information "Info" "This has an icon"
```

### Programmatic Usage

From within qtile or Python scripts:

```python
from modules.notifications import send_qtile_notification

# Simple notification
send_qtile_notification("Title", "Message")

# Notification with options
send_qtile_notification(
    "Important Update",
    "Your system has been updated",
    timeout=8000,
    urgency="normal"
)
```

### From Qtile Hooks

You can send notifications from qtile hooks:

```python
from libqtile import hook
from modules.notifications import notify_qtile_event

@hook.subscribe.client_new
def notify_new_window(client):
    notify_qtile_event("window_opened", f"New window: {client.name}")
```

## Testing the System

### 1. Test Script

Run the comprehensive test script:

```bash
cd ~/.config/qtile
python test_notifications.py
```

This will test all notification methods and provide detailed feedback.

### 2. Manual Testing

Test using the key bindings:
1. Press `Super + Ctrl + N` to send a test notification
2. Press `Super + Ctrl + Shift + N` for an urgent notification
3. Press `Super + Ctrl + Alt + N` to check system status

### 3. Command Line Testing

```bash
# Test basic functionality
notify-send "Test" "Hello from the command line"

# Test different urgency levels
notify-send -u low "Low" "Low priority message"
notify-send -u normal "Normal" "Normal priority message"
notify-send -u critical "Critical" "Critical priority message"
```

## Notification Behavior

### Urgency Levels

- **Low**: Short timeout (3 seconds), muted colors
- **Normal**: Standard timeout (5 seconds), normal colors
- **Critical**: No timeout (stays until dismissed), bright colors

### Display Location

- Notifications appear in the status bar as part of the Notify widget
- The widget shows the most recent notification
- Multiple notifications are queued and displayed in sequence

### Theming

Notifications automatically use your current color scheme:
- Background matches your bar background
- Text color adapts to your theme
- Urgent notifications use accent colors

## Troubleshooting

### No Notifications Appearing

1. **Check if enabled in config**:
   ```python
   # In qtile_config.py, ensure:
   "enabled": True,
   "show_in_bar": True,
   ```

2. **Verify widget is in bar**:
   - Look for a notification area in your status bar
   - Check qtile logs for widget creation errors

3. **Test with key bindings**:
   - Press `Super + Ctrl + N` for a test notification
   - Check qtile logs for error messages

### notify-send Not Working

1. **Install libnotify**:
   ```bash
   # Arch/Manjaro
   sudo pacman -S libnotify
   
   # Ubuntu/Debian
   sudo apt install libnotify-bin
   
   # Fedora
   sudo dnf install libnotify
   
   # FreeBSD
   pkg install libnotify
   ```

2. **Check D-Bus**:
   ```bash
   # Verify D-Bus is running
   systemctl --user status dbus
   
   # Test D-Bus notification service
   dbus-send --print-reply --dest=org.freedesktop.Notifications \
     /org/freedesktop/Notifications \
     org.freedesktop.Notifications.GetCapabilities
   ```

### Notifications Not Themed Correctly

1. **Restart qtile** after configuration changes
2. **Check color manager** is working properly
3. **Manual color reload**: Press `Super + Ctrl + C`

### Performance Issues

If notifications cause performance problems:

1. **Reduce timeout values** in configuration
2. **Disable sound** if enabled
3. **Limit notification length**:
   ```python
   "max_notification_length": 50,  # Shorter messages
   ```

## Log Information

Check qtile logs for notification-related messages:

```bash
# View qtile logs
journalctl --user -u qtile

# Or check the log file directly
tail -f ~/.local/share/qtile/qtile.log
```

Look for messages containing:
- "notification"
- "Notify widget"
- "libnotify"

## Integration with Other Applications

### Email Notifications
```bash
# Example: New email notification
notify-send -i mail-unread "New Email" "You have 3 new messages"
```

### System Monitoring
```bash
# Example: Low battery warning
notify-send -u critical -i battery-low "Low Battery" "Battery at 15%"
```

### Build Systems
```bash
# Example: Build completion
notify-send -i dialog-information "Build Complete" "Project built successfully"
```

## Advanced Configuration

### Custom Notification Function

Create custom notification functions in your config:

```python
def notify_workspace_change(qtile):
    """Notify when workspace changes"""
    current_group = qtile.current_group.name
    send_qtile_notification("Workspace", f"Switched to {current_group}")
```

### Hook Integration

Add notifications to qtile hooks:

```python
@hook.subscribe.startup_complete
def startup_notification():
    send_qtile_notification("Qtile", "Startup complete!")

@hook.subscribe.screen_change
def screen_change_notification(event):
    send_qtile_notification("Display", f"Screen configuration changed")
```

## Files Modified

The notification system was implemented by modifying/creating:

- `modules/notifications.py` - Main notification module
- `modules/bars.py` - Added notification widget to status bar
- `modules/system_commands.py` - Added test functions
- `modules/key_bindings.py` - Added key bindings
- `modules/startup_hooks.py` - Added startup notification
- `qtile_config.py` - Added notification settings
- `test_notifications.py` - Test script

## Support

If you encounter issues:

1. Run the test script: `python test_notifications.py`
2. Check qtile logs for error messages
3. Verify dependencies are installed
4. Test with manual key bindings
5. Check D-Bus service availability

The notification system is designed to degrade gracefully - if one method fails, it will try alternatives automatically.