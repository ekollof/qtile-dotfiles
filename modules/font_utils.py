#!/usr/bin/env python3
"""
Font utilities for qtile
Handles font detection, fallbacks, and cross-platform font management
"""

import subprocess
import platform
from pathlib import Path

from libqtile.log_utils import logger

class FontManager:
    """Manages font detection and fallback for qtile widgets"""

    def __init__(self):
        self.system = platform.system().lower()
        self._font_cache = {}

    def get_available_font(self, preferred_font: str | None = None, fallback_fonts: list[str | None] = None) -> str:
        """
        @brief Get the best available font with user preference and smart fallbacks
        @param preferred_font User's preferred font (e.g., "BerkeleyMono Nerd Font Mono")
        @param fallback_fonts List of fallback fonts to try if preferred font is not available
        @return The first available font name from preference list or system fallback
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
        """
        @brief Check if a font is available on the system
        @param font_name The name of the font to check for availability
        @return True if font is available, False otherwise
        """
        try:
            match self.system:
                case "linux":
                    return self._check_font_linux(font_name)
                case "openbsd" | "freebsd" | "netbsd" | "dragonfly":
                    return self._check_font_bsd(font_name)
                case "darwin":
                    return self._check_font_macos(font_name)
                case _:
                    # Unknown system: assume basic fonts are available
                    return font_name.lower() in ["monospace", "mono", "sans-serif", "serif"]
        except Exception as e:
            logger.debug(f"Error checking font {font_name}: {e}")
            return False

    def _check_font_linux(self, font_name: str) -> bool:
        """
        @brief Check font availability on Linux using fontconfig
        @param font_name The font name to verify
        @return True if font exists and is accessible on Linux systems
        @throws subprocess.TimeoutExpired if fontconfig commands timeout
        """
        try:
            # Use fc-match to check if font resolves to itself (preferred method)
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
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug(f"fc-match failed for {font_name}: {e}")
            
        # Backup method: try fc-list as fallback
        try:
            result = subprocess.run(
                ['fc-list', ':', 'family'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return font_name.lower() in result.stdout.lower()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug(f"fc-list failed for {font_name}: {e}")

        # Final fallback: assume basic fonts are available
        return font_name.lower() in ["monospace", "mono"]

    def _check_font_bsd(self, font_name: str) -> bool:
        """
        @brief Check font availability on BSD systems
        @param font_name The font name to verify
        @return True if font exists on BSD systems (OpenBSD, FreeBSD, NetBSD, DragonFly)
        """
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
            Path('/usr/X11R6/lib/X11/fonts'),
            Path('/usr/local/share/fonts'),
            Path('/usr/share/fonts'),
            Path('~/.fonts').expanduser(),
        ]

        for font_dir in font_dirs:
            if font_dir.exists():
                try:
                    for font_file in font_dir.rglob('*'):
                        if (font_file.is_file() and
                            font_file.suffix.lower() in ('.ttf', '.otf', '.pfb', '.pcf') and
                            font_name.replace(' ', '').lower() in font_file.name.lower()):
                            return True
                except Exception:
                    continue

        # Default fallback fonts that should be available
        return font_name.lower() in ["monospace", "mono", "fixed"]

    def _check_font_macos(self, font_name: str) -> bool:
        """
        @brief Check font availability on macOS
        @param font_name The font name to verify
        @return True if font exists on macOS systems
        @throws subprocess.TimeoutExpired if system_profiler command times out
        """
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

    def get_font_info(self, preferred_font: str | None = None) -> dict:
        """
        @brief Get information about font selection for debugging
        @param preferred_font The preferred font to analyze
        @return Dictionary containing font selection details and system information
        """
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
        """
        @brief Clear the font cache (useful for testing)
        """
        self._font_cache.clear()

# Global font manager instance
_font_manager = FontManager()

def get_available_font(preferred_font: str | None = None, fallback_fonts: list[str | None] = None) -> str:
    """
    @brief Convenience function to get an available font
    @param preferred_font User's preferred font
    @param fallback_fonts List of fallback fonts
    @return The first available font name
    """
    return _font_manager.get_available_font(preferred_font, fallback_fonts)

def get_font_info(preferred_font: str | None = None) -> dict:
    """
    @brief Get font selection information for debugging
    @param preferred_font The preferred font to analyze
    @return Dictionary containing font selection details
    """
    return _font_manager.get_font_info(preferred_font)