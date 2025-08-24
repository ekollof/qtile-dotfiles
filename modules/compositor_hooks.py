#!/usr/bin/env python3
"""
Compositor hooks for qtile
Handles simple compositor startup and management
"""

from libqtile import hook
from libqtile.log_utils import logger

from .simple_popup_notifications import show_popup_notification


class CompositorHooks:
    """Handles compositor-related hooks and lifecycle management"""

    def __init__(self, config: object) -> None:
        self.config = config

    def setup_compositor_hooks(self) -> None:
        """Setup all compositor-related hooks"""
        logger.debug("Setting up compositor hooks")

        @hook.subscribe.startup_complete
        def start_compositor_on_startup():  # Used by qtile hook system
            """Start the compositor when qtile is fully loaded"""
            self._start_compositor()

        @hook.subscribe.shutdown
        def stop_compositor_on_shutdown():  # Used by qtile hook system
            """Stop the compositor when qtile shuts down"""
            self._stop_compositor()

    def _start_compositor(self) -> None:
        """Start the simple compositor if enabled in configuration"""
        try:
            # Import compositor here to avoid circular imports
            from .simple_compositor import start_compositor, is_compositor_running
            
            # Check if compositor is already running
            if is_compositor_running():
                logger.info("Compositor already running")
                return
                
            # Start the compositor
            if start_compositor(self.config):
                logger.info("✅ Simple compositor started successfully")
                try:
                    show_popup_notification(
                        "Compositor", "Simple compositor started", "normal"
                    )
                except Exception:
                    pass  # Don't fail startup if notification fails
            else:
                logger.info("ℹ️ Compositor disabled or failed to start")
                
        except Exception as e:
            logger.warning(f"❌ Failed to start compositor: {e}")

    def _stop_compositor(self) -> None:
        """Stop the compositor gracefully"""
        try:
            from .simple_compositor import stop_compositor, is_compositor_running
            
            if is_compositor_running():
                stop_compositor()
                logger.info("✅ Compositor stopped successfully")
            else:
                logger.debug("Compositor was not running")
                
        except Exception as e:
            logger.warning(f"❌ Failed to stop compositor: {e}")

    def toggle_compositor(self) -> bool:
        """
        Toggle compositor on/off
        @return True if now running, False if stopped
        """
        try:
            from .simple_compositor import toggle_compositor
            
            result = toggle_compositor(self.config)
            status = "started" if result else "stopped"
            logger.info(f"Compositor {status}")
            
            try:
                show_popup_notification(
                    "Compositor", f"Compositor {status}", "normal"
                )
            except Exception:
                pass
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to toggle compositor: {e}")
            return False

    def reload_compositor_config(self) -> None:
        """Reload compositor configuration"""
        try:
            from .simple_compositor import reload_compositor_config, is_compositor_running
            
            if is_compositor_running():
                reload_compositor_config(self.config)
                logger.info("✅ Compositor configuration reloaded")
                
                try:
                    show_popup_notification(
                        "Compositor", "Configuration reloaded", "normal"
                    )
                except Exception:
                    pass
            else:
                logger.info("Compositor not running, cannot reload configuration")
                
        except Exception as e:
            logger.error(f"Failed to reload compositor configuration: {e}")

    def get_compositor_status(self) -> dict[str, object]:
        """Get compositor status information"""
        try:
            from .simple_compositor import is_compositor_running
            
            running = is_compositor_running()
            enabled = False
            
            if hasattr(self.config, 'compositor_settings'):
                settings = getattr(self.config, 'compositor_settings')
                enabled = settings.get('enabled', False) if settings else False
            
            return {
                "running": running,
                "enabled": enabled,
                "status": "running" if running else ("enabled but not running" if enabled else "disabled")
            }
            
        except Exception as e:
            logger.error(f"Failed to get compositor status: {e}")
            return {
                "running": False,
                "enabled": False,
                "status": f"error: {e}"
            }