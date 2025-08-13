#!/usr/bin/env python3
"""
Groups and layouts module for qtile
Handles workspace groups and window layouts
"""

from typing import TYPE_CHECKING

from libqtile import layout
from libqtile.config import DropDown, Group, Key, Match, ScratchPad, _Match
from libqtile.lazy import lazy

from qtile_config import get_config



if TYPE_CHECKING:
    from modules.simple_color_management import SimpleColorManager

    ColorManager = SimpleColorManager
else:
    from modules.simple_color_management import SimpleColorManager

    ColorManager = SimpleColorManager





class GroupManager:
    """Manages workspace groups and layouts"""

    def __init__(self, color_manager: ColorManager) -> None:  # pyright: ignore[reportMissingSuperCall]
        self.color_manager = color_manager
        self.config = get_config()
        self.mod = self.config.mod_key

    def get_layouts(self):
        """Get all available layouts"""
        colordict = self.color_manager.get_colors()
        defaults = self.config.layout_defaults

        return [
            layout.Tile(
                margin=defaults["margin"],
                border_width=defaults["border_width"],
                border_focus=colordict["special"]["foreground"],
                border_normal=colordict["special"]["background"],
                **self.config.tile_layout,
            ),
            layout.MonadTall(
                margin=defaults["margin"],
                border_width=defaults["border_width"],
                border_focus=colordict["special"]["foreground"],
                border_normal=colordict["special"]["background"],
                **self.config.monad_tall_layout,
            ),
            layout.Matrix(
                margin=defaults["margin"],
                border_width=defaults["border_width"],
                border_focus=colordict["special"]["foreground"],
                border_normal=colordict["special"]["background"],
            ),
            layout.Bsp(
                margin=defaults["margin"],
                border_width=defaults["border_width"],
                border_focus=colordict["special"]["foreground"],
                border_normal=colordict["special"]["background"],
                **self.config.bsp_layout,
            ),
            layout.Max(),
        ]

    def get_floating_layout(self):
        """Get floating layout configuration with fixed default rules"""
        colordict = self.color_manager.get_colors()
        defaults = self.config.layout_defaults

        # Additional custom floating rules from config
        additional_rules = []
        for rule in self.config.floating_rules:
            if "wm_class" in rule:
                additional_rules.append(Match(wm_class=rule["wm_class"]))
            elif "title" in rule:
                additional_rules.append(Match(title=rule["title"]))

        return layout.Floating(
            float_rules=additional_rules,
            border_focus=colordict["special"]["foreground"],
            border_normal=colordict["special"]["background"],
            border_width=defaults["border_width"],
        )

    def get_groups(self):
        """Get all workspace groups"""
        groups = []
        for name, _kwargs in self.config.groups:  # kwargs not currently used
            groups.append(Group(name))

        # Add scratchpad
        dropdowns = []
        for scratch_config in self.config.scratchpads:
            dropdowns.append(
                DropDown(
                    str(scratch_config["name"]),
                    str(scratch_config["command"]),
                    width=scratch_config["width"],
                    height=scratch_config["height"],
                    x=scratch_config["x"],
                    y=scratch_config["y"],
                    opacity=scratch_config["opacity"],
                )
            )
        groups.append(ScratchPad("scratch", dropdowns))

        return groups, self.config.groups

    def get_group_keys(self):
        """Get group-related keyboard bindings"""
        _groups, group_names = self.get_groups()  # groups not used, just group_names
        keys = []

        for i, (name, _kwargs) in enumerate(group_names, 1):  # kwargs not used
            # Switch to another group
            keys.append(Key([self.mod], str(i), lazy.group[name].toscreen()))
            # Send current window to another group
            keys.append(
                Key([self.mod, "shift"], str(i), lazy.window.togroup(name))
            )

        return keys


def create_group_manager(color_manager: ColorManager) -> GroupManager:
    """Create and return a group manager instance"""
    return GroupManager(color_manager)
