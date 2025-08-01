#!/usr/bin/env python3
"""
Hooks module for qtile
Handles qtile hooks and event management
"""

import subprocess
from libqtile import hook
from libqtile.log_utils import logger
from qtile_config import get_config


class HookManager:
    """Manages qtile hooks and events"""

    def __init__(self, color_manager):
        self.color_manager = color_manager
        self.config = get_config()

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

        @hook.subscribe.startup_complete
        def enforce_tiling_on_restart():
            """Force all windows to tile after qtile restart (except explicitly floating ones)"""
            from libqtile import qtile

            def retile_windows():
                if qtile:
                    try:
                        retiled_count = 0
                        # Force all windows to tile unless they should be floating
                        for window in qtile.windows_map.values():
                            if hasattr(window, 'window') and hasattr(window, 'floating'):
                                try:
                                    # Check if this window should be floating based on our rules
                                    should_float = self._should_window_float(window)

                                    if not should_float and window.floating:
                                        window.floating = False  # Force to tile
                                        retiled_count += 1
                                        try:
                                            wm_class = window.window.get_wm_class()
                                            app_name = wm_class[1] if wm_class and len(
                                                wm_class) >= 2 else "Unknown"
                                            logger.info(
                                                f"Re-tiled window after restart: {app_name}")
                                        except BaseException:
                                            logger.info("Re-tiled unnamed window after restart")

                                except (IndexError, AttributeError, TypeError) as e:
                                    logger.debug(f"Could not check window during retiling: {e}")
                                    continue
                        logger.info(
                            f"Completed window retiling after startup - retiled {retiled_count} windows")
                    except Exception as e:
                        logger.error(f"Error during window retiling: {e}")

            # Schedule retiling with a small delay to ensure all windows are restored
            qtile.call_later(1.0, retile_windows)

    def _setup_client_hooks(self):
        """Setup client/window-related hooks"""
        @hook.subscribe.client_new
        def enforce_tiling_behavior(window):
            """Enforce consistent tiling behavior for all windows"""
            try:
                # Determine if this window should float based on our rules
                should_float = self._should_window_float(window)

                if not should_float:
                    # Force this window to tile
                    window.floating = False
                    try:
                        wm_class = window.window.get_wm_class()
                        app_name = wm_class[1] if wm_class and len(
                            wm_class) >= 2 else wm_class[0] if wm_class else "Unknown"
                        logger.debug(f"Enforced tiling for: {app_name}")
                    except BaseException:
                        logger.debug("Enforced tiling for unnamed window")
                else:
                    # This window should float
                    window.floating = True
                    try:
                        wm_class = window.window.get_wm_class()
                        app_name = wm_class[1] if wm_class and len(
                            wm_class) >= 2 else wm_class[0] if wm_class else "Unknown"
                        logger.debug(f"Allowed floating for: {app_name}")
                    except BaseException:
                        logger.debug("Allowed floating for unnamed window")

            except (IndexError, AttributeError, TypeError) as e:
                logger.debug(f"Could not determine window floating behavior: {e}")
                pass

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
            try:
                wm_class = window.window.get_wm_class()
                if wm_class and len(wm_class) > 0:
                    if wm_class[0].lower() in [fc.lower()
                                               for fc in self.config.force_floating_apps]:
                        window.floating = True
                        logger.debug(f"Set {wm_class[0]} to floating via hook")
            except (IndexError, AttributeError, TypeError) as e:
                logger.debug(f"Could not check window class for floating: {e}")
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
            time.sleep(self.config.screen_settings['detection_delay'])

            startup_time = getattr(self.color_manager, '_startup_time', time.time())
            current_time = time.time()

            # Only handle screen changes after qtile has been running for a while
            if current_time - startup_time > self.config.screen_settings['startup_delay']:
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
        autostart_script = self.config.autostart_script

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

    def _should_window_float(self, window):
        """Determine if a window should be floating based on our floating rules"""
        try:
            wm_class = window.window.get_wm_class()
            if wm_class and len(wm_class) > 0:
                # Check against force floating apps
                if wm_class[0].lower() in [fc.lower() for fc in self.config.force_floating_apps]:
                    return True

                # Check against floating rules (from qtile_config.py)
                for rule in self.config.floating_rules:
                    if 'wm_class' in rule:
                        if wm_class[0].lower() == rule['wm_class'].lower():
                            return True
                        if len(wm_class) >= 2 and wm_class[1].lower() == rule['wm_class'].lower():
                            return True

                    if 'title' in rule:
                        try:
                            window_title = window.window.get_name() or ""
                            if rule['title'].lower() in window_title.lower():
                                return True
                        except BaseException:
                            pass

            # Check if it's a transient window
            if window.window.get_wm_transient_for():
                return True

            # Check WM hints for max_width (dialog-like windows)
            hints = window.window.get_wm_normal_hints()
            if hints and hints.get("max_width") and hints.get("max_width") < 1000:
                # Only consider it floating if max_width is small (dialog-like)
                return True

            return False

        except (IndexError, AttributeError, TypeError) as e:
            logger.debug(f"Could not determine if window should float: {e}")
            return False  # Default to tiling if we can't determine

    def force_retile_all_windows(self, qtile):
        """Manual command to force all windows to tile (useful for testing/debugging)"""
        try:
            retiled_count = 0
            for window in qtile.windows_map.values():
                if hasattr(window, 'window') and hasattr(window, 'floating'):
                    try:
                        should_float = self._should_window_float(window)

                        if not should_float and window.floating:
                            window.floating = False
                            retiled_count += 1
                            try:
                                wm_class = window.window.get_wm_class()
                                app_name = wm_class[1] if wm_class and len(
                                    wm_class) >= 2 else "Unknown"
                                logger.info(f"Manually re-tiled: {app_name}")
                            except BaseException:
                                logger.info("Manually re-tiled unnamed window")
                    except (IndexError, AttributeError, TypeError) as e:
                        logger.debug(f"Could not check window during manual retiling: {e}")
                        continue
            logger.info(f"Manual retiling complete - retiled {retiled_count} windows")
            return retiled_count
        except Exception as e:
            logger.error(f"Error during manual retiling: {e}")
            return 0


def create_hook_manager(color_manager):
    """Create and return a hook manager instance"""
    return HookManager(color_manager)
