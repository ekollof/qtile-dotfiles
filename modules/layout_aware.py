#!/usr/bin/env python3
"""
Layout-aware window management commands
"""

from libqtile.log_utils import logger


class LayoutAwareCommands:
    """Commands that adapt their behavior based on the current layout"""

    def __init__(self):
        pass

    @staticmethod
    def smart_grow(qtile):
        """Smart grow that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case 'monadtall' | 'monadwide':
                    # MonadTall/Wide: grow main window
                    qtile.current_group.layout.grow()
                case 'tile':
                    # Tile: increase ratio
                    qtile.current_group.layout.increase_ratio()
                case 'bsp':
                    # BSP: grow window
                    qtile.current_group.layout.grow_right()
                case 'matrix':
                    # Matrix: add column (horizontal growth)
                    qtile.current_group.layout.add()
                case _:
                    # Max and Floating layouts: no-op (but don't error)
                    pass
        except Exception as e:
            # Fallback for layouts that don't support the operation
            logger.debug(f"Smart grow not supported in {layout_name}: {e}")

    @staticmethod
    def smart_shrink(qtile):
        """Smart shrink that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case 'monadtall' | 'monadwide':
                    # MonadTall/Wide: shrink main window
                    qtile.current_group.layout.shrink()
                case 'tile':
                    # Tile: decrease ratio
                    qtile.current_group.layout.decrease_ratio()
                case 'bsp':
                    # BSP: shrink window
                    qtile.current_group.layout.grow_left()
                case 'matrix':
                    # Matrix: remove column (horizontal shrink)
                    qtile.current_group.layout.delete()
                case _:
                    # Max and Floating layouts: no-op
                    pass
        except Exception as e:
            # Fallback for layouts that don't support the operation
            logger.debug(f"Smart shrink not supported in {layout_name}: {e}")

    @staticmethod
    def smart_grow_vertical(qtile):
        """Smart vertical grow that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case 'monadtall' | 'monadwide':
                    # MonadTall/Wide: grow main window
                    qtile.current_group.layout.grow()
                case 'tile':
                    # Tile: no vertical resize in tile layout
                    pass
                case 'bsp':
                    # BSP: grow window up
                    qtile.current_group.layout.grow_up()
                case 'matrix':
                    # Matrix: no vertical resize (columns only)
                    pass
                case _:
                    # Max and Floating layouts: no-op
                    pass
        except Exception as e:
            logger.debug(f"Smart vertical grow not supported in {layout_name}: {e}")

    @staticmethod
    def smart_shrink_vertical(qtile):
        """Smart vertical shrink that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case 'monadtall' | 'monadwide':
                    # MonadTall/Wide: shrink main window
                    qtile.current_group.layout.shrink()
                case 'tile':
                    # Tile: no vertical resize in tile layout
                    pass
                case 'bsp':
                    # BSP: grow window down (shrink upward space)
                    qtile.current_group.layout.grow_down()
                case 'matrix':
                    # Matrix: no vertical resize (columns only)
                    pass
                case _:
                    # Max and Floating layouts: no-op
                    pass
        except Exception as e:
            logger.debug(f"Smart vertical shrink not supported in {layout_name}: {e}")

    @staticmethod
    def smart_normalize(qtile):
        """Smart normalize that works with different layouts"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case 'monadtall' | 'monadwide' | 'monadthreecol':
                    # Monad layouts: normalize secondary windows
                    qtile.current_group.layout.normalize()
                case 'tile':
                    # Tile: reset to default ratios
                    qtile.current_group.layout.reset()
                case 'bsp':
                    # BSP: normalize window sizes
                    qtile.current_group.layout.normalize()
                case 'columns':
                    # Columns: normalize column widths and reset ratios
                    qtile.current_group.layout.normalize()
                case 'spiral':
                    # Spiral: reset ratios to config values
                    qtile.current_group.layout.reset()
                case 'verticaltile':
                    # VerticalTile: normalize window sizes
                    qtile.current_group.layout.normalize()
                case 'plasma':
                    # Plasma: reset current window size to automatic
                    qtile.current_group.layout.reset_size()
                case 'matrix':
                    # Matrix: no normalize function, but we can do nothing gracefully
                    pass
                case 'max' | 'floating':
                    # Max/Floating: no normalize needed
                    pass
                case _ if hasattr(qtile.current_group.layout, 'normalize'):
                    # Generic normalize fallback
                    qtile.current_group.layout.normalize()
                case _ if hasattr(qtile.current_group.layout, 'reset'):
                    # Generic reset fallback
                    qtile.current_group.layout.reset()
        except Exception as e:
            logger.debug(f"Normalize not supported in {layout_name}: {e}")

    @staticmethod
    def layout_safe_command(qtile, command_name, *args, **kwargs):
        """Execute a layout command only if the layout supports it"""
        try:
            layout = qtile.current_group.layout
            if hasattr(layout, command_name):
                command = getattr(layout, command_name)
                if callable(command):
                    return command(*args, **kwargs)
        except Exception as e:
            logger.debug(f"Layout command {command_name} failed: {e}")

    @staticmethod
    def get_layout_info(qtile):
        """Get information about the current layout"""
        layout = qtile.current_group.layout
        return {
            'name': layout.name,
            'supports_grow': hasattr(layout, 'grow'),
            'supports_shrink': hasattr(layout, 'shrink'),
            'supports_normalize': hasattr(layout, 'normalize'),
            'supports_reset': hasattr(layout, 'reset'),
            'supports_flip': hasattr(layout, 'flip'),
            # Note: maximize is now handled via lazy.window.toggle_maximize() which works with all layouts
        }

    @staticmethod
    def smart_flip(qtile):
        """Smart flip that works with layouts that support it"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case 'monadtall' | 'monadwide' | 'bsp':
                    qtile.current_group.layout.flip()
                case 'tile':
                    # Tile doesn't have flip, but we can swap main/secondary
                    if hasattr(qtile.current_group.layout, 'swap_main'):
                        qtile.current_group.layout.swap_main()
        except Exception as e:
            logger.debug(f"Smart flip not supported in {layout_name}: {e}")
