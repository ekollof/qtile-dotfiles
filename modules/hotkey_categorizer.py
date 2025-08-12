#!/usr/bin/env python3
"""
Hotkey categorization functionality
"""

from .hotkey_formatter import KeyFormatter


class HotkeyCategorizer:
    """Handles categorization and organization of hotkeys"""

    def __init__(self):  # pyright: ignore[reportMissingSuperCall]
        self.categories = {
            "Window Management": [],
            "Layout Control": [],
            "Group/Workspace": [],
            "System": [],
            "Applications": [],
            "Screen/Display": [],
            "Other": [],
        }

    def clear_categories(self):
        """Clear all categories"""
        for category in self.categories.values():
            category.clear()

    def categorize_key(self, key) -> str:
        """Determine the appropriate category for a key"""
        key_name = key.key
        description = KeyFormatter.infer_description(key).lower()

        # Check if it's a number key (likely group/workspace)
        if key_name.isdigit():
            return "Group/Workspace"

        # Define keyword categories
        window_words = ["window", "focus", "move", "close", "kill", "floating"]
        layout_words = ["layout", "tile", "max", "split"]
        group_words = ["group", "workspace"]
        system_words = [
            "restart",
            "quit",
            "shutdown",
            "reload",
            "screen",
            "color",
        ]
        app_words = ["launch", "spawn", "browser", "terminal"]
        display_words = ["screen", "monitor", "display"]

        # Categorize based on description content using match statements
        match True:
            case _ if any(word in description for word in window_words):
                return "Window Management"
            case _ if any(word in description for word in layout_words):
                return "Layout Control"
            case _ if any(word in description for word in group_words):
                return "Group/Workspace"
            case _ if any(word in description for word in system_words):
                return "System"
            case _ if any(word in description for word in app_words):
                return "Applications"
            case _ if any(word in description for word in display_words):
                return "Screen/Display"
            case _:
                return "Other"

    def add_key_to_category(self, key, category: str | None = None):
        """Add a key to the appropriate category"""
        if category is None:
            category = self.categorize_key(key)

        # Extract key combination and description
        key_combo = KeyFormatter.extract_key_combination(key)
        description = KeyFormatter.infer_description(key)

        # Format the hotkey line
        hotkey_line = KeyFormatter.format_hotkey_line(key_combo, description)

        # Add to category
        if category in self.categories:
            self.categories[category].append(hotkey_line)
        else:
            self.categories["Other"].append(hotkey_line)

    def process_keys(self, keys: list) -> dict[str, list[str]]:
        """Process a list of keys and categorize them"""
        self.clear_categories()

        for key in keys:
            self.add_key_to_category(key)

        # Sort hotkeys within each category
        for category_hotkeys in self.categories.values():
            category_hotkeys.sort()

        return self.categories

    def build_formatted_list(
        self, include_instructions: bool = True
    ) -> list[str]:
        """Build the final formatted hotkey list with categories"""
        final_hotkeys = []

        # Add instructions if requested
        if include_instructions:
            final_hotkeys.extend(KeyFormatter.create_instructions())

        # Add categories with hotkeys
        for category_name, category_hotkeys in self.categories.items():
            if category_hotkeys:  # Only show categories that have hotkeys
                final_hotkeys.append("")  # Empty line for separation
                final_hotkeys.append(f"=== {category_name} ===")
                final_hotkeys.extend(category_hotkeys)

        return final_hotkeys

    def get_category_summary(self) -> dict[str, int]:
        """Get a summary of hotkeys per category"""
        return {
            category: len(hotkeys)
            for category, hotkeys in self.categories.items()
            if hotkeys
        }

    def search_hotkeys(self, search_term: str) -> list[str]:
        """Search for hotkeys containing the search term"""
        search_term = search_term.lower()
        results = []

        for category_name, category_hotkeys in self.categories.items():
            for hotkey in category_hotkeys:
                if search_term in hotkey.lower():
                    results.append(f"[{category_name}] {hotkey}")

        return results
