#!/usr/bin/env python3
"""
Font utilities for qtile
Handles font detection, fallbacks, and cross-platform font management
"""

import subprocess
import platform
import os
from typing import List, Optional
from libqtile.log_utils import logger


class FontManager:
    """Manages font detection and fallback for qtile widgets"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self._font_cache = {}

    def get_available_font(self, preferred_font: Optional[str] = None, fallback_fonts: Optional[List[str]] = None) -> str:
        """
        Get the best available font with user preference and smart fallbacks.
        
        Args:
            preferred_font: User's preferred font (e.g., "BerkeleyMono Nerd Font Mono")
            fallback_fonts: List of fallback fonts to try if preferred font is not available
            
        Returns:
            The first available font name
        """
        # Default fallback fonts (common monospace fonts across platforms)
        if fallback_fonts is None:
            fallback_fonts = [
                "JetBrains Mono",
                "Fira Code",
                "Source Code Pro", 
                "Hack",
                "Inconsolata",
                "DejaVu Sans Mono",
                "Liberation Mono",
                "Consolas",  # Windows
                "Monaco",    # macOS
                "Monospace", # Generic Linux
                "monospace"  # Lowercase fallback
            ]
        
        # Build preference list: user preference first, then fallbacks
        fonts_to_try = []
        if preferred_font:
            fonts_to_try.append(preferred_font)
        fonts_to_try.extend(fallback_fonts)
        
        # Check cache first
        cache_key = (preferred_font, tuple(fallback_fonts))
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        # Try each font in order
        for font in fonts_to_try:
            if self._is_font_available(font):
                logger.debug(f"Selected font: {font}")
                self._font_cache[cache_key] = font
                return font
        
        # Ultimate fallback
        final_fallback = "monospace"
        logger.warning(f"No fonts available from preferences, using final fallback: {final_fallback}")
        self._font_cache[cache_key] = final_fallback
        return final_fallback

    def _is_font_available(self, font_name: str) -> bool:
        """Check if a font is available on the system"""
        try:
            if self.system == "linux":
                return self._check_font_linux(font_name)
            elif self.system in ["openbsd", "freebsd", "netbsd", "dragonfly"]:
                return self._check_font_bsd(font_name)
            elif self.system == "darwin":
                return self._check_font_macos(font_name)
            else:
                # Unknown system: assume basic fonts are available
                return font_name.lower() in ["monospace", "mono", "sans-serif", "serif"]
        except Exception as e:
            logger.debug(f"Error checking font {font_name}: {e}")
            return False

    def _check_font_linux(self, font_name: str) -> bool:
        """Check font availability on Linux using fontconfig"""
        try:
            # Use fc-match to check if font resolves to itself
            result = subprocess.run(
                ['fc-match', '--format=%{family}', font_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                matched_family = result.stdout.strip()
                # If fc-match returns the same font name, it's available
                return font_name.lower() == matched_family.lower()
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # fc-match not available, try fc-list as backup
            try:
                result = subprocess.run(
                    ['fc-list', ':', 'family'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return font_name.lower() in result.stdout.lower()
                return False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # No fontconfig tools available
                return font_name.lower() in ["monospace", "mono"]

    def _check_font_bsd(self, font_name: str) -> bool:
        """Check font availability on BSD systems"""
        try:
            # Try fc-match if available (on systems with fontconfig)
            result = subprocess.run(
                ['fc-match', '--format=%{family}', font_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                matched_family = result.stdout.strip()
                return font_name.lower() == matched_family.lower()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback: check common font directories
        font_dirs = [
            '/usr/X11R6/lib/X11/fonts',
            '/usr/local/share/fonts',
            '/usr/share/fonts',
            os.path.expanduser('~/.fonts'),
        ]
        
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                try:
                    for root, dirs, files in os.walk(font_dir):
                        for file in files:
                            if (file.lower().endswith(('.ttf', '.otf', '.pfb', '.pcf')) and
                                font_name.replace(' ', '').lower() in file.lower()):
                                return True
                except Exception:
                    continue
        
        # Default fallback fonts that should be available
        return font_name.lower() in ["monospace", "mono", "fixed"]

    def _check_font_macos(self, font_name: str) -> bool:
        """Check font availability on macOS"""
        try:
            # Use system_profiler to check available fonts
            result = subprocess.run(
                ['system_profiler', 'SPFontsDataType'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return font_name in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback: assume common macOS fonts are available
        common_macos_fonts = ["monaco", "menlo", "courier", "courier new"]
        return font_name.lower() in common_macos_fonts

    def get_font_info(self, preferred_font: Optional[str] = None) -> dict:
        """Get information about font selection for debugging"""
        selected_font = self.get_available_font(preferred_font)
        return {
            'preferred_font': preferred_font,
            'selected_font': selected_font,
            'is_preferred': selected_font == preferred_font if preferred_font else False,
            'is_fallback': selected_font.lower() in ['monospace', 'mono'],
            'system': self.system,
            'cache_size': len(self._font_cache)
        }

    def clear_cache(self):
        """Clear the font cache (useful for testing)"""
        self._font_cache.clear()


# Global font manager instance
_font_manager = FontManager()


def get_available_font(preferred_font: Optional[str] = None, fallback_fonts: Optional[List[str]] = None) -> str:
    """
    Convenience function to get an available font.
    
    Args:
        preferred_font: User's preferred font
        fallback_fonts: List of fallback fonts
        
    Returns:
        The first available font name
    """
    return _font_manager.get_available_font(preferred_font, fallback_fonts)


def get_font_info(preferred_font: Optional[str] = None) -> dict:
    """Get font selection information for debugging"""
    return _font_manager.get_font_info(preferred_font)
