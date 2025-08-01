#!/usr/bin/env python3
"""
Color validation and utility functions
"""

import hashlib
import json
import os
from typing import Dict, Union, Optional, Any
from libqtile.log_utils import logger


ColorDict = Dict[str, Union[Dict[str, str], str]]


def get_file_hash(filepath: str) -> Optional[str]:
    """Get SHA256 hash of file content"""
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Error getting file hash: {e}")
        return None


def validate_colors(colors: ColorDict) -> bool:
    """Validate color dictionary structure"""
    try:
        # Check required sections
        if 'special' not in colors or 'colors' not in colors:
            return False

        # Check special colors
        special = colors['special']
        if not isinstance(special, dict):
            return False
        
        required_special = ['background', 'foreground', 'cursor']
        for key in required_special:
            if key not in special:
                return False
            value = special[key]
            if not isinstance(value, str) or not value.startswith('#') or len(value) != 7:
                return False

        # Check color palette
        color_palette = colors['colors']
        if not isinstance(color_palette, dict):
            return False
        
        for i in range(16):
            color_key = f'color{i}'
            if color_key not in color_palette:
                return False
            color_val = color_palette[color_key]
            if not isinstance(color_val, str) or not color_val.startswith('#') or len(color_val) != 7:
                return False

        return True
    except Exception as e:
        logger.error(f"Error validating colors: {e}")
        return False


def load_default_colors() -> ColorDict:
    """Load default colors if pywal colors don't exist"""
    return {
        "wallpaper": "/home/ekollof/Wallpapers/derektaylor/0270.jpg",
        "alpha": "100",
        "special": {
            "background": "#0F0F0F",
            "foreground": "#d3d9db",
            "cursor": "#d3d9db"
        },
        "colors": {
            "color0": "#0F0F0F",
            "color1": "#9B8A77",
            "color2": "#4B768A",
            "color3": "#6A8FA0",
            "color4": "#97A1A1",
            "color5": "#AFB6B4",
            "color6": "#C2BEB5",
            "color7": "#d3d9db",
            "color8": "#939799",
            "color9": "#9B8A77",
            "color10": "#4B768A",
            "color11": "#6A8FA0",
            "color12": "#97A1A1",
            "color13": "#AFB6B4",
            "color14": "#E4A3A8",
            "color15": "#E9D2D4"
        }
    }


def load_colors_from_file(filepath: str) -> Optional[ColorDict]:
    """Load and validate colors from a JSON file"""
    try:
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r', encoding="utf-8") as f:
            colors: ColorDict = json.load(f)
            
        if validate_colors(colors):
            return colors
        else:
            logger.warning(f"Invalid colors in file: {filepath}")
            return None
            
    except Exception as e:
        logger.error(f"Error loading colors from {filepath}: {e}")
        return None


def ensure_directories(*directories: str) -> None:
    """Ensure all required directories exist"""
    try:
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
