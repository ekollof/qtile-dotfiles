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

from .client_hooks import ClientHooks
from .lifecycle_hooks import LifecycleHooks
from .window_manager import WindowManager


class HookManager:
    """
    @brief Manages qtile hooks and events

    Orchestrates all hook management functionality including startup hooks,
    client hooks, screen hooks, and window management. Provides centralized
    control and validation for qtile's event handling system.
    """

    def __init__(self, color_manager: Any) -> None:
        self.color_manager = color_manager
        self.config = get_config()

        # Initialize component modules
        self.window_manager = WindowManager(self.config)
        self.lifecycle_hooks = LifecycleHooks(
            self.config, color_manager, self.window_manager
        )
        self.client_hooks = ClientHooks(self.config, self.window_manager)

        # Maintain backward compatibility
        self.startup_hooks = self.lifecycle_hooks
        self.screen_hooks = self.lifecycle_hooks

    def setup_hooks(self) -> None:
        """
        @brief Setup all qtile hooks
        @throws Exception if hook setup fails
        """
        logger.info("Setting up qtile hooks")
        self.lifecycle_hooks.setup_all_hooks()
        self.client_hooks.setup_client_hooks()
        logger.info("All qtile hooks configured successfully")

    def force_retile_all_windows(self, qtile: Any) -> int:
        """
        @brief Manual command to force all windows to tile
        (useful for testing/debugging)
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
            "lifecycle": self.lifecycle_hooks.get_lifecycle_status(),
            "client": self.client_hooks.get_client_statistics(),
            "window_manager": self.get_window_manager_status(),
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
                    "statistics": self.window_manager.get_window_statistics(qtile),
                    "floating_windows": self.window_manager.list_floating_windows(
                        qtile
                    ),
                    "problematic_windows": self.window_manager.get_problematic_windows(
                        qtile
                    ),
                    "floating_rules_validation": self.window_manager.validate_floating_rules(),
                }
            else:
                return {"error": "Qtile instance not available"}
        except Exception as e:
            logger.error(f"Error getting window manager status: {e}")
            return {"error": str(e)}

    def validate_configuration(self) -> dict[str, Any]:
        """Validate the entire hook configuration"""
        validation: dict[str, Any] = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "component_validations": {},
        }

        # Validate each component
        components = {
            "lifecycle": {
                "autostart": self.lifecycle_hooks.validate_autostart_script(),
                "screen": self.lifecycle_hooks.validate_screen_configuration(),
                "valid": True,
            },
            "window_manager": self.window_manager.validate_floating_rules(),
        }

        for component_name, component_validation in components.items():
            validation["component_validations"][component_name] = component_validation

            if not component_validation.get("valid", True):
                validation["valid"] = False

            validation["warnings"].extend(component_validation.get("warnings", []))
            validation["errors"].extend(component_validation.get("errors", []))

        return validation

    # Backward compatibility methods
    def autostart(self) -> Any:
        """
        @brief Run autostart script (backward compatibility)
        @return Result from autostart execution
        """
        return self.lifecycle_hooks.run_autostart_script()

    def _should_window_float(self, window: Any) -> bool:
        """Determine if window should float (backward compatibility)"""
        return self.window_manager.should_window_float(window)


def create_hook_manager(color_manager: Any) -> HookManager:
    """
    @brief Create and return a hook manager instance
    @param color_manager Color manager instance for hook configuration
    @return Configured HookManager instance
    """
    return HookManager(color_manager)
