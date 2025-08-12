#!/usr/bin/env python3
"""
@brief Main hook manager class - orchestrates all hook management functionality
@file hook_manager.py

Orchestrates all hook management functionality for qtile configuration.
Provides centralized management of startup, client, and screen hooks.

@author Qtile configuration system
@note This module follows Python 3.10+ standards and project guidelines
"""

from typing import Any
from libqtile.log_utils import logger
from qtile_config import get_config

from .startup_hooks import StartupHooks
from .client_hooks import ClientHooks
from .screen_hooks import ScreenHooks
from .window_manager import WindowManager

class HookManager:
    """
    @brief Manages qtile hooks and events

    Orchestrates all hook management functionality including startup hooks,
    client hooks, screen hooks, and window management. Provides centralized
    control and validation for qtile's event handling system.
    """

    def __init__(self, color_manager):
        self.color_manager = color_manager
        self.config = get_config()

        # Initialize component modules
        self.window_manager = WindowManager(self.config)
        self.startup_hooks = StartupHooks(self.config, color_manager, self.window_manager)
        self.client_hooks = ClientHooks(self.config, self.window_manager)
        self.screen_hooks = ScreenHooks(self.config, color_manager)

    def setup_hooks(self) -> None:
        """
        @brief Setup all qtile hooks
        @throws Exception if hook setup fails
        """
        logger.info("Setting up qtile hooks")
        self.startup_hooks.setup_startup_hooks()
        self.client_hooks.setup_client_hooks()
        self.screen_hooks.setup_screen_hooks()
        logger.info("All qtile hooks configured successfully")

    def force_retile_all_windows(self, qtile) -> int:
        """
        @brief Manual command to force all windows to tile (useful for testing/debugging)
        @param qtile Qtile instance
        @return Number of windows retiled
        """
        return self.window_manager.force_retile_all_windows(qtile)

    def get_hook_status(self) -> dict[str, Any]:
        """
        @brief Get comprehensive status of all hook components
        @return Dictionary containing status of startup, client, screen, and window manager hooks
        """
        status = {
            'startup': self.startup_hooks.get_startup_status(),
            'client': self.client_hooks.get_client_statistics(),
            'screen': self.screen_hooks.get_screen_status(),
            'window_manager': self.get_window_manager_status(),
        }
        return status

    def get_window_manager_status(self) -> dict[str, Any]:
        """
        @brief Get window manager status and statistics
        @return Dictionary containing window manager status and statistics
        """
        try:
            from libqtile import qtile
            if qtile:
                return {
                    'statistics': self.window_manager.get_window_statistics(qtile),
                    'floating_windows': self.window_manager.list_floating_windows(qtile),
                    'problematic_windows': self.window_manager.get_problematic_windows(qtile),
                    'floating_rules_validation': self.window_manager.validate_floating_rules(),
                }
            else:
                return {'error': 'Qtile instance not available'}
        except Exception as e:
            logger.error(f"Error getting window manager status: {e}")
            return {'error': str(e)}

    def validate_configuration(self) -> dict[str, Any]:
        """Validate the entire hook configuration"""
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'component_validations': {}
        }

        # Validate each component
        components = {
            'startup': self.startup_hooks.validate_autostart_script(),
            'screen': self.screen_hooks.validate_screen_configuration(),
            'window_manager': self.window_manager.validate_floating_rules(),
        }

        for component_name, component_validation in components.items():
            validation['component_validations'][component_name] = component_validation

            if not component_validation.get('valid', True):
                validation['valid'] = False

            validation['warnings'].extend(component_validation.get('warnings', []))
            validation['errors'].extend(component_validation.get('errors', []))

        return validation

    def get_comprehensive_diagnostics(self) -> dict[str, Any]:
        """Get comprehensive diagnostics for troubleshooting"""
        try:
            from libqtile import qtile

            diagnostics = {
                'hook_status': self.get_hook_status(),
                'configuration_validation': self.validate_configuration(),
                'qtile_available': qtile is not None,
            }

            if qtile:
                diagnostics.update({
                    'qtile_version': getattr(qtile, 'version', 'unknown'),
                    'screen_count': len(qtile.screens),
                    'group_count': len(qtile.groups),
                    'total_windows': len(qtile.windows_map),
                })

            return diagnostics
        except Exception as e:
            logger.error(f"Error generating diagnostics: {e}")
            return {'error': str(e)}

    def emergency_reset(self) -> dict[str, Any]:
        """Emergency reset of window states"""
        try:
            from libqtile import qtile
            if qtile:
                logger.warning("Performing emergency hook manager reset")

                # Force retile all windows
                retiled = self.force_retile_all_windows(qtile)
                logger.info(f"Emergency reset: retiled {retiled} windows")

                # Reset any problematic window states
                problematic = self.window_manager.get_problematic_windows(qtile)
                for window_info in problematic:
                    logger.info(f"Found problematic window: {window_info['name']} - {window_info['issues']}")

                return {
                    'retiled_windows': retiled,
                    'problematic_windows': len(problematic),
                    'success': True
                }
            else:
                return {'error': 'Qtile instance not available', 'success': False}
        except Exception as e:
            logger.error(f"Error during emergency reset: {e}")
            return {'error': str(e), 'success': False}

    def reload_configuration(self):
        """Reload hook configuration (placeholder for future implementation)"""
        # This could be used to reload configuration without restarting qtile
        logger.info("Hook configuration reload requested")
        # Implementation would involve:
        # 1. Unsubscribing existing hooks
        # 2. Reloading config
        # 3. Re-setting up hooks
        pass

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for hook operations"""
        # This could track timing and frequency of hook operations
        return {
            'startup_time': getattr(self.color_manager, '_startup_time', 0),
            'hooks_configured': True,
            'window_operations': 'Available',
            'screen_monitoring': 'Active' if self.color_manager.is_monitoring() else 'Inactive'
        }

    # Backward compatibility methods
    def autostart(self):
        """Run autostart script (backward compatibility)"""
        return self.startup_hooks.run_autostart_script()

    def _should_window_float(self, window):
        """Determine if window should float (backward compatibility)"""
        return self.window_manager.should_window_float(window)

def create_hook_manager(color_manager) -> HookManager:
    """
    @brief Create and return a hook manager instance
    @param color_manager Color manager instance for hook configuration
    @return Configured HookManager instance
    """
    return HookManager(color_manager)
