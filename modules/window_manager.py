#!/usr/bin/env python3
"""
Window management utilities and floating window logic
"""

from typing import Any

from libqtile.log_utils import logger


class WindowManager:
    """Handles window state management and floating window logic"""

    def __init__(self, config):
        self.config = config

    def should_window_float(self, window) -> bool:
        """Determine if a window should be floating based on floating rules"""
        try:
            wm_class = window.window.get_wm_class()

            if wm_class and len(wm_class) > 0:
                if self._check_force_floating_apps(wm_class):
                    return True
                if self._check_floating_rules(wm_class, window):
                    return True

            if self._check_transient_window(window):
                return True

            if self._check_wm_hints(window):
                return True

            return False

        except (IndexError, AttributeError, TypeError) as e:
            logger.debug(f"Could not determine if window should float: {e}")
            return False  # Default to tiling if we can't determine

    def _check_force_floating_apps(self, wm_class) -> bool:
        """Check if window class is in force floating apps list"""
        return wm_class[0].lower() in [
            fc.lower() for fc in self.config.force_floating_apps
        ]

    def _check_floating_rules(self, wm_class, window) -> bool:
        """Check against floating rules from configuration"""
        for rule in self.config.floating_rules:
            if self._check_wm_class_rule(wm_class, rule):
                return True
            if self._check_title_rule(window, rule):
                return True
        return False

    def _check_wm_class_rule(self, wm_class, rule) -> bool:
        """Check if window class matches floating rule"""
        if "wm_class" not in rule:
            return False

        rule_class = rule["wm_class"].lower()
        if wm_class[0].lower() == rule_class:
            return True
        if len(wm_class) >= 2 and wm_class[1].lower() == rule_class:
            return True
        return False

    def _check_title_rule(self, window, rule) -> bool:
        """Check if window title matches floating rule"""
        if "title" not in rule:
            return False

        try:
            window_title = window.window.get_name() or ""
            return rule["title"].lower() in window_title.lower()
        except Exception:
            return False

    def _check_transient_window(self, window) -> bool:
        """Check if window is transient (should float)"""
        return bool(window.window.get_wm_transient_for())

    def _check_wm_hints(self, window) -> bool:
        """Check WM hints for dialog-like windows"""
        hints = window.window.get_wm_normal_hints()
        if hints and hints.get("max_width") and hints.get("max_width") < 1000:
            return True
        return False

    def enforce_window_tiling(self, window):
        """Enforce consistent tiling behavior for a window"""
        try:
            # Determine if this window should float based on our rules
            should_float = self.should_window_float(window)

            if not should_float:
                # Force this window to tile
                window.floating = False
                app_name = self._get_window_name(window)
                logger.debug(f"Enforced tiling for: {app_name}")
            else:
                # This window should float
                window.floating = True
                app_name = self._get_window_name(window)
                logger.debug(f"Allowed floating for: {app_name}")

        except (IndexError, AttributeError, TypeError) as e:
            logger.debug(f"Could not determine window floating behavior: {e}")

    def force_retile_all_windows(self, qtile) -> int:
        """Manual command to force all windows to tile (useful for testing/debugging)"""
        try:
            retiled_count = 0
            for window in qtile.windows_map.values():
                if hasattr(window, "window") and hasattr(window, "floating"):
                    try:
                        should_float = self.should_window_float(window)

                        if not should_float and window.floating:
                            window.floating = False
                            retiled_count += 1
                            app_name = self._get_window_name(window)
                            logger.info(f"Manually re-tiled: {app_name}")
                    except (IndexError, AttributeError, TypeError) as e:
                        logger.debug(
                            f"Could not check window during manual retiling: {e}"
                        )
                        continue
            logger.info(
                f"Manual retiling complete - retiled {retiled_count} windows"
            )
            return retiled_count
        except Exception as e:
            logger.error(f"Error during manual retiling: {e}")
            return 0

    def retile_windows_after_startup(self, qtile) -> int:
        """Force all windows to tile after qtile restart (except explicitly floating ones)"""
        try:
            retiled_count = 0
            # Force all windows to tile unless they should be floating
            for window in qtile.windows_map.values():
                if hasattr(window, "window") and hasattr(window, "floating"):
                    try:
                        # Check if this window should be floating based on our rules
                        should_float = self.should_window_float(window)

                        if not should_float and window.floating:
                            window.floating = False  # Force to tile
                            retiled_count += 1
                            app_name = self._get_window_name(window)
                            logger.info(
                                f"Re-tiled window after restart: {app_name}"
                            )

                    except (IndexError, AttributeError, TypeError) as e:
                        logger.debug(
                            f"Could not check window during retiling: {e}"
                        )
                        continue
            logger.info(
                f"Completed window retiling after startup - retiled {retiled_count} windows"
            )
            return retiled_count
        except Exception as e:
            logger.error(f"Error during window retiling: {e}")
            return 0

    def handle_transient_window(self, window):
        """Handle WM hints for transient windows"""
        try:
            hints = window.window.get_wm_normal_hints()
            if window.window.get_wm_transient_for():
                window.floating = True
                logger.debug(
                    f"Set transient window to floating: {self._get_window_name(window)}"
                )
            if hints and hints.get("max_width") and hints.get("max_width") < 1000:
                window.floating = True
                logger.debug(
                    f"Set window with small max_width to floating: {self._get_window_name(window)} (max_width={hints.get('max_width')})"
                )
        except Exception as e:
            logger.debug(f"Error handling transient window: {e}")

    def set_parent_for_transient(self, window):
        """Set parent for transient windows"""
        try:
            if window.window.get_wm_transient_for():
                parent = window.window.get_wm_transient_for()
                for client in window.qtile.windows_map.values():
                    if (
                        hasattr(client, "window")
                        and client.window.wid == parent
                    ):
                        window.parent = client
                        logger.debug(
                            f"Set parent for transient window: {self._get_window_name(window)}"
                        )
                        return
        except Exception as e:
            logger.debug(f"Error setting parent for transient window: {e}")

    def get_window_statistics(self, qtile) -> dict[str, Any]:
        """Get statistics about current windows"""
        try:
            stats = {
                "total_windows": 0,
                "floating_windows": 0,
                "tiled_windows": 0,
                "transient_windows": 0,
                "windows_by_class": {},
                "windows_by_group": {},
            }

            for window in qtile.windows_map.values():
                if hasattr(window, "window") and hasattr(window, "floating"):
                    stats["total_windows"] += 1

                    if window.floating:
                        stats["floating_windows"] += 1
                    else:
                        stats["tiled_windows"] += 1

                    if window.window.get_wm_transient_for():
                        stats["transient_windows"] += 1

                    # Count by class
                    wm_class = self._get_window_class(window)
                    if wm_class:
                        stats["windows_by_class"][wm_class] = (
                            stats["windows_by_class"].get(wm_class, 0) + 1
                        )

                    # Count by group
                    if hasattr(window, "group") and window.group:
                        group_name = window.group.name
                        stats["windows_by_group"][group_name] = (
                            stats["windows_by_group"].get(group_name, 0) + 1
                        )

            return stats
        except Exception as e:
            logger.error(f"Error getting window statistics: {e}")
            return {}

    def validate_floating_rules(self) -> dict[str, Any]:
        """Validate the floating rules configuration"""
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "rule_count": 0,
            "force_floating_count": 0,
        }

        try:
            # Check floating rules
            validation["rule_count"] = len(self.config.floating_rules)
            for i, rule in enumerate(self.config.floating_rules):
                if not isinstance(rule, dict):
                    validation["errors"].append(
                        f"Rule {i} is not a dictionary"
                    )
                    validation["valid"] = False
                elif "wm_class" not in rule and "title" not in rule:
                    validation["warnings"].append(
                        f"Rule {i} has neither wm_class nor title"
                    )

            # Check force floating apps
            validation["force_floating_count"] = len(
                self.config.force_floating_apps
            )
            for app in self.config.force_floating_apps:
                if not isinstance(app, str):
                    validation["errors"].append(
                        f"Force floating app '{app}' is not a string"
                    )
                    validation["valid"] = False

        except AttributeError as e:
            validation["errors"].append(
                f"Missing configuration attribute: {e}"
            )
            validation["valid"] = False

        return validation

    def _get_window_name(self, window) -> str:
        """Get a human-readable name for a window"""
        try:
            wm_class = window.window.get_wm_class()
            if wm_class and len(wm_class) >= 2:
                return wm_class[1]
            elif wm_class and len(wm_class) >= 1:
                return wm_class[0]
            else:
                return "Unknown"
        except Exception:
            return "Unknown"

    def _get_window_class(self, window) -> str | None:
        """Get the WM class of a window"""
        try:
            wm_class = window.window.get_wm_class()
            if wm_class and len(wm_class) >= 1:
                return wm_class[0]
            return None
        except Exception:
            return None

    def list_floating_windows(self, qtile) -> list[dict[str, Any]]:
        """Get list of currently floating windows with details"""
        floating_windows = []
        try:
            for window in qtile.windows_map.values():
                if (
                    hasattr(window, "window")
                    and hasattr(window, "floating")
                    and window.floating
                ):
                    window_info = {
                        "name": self._get_window_name(window),
                        "class": self._get_window_class(window),
                        "transient": bool(
                            window.window.get_wm_transient_for()
                        ),
                        "group": (
                            window.group.name
                            if hasattr(window, "group") and window.group
                            else None
                        ),
                    }
                    floating_windows.append(window_info)
        except Exception as e:
            logger.error(f"Error listing floating windows: {e}")

        return floating_windows

    def get_problematic_windows(self, qtile) -> list[dict[str, Any]]:
        """Get list of windows that might be causing issues"""
        problematic = []
        try:
            for window in qtile.windows_map.values():
                if hasattr(window, "window") and hasattr(window, "floating"):
                    issues = []

                    # Check if window should float but is tiled (or vice versa)
                    should_float = self.should_window_float(window)
                    if should_float and not window.floating:
                        issues.append("Should be floating but is tiled")
                    elif not should_float and window.floating:
                        issues.append("Should be tiled but is floating")

                    # Check for missing parent in transient windows
                    if window.window.get_wm_transient_for() and not hasattr(
                        window, "parent"
                    ):
                        issues.append("Transient window without parent")

                    if issues:
                        problematic.append(
                            {
                                "name": self._get_window_name(window),
                                "class": self._get_window_class(window),
                                "issues": issues,
                                "floating": window.floating,
                                "transient": bool(
                                    window.window.get_wm_transient_for()
                                ),
                            }
                        )
        except Exception as e:
            logger.error(f"Error getting problematic windows: {e}")

        return problematic
