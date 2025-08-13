#!/usr/bin/env python3
"""
@brief Client hooks for qtile window management
@file client_hooks.py

This module provides client/window event handling functionality for qtile,
including window focusing, floating rules, and client state management.
"""

from typing import Any

from libqtile import hook
from libqtile.log_utils import logger


class ClientHooks:
    """
    @brief Handles client/window-related hooks for qtile

    Manages window events, floating rules, focus tracking, and client
    state changes in the qtile window manager.
    """

    def __init__(self, config: Any, window_manager: Any) -> None:
        """
        @brief Initialize client hooks manager
        @param config Configuration object with floating rules and debug settings
        @param window_manager Window manager instance for window operations
        """
        super().__init__()
        self.config = config
        self.window_manager = window_manager
        self._enforce_tiling_behavior = None  # Will be set in setup_client_hooks

    def setup_client_hooks(self) -> None:
        """
        @brief Setup all client/window-related hooks
        """
        logger.debug("Setting up client hooks")

        @hook.subscribe.client_new # pyright: ignore[reportUnknownMemberType]
        def enforce_tiling_behavior(window: Any) -> None:
            """Enforce consistent tiling behavior for all windows"""
            self.window_manager.enforce_window_tiling(window)

        # Store reference to make function accessible
        self._enforce_tiling_behavior = enforce_tiling_behavior

        @hook.subscribe.client_new  # pyright: ignore[reportUnknownMemberType]
        def handle_transient_window(window: Any) -> None:  # pyright: ignore[reportUnusedFunction]
            """Handle WM hints for transient windows"""
            self.window_manager.handle_transient_window(window)

        @hook.subscribe.client_new  # pyright: ignore[reportUnknownMemberType]
        def set_floating_by_class(window: Any) -> None:  # pyright: ignore[reportUnusedFunction]
            """Set specific windows to floating based on WM class"""
            self._set_floating_by_class(window)

        @hook.subscribe.client_new  # pyright: ignore[reportUnknownMemberType]
        def set_parent_for_transient(window: Any) -> None:  # pyright: ignore[reportUnusedFunction]
            """Set parent for transient windows"""
            self.window_manager.set_parent_for_transient(window)



        @hook.subscribe.client_new  # pyright: ignore[reportUnknownMemberType]
        def handle_swallow(window: Any) -> None:  # pyright: ignore[reportUnusedFunction]
            """Handle terminal window swallowing"""
            self._handle_swallow(window)

        @hook.subscribe.client_killed  # pyright: ignore[reportUnknownMemberType]
        def handle_unswallow(window: Any) -> None:  # pyright: ignore[reportUnusedFunction]
            """Handle terminal window unswallowing"""
            self._handle_unswallow(window)

        @hook.subscribe.client_focus  # pyright: ignore[reportUnknownMemberType]
        def log_window_focus(window: Any) -> None:  # pyright: ignore[reportUnusedFunction]
            """Log window focus events for debugging"""
            if (
                hasattr(self.config, "debug_window_focus")
                and self.config.debug_window_focus
            ):
                window_name = self.window_manager._get_window_name(window)
                logger.debug(f"Window focused: {window_name}")

        @hook.subscribe.client_urgent_hint_changed  # pyright: ignore[reportUnknownMemberType]
        def handle_urgent_hint(window: Any) -> None:  # pyright: ignore[reportUnusedFunction]
            """Handle urgent hint changes"""
            if hasattr(window, "urgent") and window.urgent:  # pyright: ignore[reportUnknownArgumentType,reportUnknownMemberType]
                window_name = self.window_manager._get_window_name(window)
                logger.info(f"Window marked urgent: {window_name}")

    def _set_floating_by_class(self, window: Any) -> None:
        """
        @brief Set specific windows to floating based on force_floating_apps
        @param window Window object to check for floating rules
        """
        try:
            wm_class = window.window.get_wm_class()
            if wm_class and len(wm_class) > 0:
                if wm_class[0].lower() in [
                    fc.lower() for fc in self.config.force_floating_apps
                ]:
                    window.floating = True
                    logger.debug(
                        f"Set {wm_class[0]} to floating via force_floating_apps"
                    )
        except (IndexError, AttributeError, TypeError) as e:
            logger.debug(f"Could not check window class for floating: {e}")

    def _handle_swallow(self, window: Any) -> None:
        """
        @brief Handle terminal window swallowing (placeholder for future implementation)
        @param window Window object that might be swallowed
        """
        # Terminal swallowing logic can be implemented here
        # This would involve:
        # 1. Detecting if this is a terminal window
        # 2. Finding child processes
        # 3. Hiding the terminal when child GUI apps are launched
        pass

    def _handle_unswallow(self, window: Any) -> None:
        """
        @brief Handle terminal window unswallowing (placeholder for future implementation)
        @param window Window object that was previously swallowed
        """
        # Unswallowing logic can be implemented here
        # This would involve:
        # 1. Detecting when a swallowed app is closed
        # 2. Restoring the parent terminal window
        pass

    def get_client_statistics(self) -> dict[str, Any]:
        """
        @brief Get statistics about client hook handling
        @return Dictionary containing hook registration and rule counts
        """
        return {
            "hooks_registered": self._count_registered_hooks(),
            "force_floating_apps": (
                len(self.config.force_floating_apps)
                if hasattr(self.config, "force_floating_apps")
                else 0
            ),
            "floating_rules": (
                len(self.config.floating_rules)
                if hasattr(self.config, "floating_rules")
                else 0
            ),
        }

    def _count_registered_hooks(self) -> dict[str, int]:
        """
        @brief Count registered client hooks
        @return Dictionary mapping hook types to their counts
        """
        # This is a simplified count - in practice, qtile doesn't expose hook counts easily
        return {
            "client_new": 5,  # enforce_tiling_behavior, handle_transient_window, set_floating_by_class, set_parent_for_transient, handle_swallow
            "client_killed": 1,  # handle_unswallow
            "client_focus": 1,  # log_window_focus
            "client_urgent_hint_changed": 1,  # handle_urgent_hint
        }
