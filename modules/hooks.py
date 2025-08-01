#!/usr/bin/env python3
"""
Hooks module for qtile
Handles qtile hooks and event management
"""

import subprocess
from libqtile import hook
from libqtile.log_utils import logger


class HookManager:
    """Manages qtile hooks and events"""

    def __init__(self, color_manager):
        self.color_manager = color_manager

    def setup_hooks(self):
        """Setup all qtile hooks"""
        logger.info("Setting up qtile hooks")
        self._setup_startup_hooks()
        self._setup_client_hooks()
        self._setup_screen_hooks()

    def _setup_startup_hooks(self):
        """Setup startup-related hooks"""
        @hook.subscribe.startup_once
        def start_color_watcher():
            """Start the color file watcher when qtile starts"""
            logger.info("Qtile startup_once hook called")

        @hook.subscribe.startup_once
        def run_autostart():
            """Run autostart script when qtile starts"""
            self.autostart()

        @hook.subscribe.startup_complete
        def setup_color_watching():
            """Additional setup after qtile is fully loaded"""
            logger.info("Qtile startup completed - starting color monitoring")
            self.color_manager.start_monitoring()

    def _setup_client_hooks(self):
        """Setup client/window-related hooks"""
        @hook.subscribe.client_new
        def transient_window(window):
            """Handle wm hints"""
            hints = window.window.get_wm_normal_hints()
            if window.window.get_wm_transient_for():
                window.floating = True
            if hints and hints.get("max_width"):
                window.floating = True

        @hook.subscribe.client_new
        def set_floating(window):
            """Set specific windows to floating"""
            floating_classes = ("nm-connection-editor", "pavucontrol", "origin.exe")
            try:
                if window.window.get_wm_class()[0] in floating_classes:
                    window.floating = True
            except (IndexError, AttributeError):
                pass

        @hook.subscribe.client_new
        def set_parent(window):
            """Set parent for transient windows"""
            if window.window.get_wm_transient_for():
                parent = window.window.get_wm_transient_for()
                for client in window.qtile.windows_map.values():
                    if hasattr(client, "window") and client.window.wid == parent:
                        window.parent = client
                        return

        @hook.subscribe.client_new
        def swallow(window):
            """Swallow terminal windows"""
            # pid = window.window.get_net_wm_pid()
            # Add swallowing logic here if needed
            pass

        @hook.subscribe.client_killed
        def unswallow(window):
            """Unswallow terminal windows"""
            # Add unswallowing logic here if needed
            pass

    def _setup_screen_hooks(self):
        """Setup screen-related hooks"""
        @hook.subscribe.screen_change
        def handle_screen_change(event):
            """Handle screen configuration changes (monitor hotplug/unplug)"""
            import time
            from modules.screens import refresh_screens
            from modules.bars import create_bar_manager
            
            # Add minimal delay to let the system settle
            time.sleep(2)
            
            startup_time = getattr(self.color_manager, '_startup_time', time.time())
            current_time = time.time()
            
            # Only handle screen changes after qtile has been running for a while
            if current_time - startup_time > 30:
                logger.info("Screen change detected - checking for monitor changes")
                
                try:
                    # Check if screen count actually changed
                    if refresh_screens():
                        logger.info("Monitor configuration changed - updating screens")
                        
                        # Get qtile instance
                        from libqtile import qtile
                        if qtile is not None:
                            # Force screen reconfiguration
                            from modules.screens import get_screen_count
                            new_screen_count = get_screen_count()
                            
                            # Recreate screens with new configuration
                            bar_manager = create_bar_manager(self.color_manager)
                            new_screens = bar_manager.create_screens(new_screen_count)
                            
                            # Update qtile's screen configuration
                            qtile.config.screens = new_screens
                            
                            # Restart qtile to apply new screen configuration
                            logger.info(f"Restarting qtile with {new_screen_count} screens")
                            qtile.restart()
                        else:
                            logger.warning("Could not get qtile instance")
                    else:
                        logger.info("Screen change detected but count unchanged")
                except Exception as e:
                    logger.error(f"Error handling screen change: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            else:
                logger.info("Screen change detected but ignored (too soon after startup)")

    def autostart(self):
        """Run autostart script"""
        import os
        home = os.path.expanduser("~")
        autostart_script = os.path.join(home, ".config", "qtile", "autostart.sh")

        if os.path.exists(autostart_script) and os.access(autostart_script, os.X_OK):
            try:
                logger.info(f"Running autostart script: {autostart_script}")
                # Run completely detached - don't wait for completion
                subprocess.Popen([autostart_script],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               stdin=subprocess.DEVNULL,
                               start_new_session=True)
                logger.info("Autostart script launched successfully")
            except Exception as e:
                logger.error(f"Failed to launch autostart script: {e}")
        else:
            logger.error(f"Autostart script not found or not executable: {autostart_script}")


def create_hook_manager(color_manager):
    """Create and return a hook manager instance"""
    return HookManager(color_manager)
