#!/usr/bin/env python3
"""
Screen hooks for qtile
"""

import time
import traceback
from libqtile import hook, qtile
from libqtile.log_utils import logger


class ScreenHooks:
    """Handles screen-related hooks and monitor changes"""
    
    def __init__(self, config, color_manager):
        self.config = config
        self.color_manager = color_manager

    def setup_screen_hooks(self):
        """Setup all screen-related hooks"""
        logger.debug("Setting up screen hooks")
        
        @hook.subscribe.screen_change
        def handle_screen_change(*args, **kwargs):
            """Handle screen configuration changes (monitor hotplug/unplug)"""
            # Some qtile versions don't pass event parameter
            event = args[0] if args else None
            self._handle_screen_change_event(event)

        @hook.subscribe.current_screen_change
        def handle_current_screen_change(*args, **kwargs):
            """Handle changes to the current screen focus"""
            # Some qtile versions don't pass event parameter
            event = args[0] if args else None
            self._handle_current_screen_change_event(event)

    def _handle_screen_change_event(self, event=None):
        """Handle screen configuration changes with proper timing and validation"""
        # Add minimal delay to let the system settle
        time.sleep(self.config.screen_settings['detection_delay'])

        startup_time = getattr(self.color_manager, '_startup_time', time.time())
        current_time = time.time()

        # Only handle screen changes after qtile has been running for a while
        if current_time - startup_time > self.config.screen_settings['startup_delay']:
            logger.info("Screen change detected - checking for monitor changes")
            if event is not None:
                logger.debug(f"Screen change event data: {event}")

            try:
                # Check if screen count actually changed
                if self._refresh_and_check_screens():
                    logger.info("Monitor configuration changed - updating screens")
                    self._reconfigure_screens()
                else:
                    logger.info("Screen change detected but count unchanged")
            except Exception as e:
                logger.error(f"Error handling screen change: {e}")
                logger.error(traceback.format_exc())
        else:
            logger.info("Screen change detected but ignored (too soon after startup)")

    def _handle_current_screen_change_event(self, event=None):
        """Handle changes to current screen focus"""
        try:
            if qtile and qtile.current_screen:
                screen_index = qtile.screens.index(qtile.current_screen)
                logger.debug(f"Current screen changed to: {screen_index}")
                if event is not None:
                    logger.debug(f"Screen change event data: {event}")
        except Exception as e:
            logger.debug(f"Error handling current screen change: {e}")

    def _refresh_and_check_screens(self) -> bool:
        """Refresh screen detection and check if configuration changed"""
        try:
            from modules.screens import refresh_screens
            return refresh_screens()
        except Exception as e:
            logger.error(f"Error refreshing screens: {e}")
            return False

    def _reconfigure_screens(self):
        """Reconfigure screens with new monitor setup"""
        try:
            # Get qtile instance
            if qtile is not None:
                from modules.screens import get_screen_count
                from modules.bars import create_bar_manager
                
                # Force screen reconfiguration
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
                logger.warning("Could not get qtile instance for screen reconfiguration")
        except Exception as e:
            logger.error(f"Error reconfiguring screens: {e}")
            logger.error(traceback.format_exc())

    def get_screen_status(self) -> dict:
        """Get current screen configuration status"""
        try:
            from modules.screens import get_screen_count
            
            status = {
                'screen_count': get_screen_count(),
                'detection_delay': self.config.screen_settings['detection_delay'],
                'startup_delay': self.config.screen_settings['startup_delay'],
                'qtile_screens': len(qtile.screens) if qtile else 0,
                'current_screen': qtile.screens.index(qtile.current_screen) if qtile and qtile.current_screen else None,
            }
            
            if qtile:
                status['screen_details'] = [
                    {
                        'index': i,
                        'width': screen.width,
                        'height': screen.height,
                        'x': screen.x,
                        'y': screen.y,
                        'group': screen.group.name if screen.group else None
                    }
                    for i, screen in enumerate(qtile.screens)
                ]
            
            return status
        except Exception as e:
            logger.error(f"Error getting screen status: {e}")
            return {'error': str(e)}

    def validate_screen_configuration(self) -> dict:
        """Validate the screen configuration settings"""
        validation = {
            'valid': True,
            'warnings': [],
            'errors': []
        }

        try:
            # Check detection delay
            delay = self.config.screen_settings['detection_delay']
            if not isinstance(delay, (int, float)) or delay < 0:
                validation['errors'].append("Detection delay must be a non-negative number")
                validation['valid'] = False
            elif delay > 5:
                validation['warnings'].append("Detection delay is quite high (>5 seconds)")

            # Check startup delay
            startup_delay = self.config.screen_settings['startup_delay']
            if not isinstance(startup_delay, (int, float)) or startup_delay < 0:
                validation['errors'].append("Startup delay must be a non-negative number")
                validation['valid'] = False
            elif startup_delay > 60:
                validation['warnings'].append("Startup delay is quite high (>60 seconds)")

        except (AttributeError, KeyError, TypeError) as e:
            validation['errors'].append(f"Missing or invalid screen settings: {e}")
            validation['valid'] = False

        return validation

    def force_screen_refresh(self):
        """Manually force a screen refresh (for testing/debugging)"""
        logger.info("Forcing screen refresh")
        try:
            if self._refresh_and_check_screens():
                logger.info("Screen configuration changed during manual refresh")
                self._reconfigure_screens()
            else:
                logger.info("No screen configuration change detected during manual refresh")
        except Exception as e:
            logger.error(f"Error during forced screen refresh: {e}")

    def get_screen_change_history(self) -> list:
        """Get history of screen changes (placeholder for future implementation)"""
        # This could be implemented to track screen change events over time
        # Useful for debugging monitor hotplug issues
        return []

    def _count_registered_hooks(self) -> dict:
        """Count registered screen hooks"""
        return {
            'screen_change': 1,  # handle_screen_change
            'current_screen_change': 1  # handle_current_screen_change
        }
