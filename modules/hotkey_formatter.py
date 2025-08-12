#!/usr/bin/env python3
"""
Key formatting utilities for hotkey display
"""


class KeyFormatter:
    """Handles formatting of key combinations and descriptions"""

    @staticmethod
    def format_key_combination(key_combo: str) -> str:
        """Format key combination for display"""
        # Replace modifier names with more readable versions
        formatted = key_combo.replace("mod4", "Super")
        formatted = formatted.replace("mod1", "Alt")
        formatted = formatted.replace("shift", "Shift")
        formatted = formatted.replace("control", "Ctrl")

        # Capitalize single keys
        parts = formatted.split("+")
        if len(parts) > 1:
            # Last part is the main key
            parts[-1] = parts[-1].capitalize()
        else:
            parts[0] = parts[0].capitalize()

        return "+".join(parts)

    @staticmethod
    def extract_key_combination(key) -> str:
        """Extract key combination from key object"""
        # Extract modifiers and key
        modifiers = key.modifiers if key.modifiers else []
        key_name = key.key

        # Combine modifiers and key
        if modifiers:
            key_combo = "+".join(modifiers) + "+" + key_name
        else:
            key_combo = key_name

        return key_combo

    @staticmethod
    def infer_description(key) -> str:
        """Infer description from key command if not explicitly provided"""
        # Try to get explicit description first
        description = getattr(key, "desc", None)
        if description:
            return description

        # Try to infer from commands
        if hasattr(key, "commands") and key.commands:
            cmd = key.commands[0]

            if hasattr(cmd, "__name__"):
                return cmd.__name__.replace("_", " ").title()
            elif hasattr(cmd, "name"):
                return cmd.name.replace("_", " ").title()
            else:
                return KeyFormatter._parse_command_string(cmd)

        return "Custom action"

    @staticmethod
    def _parse_command_string(cmd) -> str:
        """Parse command string to extract meaningful description"""
        cmd_str = str(cmd).lower()

        # Use match statement for cleaner pattern matching
        match True:
            case _ if "spawn" in cmd_str:
                # Extract spawn command
                if hasattr(cmd, "args") and cmd.args:
                    app_name = (
                        cmd.args[0].split("/")[-1]
                        if "/" in cmd.args[0]
                        else cmd.args[0]
                    )
                    return f"Launch {app_name}"
                else:
                    return "Launch application"
            case _ if "layout" in cmd_str:
                return "Change layout"
            case _ if "group" in cmd_str:
                return "Switch group"
            case _ if "window" in cmd_str:
                return "Window action"
            case _:
                return str(cmd)[:50]  # Truncate long descriptions

    @staticmethod
    def format_hotkey_line(
        key_combo: str, description: str, width: int = 25
    ) -> str:
        """Format a single hotkey line for display"""
        formatted_combo = KeyFormatter.format_key_combination(key_combo)
        return f"{formatted_combo:<{width}} {description}"

    @staticmethod
    def create_instructions() -> list[str]:
        """Create instruction lines for the hotkey display"""
        return [
            "Press Escape or Enter to close this window",
            "Tip: Most actions use Super (Windows) key as modifier",
            "",
        ]
