#!/usr/bin/env python3
"""
Main key manager class - orchestrates all key management functionality
"""

import os
from typing import Any

from libqtile.config import Key

from qtile_config import get_config

from .key_bindings import KeyBindings
from .layout_aware import LayoutAwareCommands
from .system_commands import SystemCommands
from .window_commands import WindowCommands


class KeyManager:
    """Manages keyboard bindings and shortcuts"""

    def __init__(self, color_manager):
        self.color_manager = color_manager
        self.config = get_config()
        self.mod = self.config.mod_key
        self.alt = self.config.alt_key
        self.homedir = os.getenv("HOME")
        self.terminal = self.config.terminal
        self.apps = self.config.applications

        # Initialize command modules
        self.layout_commands = LayoutAwareCommands()
        self.window_commands = WindowCommands(self.config)
        self.system_commands = SystemCommands(color_manager)

        # Initialize key bindings
        self.key_bindings = KeyBindings(
            self.config,
            self.layout_commands,
            self.window_commands,
            self.system_commands,
        )

    def get_keys(self) -> list[Key]:
        """Get all keyboard bindings"""
        return self.key_bindings.get_all_keys(key_manager=self)

    def get_keys_by_category(self) -> dict[str, list[Key]]:
        """Get keys organized by category"""
        return self.key_bindings.get_keys_by_category(key_manager=self)

    def get_key_statistics(self) -> dict[str, Any]:
        """Get statistics about key bindings"""
        categories = self.get_keys_by_category()
        total_keys = sum(len(keys) for keys in categories.values())

        return {
            "total_keys": total_keys,
            "categories": len(categories),
            "keys_per_category": self.key_bindings.get_key_count_by_category(),
            "modifier_usage": self._analyze_modifier_usage(),
        }

    def _analyze_modifier_usage(self) -> dict[str, int]:
        """Analyze usage of different modifier keys"""
        modifier_counts = {
            "mod_only": 0,
            "mod_shift": 0,
            "mod_control": 0,
            "mod_alt": 0,
            "alt_only": 0,
            "other": 0,
        }

        all_keys = self.get_keys()
        for key in all_keys:
            modifiers = set(key.modifiers) if key.modifiers else set()

            if modifiers == {self.mod}:
                modifier_counts["mod_only"] += 1
            elif modifiers == {self.mod, "shift"}:
                modifier_counts["mod_shift"] += 1
            elif modifiers == {self.mod, "control"}:
                modifier_counts["mod_control"] += 1
            elif self.alt in modifiers and self.mod in modifiers:
                modifier_counts["mod_alt"] += 1
            elif modifiers == {self.alt} or (
                len(modifiers) == 2 and self.alt in modifiers
            ):
                modifier_counts["alt_only"] += 1
            else:
                modifier_counts["other"] += 1

        return modifier_counts

    def find_key_conflicts(self) -> list[dict[str, Any]]:
        """Find potential key binding conflicts"""
        conflicts = []
        all_keys = self.get_keys()
        key_combinations = {}

        for key in all_keys:
            combo = (
                tuple(sorted(key.modifiers)) if key.modifiers else (),
                key.key,
            )
            if combo in key_combinations:
                conflicts.append(
                    {
                        "combination": combo,
                        "keys": [key_combinations[combo], key],
                        "descriptions": [
                            getattr(
                                key_combinations[combo],
                                "desc",
                                "No description",
                            ),
                            getattr(key, "desc", "No description"),
                        ],
                    }
                )
            else:
                key_combinations[combo] = key

        return conflicts

    def get_available_keys(
        self, modifier_combo: tuple | None = None
    ) -> list[str]:
        """Get list of available (unused) keys for a given modifier combination"""
        if modifier_combo is None:
            modifier_combo = (self.mod,)

        # Common keys to check
        all_possible_keys = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "0",
            "F1",
            "F2",
            "F3",
            "F4",
            "F5",
            "F6",
            "F7",
            "F8",
            "F9",
            "F10",
            "F11",
            "F12",
            "Up",
            "Down",
            "Left",
            "Right",
            "Home",
            "End",
            "Page_Up",
            "Page_Down",
            "Insert",
            "Delete",
            "BackSpace",
            "Tab",
            "Return",
            "space",
            "comma",
            "period",
            "slash",
            "backslash",
            "semicolon",
            "apostrophe",
            "bracketleft",
            "bracketright",
            "grave",
            "minus",
            "equal",
        ]

        # Get used keys for this modifier combination
        used_keys = set()
        all_keys = self.get_keys()
        for key in all_keys:
            key_modifiers = (
                tuple(sorted(key.modifiers)) if key.modifiers else ()
            )
            if key_modifiers == modifier_combo:
                used_keys.add(key.key)

        # Return available keys
        available = [key for key in all_possible_keys if key not in used_keys]
        return sorted(available)

    def validate_configuration(self) -> dict[str, Any]:
        """Validate the key configuration"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": self.get_key_statistics(),
            "conflicts": self.find_key_conflicts(),
        }

        # Check for conflicts
        if validation_results["conflicts"]:
            validation_results["valid"] = False
            validation_results["errors"].append(
                f"Found {len(validation_results['conflicts'])} key binding conflicts"
            )

        # Check for reasonable number of bindings
        total_keys = validation_results["statistics"]["total_keys"]
        if total_keys < 10:
            validation_results["warnings"].append(
                "Very few key bindings defined"
            )
        elif total_keys > 100:
            validation_results["warnings"].append(
                "Large number of key bindings may be hard to remember"
            )

        # Check modifier distribution
        modifier_usage = validation_results["statistics"]["modifier_usage"]
        if modifier_usage["mod_only"] > 26:  # More than alphabet
            validation_results["warnings"].append(
                "Too many single modifier bindings"
            )

        return validation_results

    def export_key_reference(self, format="text") -> str:
        """Export key bindings as reference documentation"""
        match format:
            case "text":
                return self._export_text_reference()
            case "markdown":
                return self._export_markdown_reference()
            case "html":
                return self._export_html_reference()
            case _:
                raise ValueError(f"Unsupported format: {format}")

    def _export_text_reference(self) -> str:
        """Export as plain text reference"""
        lines = ["Qtile Key Bindings Reference", "=" * 30, ""]

        categories = self.get_keys_by_category()
        for category, keys in categories.items():
            lines.append(f"{category}:")
            lines.append("-" * len(category) + ":")
            for key in keys:
                modifiers = "+".join(key.modifiers) if key.modifiers else ""
                combo = f"{modifiers}+{key.key}" if modifiers else key.key
                desc = getattr(key, "desc", "No description")
                lines.append(f"  {combo:<20} {desc}")
            lines.append("")

        return "\n".join(lines)

    def _export_markdown_reference(self) -> str:
        """Export as markdown reference"""
        lines = ["# Qtile Key Bindings Reference", ""]

        categories = self.get_keys_by_category()
        for category, keys in categories.items():
            lines.append(f"## {category}")
            lines.append("")
            lines.append("| Key Combination | Description |")
            lines.append("|-----------------|-------------|")

            for key in keys:
                modifiers = "+".join(key.modifiers) if key.modifiers else ""
                combo = f"{modifiers}+{key.key}" if modifiers else key.key
                desc = getattr(key, "desc", "No description")
                lines.append(f"| `{combo}` | {desc} |")
            lines.append("")

        return "\n".join(lines)

    def _export_html_reference(self) -> str:
        """Export as HTML reference"""
        html = ["<html><head><title>Qtile Key Bindings</title></head><body>"]
        html.append("<h1>Qtile Key Bindings Reference</h1>")

        categories = self.get_keys_by_category()
        for category, keys in categories.items():
            html.append(f"<h2>{category}</h2>")
            html.append("<table border='1'>")
            html.append(
                "<tr><th>Key Combination</th><th>Description</th></tr>"
            )

            for key in keys:
                modifiers = "+".join(key.modifiers) if key.modifiers else ""
                combo = f"{modifiers}+{key.key}" if modifiers else key.key
                desc = getattr(key, "desc", "No description")
                html.append(
                    f"<tr><td><code>{combo}</code></td><td>{desc}</td></tr>"
                )

            html.append("</table><br>")

        html.append("</body></html>")
        return "\n".join(html)


def create_key_manager(color_manager: Any) -> "KeyManager":
    """Create and return a key manager instance"""
    return KeyManager(color_manager)
