#!/usr/bin/env python3
"""
@brief Platform-specific mascot icon generator for qtile bars
@file platform_icons.py

Creates beautiful, simplified SVG versions of platform mascots:
- Linux: Tux the penguin
- OpenBSD: Puffy the pufferfish  
- FreeBSD: Beastie the daemon
- NetBSD: Flag logo
- macOS: Apple logo
- Windows: Windows logo

@author Qtile configuration system  
@note This module follows Python 3.10+ standards and project guidelines
"""

import platform
from typing import Any

try:
    from libqtile.log_utils import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class PlatformMascotGenerator:
    """
    @brief Generates platform-specific mascot icons for the system bar
    
    Detects the current platform and provides appropriate SVG mascot icons
    that represent the operating system in a fun, recognizable way.
    """
    
    def __init__(self, color_manager: Any = None) -> None:  # pyright: ignore[reportMissingSuperCall]
        """
        @brief Initialize platform mascot generator
        @param color_manager: Optional color manager for theming
        """
        self.color_manager = color_manager
        self.current_platform = self._detect_platform()
        logger.debug(f"Detected platform: {self.current_platform}")
    
    def _detect_platform(self) -> str:
        """
        @brief Detect the current operating system platform
        @return Platform identifier string
        """
        system = platform.system().lower()
        
        # Use modern match statement (Python 3.10+)
        match system:
            case "openbsd":
                return "openbsd"
            case "freebsd":
                return "freebsd"
            case "netbsd":
                return "netbsd"
            case "dragonfly":
                return "dragonfly"
            case "linux":
                return "linux"
            case "darwin":
                return "macos"
            case "windows":
                return "windows"
            case _:
                # Try to detect from uname if available
                try:
                    uname = platform.uname()
                    uname_system = uname.system.lower()
                    match True:
                        case _ if "openbsd" in uname_system:
                            return "openbsd"
                        case _ if "freebsd" in uname_system:
                            return "freebsd"
                        case _ if "netbsd" in uname_system:
                            return "netbsd"
                        case _ if "bsd" in uname_system:
                            return "bsd"  # Generic BSD
                        case _:
                            return "linux"  # Default fallback
                except Exception:
                    return "linux"  # Default fallback
    
    def get_platform_mascot(self, size: int = 24) -> str:
        """
        @brief Get SVG content for the current platform's mascot
        @param size: Icon size in pixels
        @return SVG content as string
        """
        colors = self._get_colors()
        
        match self.current_platform:
            case "linux":
                return self._tux_penguin(size, colors)
            case "openbsd":
                return self._puffy_pufferfish(size, colors)
            case "freebsd":
                return self._beastie_daemon(size, colors)
            case "netbsd":
                return self._netbsd_flag(size, colors)
            case "macos":
                return self._apple_logo(size, colors)
            case "windows":
                return self._windows_logo(size, colors)
            case _:
                return self._generic_computer(size, colors)
    
    def _get_colors(self) -> dict[str, str]:
        """
        @brief Get themed colors for the mascot
        @return Dictionary of color values
        """
        if self.color_manager:
            try:
                qtile_colors = self.color_manager.get_colors()
                if qtile_colors and "colors" in qtile_colors:
                    return {
                        "primary": qtile_colors["colors"]["color5"],      # Main color (blue)
                        "secondary": qtile_colors["colors"]["color11"],   # Warning/accent color
                        "accent": qtile_colors["colors"]["color4"],       # Different blue
                        "highlight": qtile_colors["colors"]["color15"],   # Light color
                        "dark": qtile_colors["colors"]["color0"],         # Dark color
                        "background": qtile_colors["special"]["background"],
                        "foreground": qtile_colors["colors"]["color5"],   # Match text
                        "white": qtile_colors["colors"]["color15"],       # Light/white
                        "orange": qtile_colors["colors"]["color11"],      # Orange/yellow
                    }
            except Exception as e:
                logger.debug(f"Could not get colors from color_manager: {e}")
        
        # Fallback colors
        return {
            "primary": "#4A88A2",      # Medium blue
            "secondary": "#9E6C8F",    # Purple accent  
            "accent": "#39919B",       # Teal
            "highlight": "#C5C5DE",    # Light purple
            "dark": "#424446",         # Dark gray
            "background": "#17191A",   # Dark background
            "foreground": "#4A88A2",   # Match text color
            "white": "#C5C5DE",        # Light color
            "orange": "#9E6C8F",       # Orange/accent
        }
    
    def _tux_penguin(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate Tux the penguin (Linux mascot)
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Use multiple themed colors for contrast
        black = colors["dark"]           # Dark body
        white = colors["white"]          # Belly and face
        orange = colors["orange"]        # Beak and feet
        primary = colors["primary"]      # Eyes and details
        
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Tux the Penguin - Linux Mascot -->
            <!-- Main body (black) -->
            <ellipse cx="12" cy="16" rx="6" ry="5" fill="{black}"/>
            
            <!-- Head (black) -->
            <circle cx="12" cy="8" r="4.5" fill="{black}"/>
            
            <!-- White belly -->  
            <ellipse cx="12" cy="15.5" rx="3.5" ry="3.5" fill="{white}"/>
            
            <!-- White face area -->
            <ellipse cx="12" cy="8.5" rx="2.5" ry="2" fill="{white}"/>
            
            <!-- Orange beak -->
            <ellipse cx="12" cy="9.5" rx="1" ry="0.5" fill="{orange}"/>
            
            <!-- Eyes (black dots) -->
            <circle cx="10.5" cy="7.5" r="0.6" fill="{black}"/>
            <circle cx="13.5" cy="7.5" r="0.6" fill="{black}"/>
            
            <!-- Eye highlights -->
            <circle cx="10.7" cy="7.3" r="0.2" fill="{white}"/>
            <circle cx="13.7" cy="7.3" r="0.2" fill="{white}"/>
            
            <!-- Wings/flippers -->
            <ellipse cx="7.5" cy="13" rx="1.5" ry="3" fill="{black}"/>
            <ellipse cx="16.5" cy="13" rx="1.5" ry="3" fill="{black}"/>
            
            <!-- Orange feet -->
            <ellipse cx="10" cy="20" rx="1.5" ry="0.8" fill="{orange}"/>
            <ellipse cx="14" cy="20" rx="1.5" ry="0.8" fill="{orange}"/>
        </svg>'''
    
    def _puffy_pufferfish(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate Puffy the pufferfish (OpenBSD mascot)
        @param size: Icon size  
        @param colors: Color scheme
        @return SVG content
        """
        # Use multiple themed colors for contrast
        body_color = colors["primary"]     # Main body
        spike_color = colors["accent"]     # Spikes 
        eye_color = colors["dark"]         # Eyes
        mouth_color = colors["orange"]     # Mouth
        fin_color = colors["secondary"]    # Fins and tail
        
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Puffy the Pufferfish - OpenBSD Mascot -->
            <!-- Main body -->
            <circle cx="12" cy="12" r="7" fill="{body_color}"/>
            
            <!-- Spikes around body -->
            <circle cx="8" cy="8" r="0.6" fill="{spike_color}"/>
            <circle cx="16" cy="8" r="0.6" fill="{spike_color}"/>
            <circle cx="8" cy="16" r="0.6" fill="{spike_color}"/>
            <circle cx="16" cy="16" r="0.6" fill="{spike_color}"/>
            <circle cx="6" cy="12" r="0.6" fill="{spike_color}"/>
            <circle cx="18" cy="12" r="0.6" fill="{spike_color}"/>
            <circle cx="12" cy="6" r="0.6" fill="{spike_color}"/>
            <circle cx="12" cy="18" r="0.6" fill="{spike_color}"/>
            
            <!-- Eyes -->
            <circle cx="10" cy="10" r="1.2" fill="{colors["white"]}"/>
            <circle cx="14" cy="10" r="1.2" fill="{colors["white"]}"/>
            <circle cx="10" cy="10" r="0.7" fill="{eye_color}"/>
            <circle cx="14" cy="10" r="0.7" fill="{eye_color}"/>
            
            <!-- Mouth -->
            <ellipse cx="12" cy="14" rx="1.5" ry="0.8" fill="{mouth_color}"/>
            
            <!-- Fins -->
            <ellipse cx="6" cy="14" rx="1" ry="2" fill="{fin_color}" transform="rotate(-20 6 14)"/>
            <ellipse cx="18" cy="14" rx="1" ry="2" fill="{fin_color}" transform="rotate(20 18 14)"/>
            
            <!-- Tail -->
            <polygon points="19,12 22,10 22,14" fill="{fin_color}"/>
        </svg>'''
    
    def _beastie_daemon(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate Beastie the BSD daemon (FreeBSD mascot)
        @param size: Icon size
        @param colors: Color scheme  
        @return SVG content
        """
        # Use multiple themed colors for contrast
        body_color = colors["primary"]      # Main body (red/orange)
        horn_color = colors["dark"]         # Horns (dark)
        eye_color = colors["white"]         # Eyes (white)
        pupil_color = colors["dark"]        # Pupils (dark)
        trident_color = colors["accent"]    # Trident (metallic)
        smile_color = colors["orange"]      # Smile (warm)
        
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Beastie the BSD Daemon - FreeBSD Mascot -->
            <!-- Head -->
            <circle cx="12" cy="10" r="5" fill="{body_color}"/>
            
            <!-- Horns -->
            <polygon points="9,6 8,4 10,5" fill="{horn_color}"/>
            <polygon points="15,6 16,4 14,5" fill="{horn_color}"/>
            
            <!-- Eyes -->
            <circle cx="10.5" cy="9" r="1" fill="{eye_color}"/>
            <circle cx="13.5" cy="9" r="1" fill="{eye_color}"/>
            <circle cx="10.5" cy="9" r="0.5" fill="{pupil_color}"/>
            <circle cx="13.5" cy="9" r="0.5" fill="{pupil_color}"/>
            
            <!-- Smile -->
            <path d="M 9.5 11.5 Q 12 13 14.5 11.5" stroke="{smile_color}" stroke-width="0.8" fill="none"/>
            
            <!-- Body -->
            <ellipse cx="12" cy="17" rx="4" ry="4.5" fill="{body_color}"/>
            
            <!-- Arms -->
            <ellipse cx="8" cy="15" rx="1" ry="2.5" fill="{body_color}"/>
            <ellipse cx="16" cy="15" rx="1" ry="2.5" fill="{body_color}"/>
            
            <!-- Trident (metallic) -->
            <rect x="11.7" y="19" width="0.6" height="3" fill="{trident_color}"/>
            <polygon points="11,19 12,18 13,19" fill="{trident_color}"/>
            
            <!-- Tail -->
            <path d="M 12 20 Q 14 21 15 19" stroke="{colors["secondary"]}" stroke-width="1" fill="none"/>
        </svg>'''
    
    def _netbsd_flag(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate NetBSD flag logo
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Use multiple themed colors for the flag
        pole_color = colors["dark"]         # Flagpole (dark)
        flag_primary = colors["primary"]    # Main flag color
        flag_accent = colors["accent"]      # Flag accent/stripes
        flag_highlight = colors["white"]    # Flag highlights
        
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- NetBSD Flag Logo -->
            <!-- Flagpole -->
            <rect x="4" y="4" width="1.5" height="16" fill="{pole_color}"/>
            
            <!-- Main flag -->
            <polygon points="5.5,4 5.5,14 18,9" fill="{flag_primary}"/>
            
            <!-- Flag stripes/pattern -->
            <rect x="6.5" y="5.5" width="8" height="0.8" fill="{flag_accent}"/>
            <rect x="6.5" y="7.2" width="6.5" height="0.8" fill="{flag_highlight}"/>
            <rect x="6.5" y="8.9" width="5" height="0.8" fill="{flag_accent}"/>
            <rect x="6.5" y="10.6" width="3.5" height="0.8" fill="{flag_highlight}"/>
            <rect x="6.5" y="12.3" width="2" height="0.8" fill="{flag_accent}"/>
            
            <!-- Flag border -->
            <polygon points="5.5,4 5.5,14 18,9" fill="none" stroke="{colors["dark"]}" stroke-width="0.3"/>
        </svg>'''
    
    def _apple_logo(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate Apple logo (macOS mascot)
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Use multiple themed colors for the Apple logo
        apple_body = colors["primary"]      # Main apple body
        apple_leaf = colors["accent"]       # Leaf (green-ish)
        apple_highlight = colors["white"]   # Highlight
        bite_color = colors["background"]   # Bite mark (background color)
        
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Apple Logo - macOS -->
            <!-- Apple body with gradient effect -->
            <path d="M 12 20 C 8 20 6 17 6 14 C 6 11 8 9 11 9 C 11.5 9 12 9.1 12.5 9.2 C 13 9.1 13.5 9 14 9 C 17 9 19 11 19 14 C 19 17 17 20 14 20 C 13.5 20 13 19.8 12.5 19.6 C 13 19.8 12.5 20 12 20 Z" fill="{apple_body}"/>
            
            <!-- Apple highlight -->
            <ellipse cx="11" cy="12" rx="1.5" ry="3" fill="{apple_highlight}" opacity="0.3"/>
            
            <!-- Leaf -->
            <ellipse cx="14.5" cy="7" rx="1.5" ry="2.5" fill="{apple_leaf}" transform="rotate(30 14.5 7)"/>
            
            <!-- Leaf detail -->
            <path d="M 14 7.5 Q 15 6.5 15.5 8" stroke="{colors["dark"]}" stroke-width="0.3" fill="none"/>
            
            <!-- Bite mark -->
            <circle cx="16" cy="13" r="2" fill="{bite_color}"/>
            
            <!-- Bite shadow -->
            <circle cx="16.2" cy="13.2" r="1.8" fill="{colors["dark"]}" opacity="0.1"/>
        </svg>'''
    
    def _windows_logo(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate Windows logo
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Use multiple themed colors for the Windows logo (classic four-color design)
        blue_pane = colors["primary"]       # Top-left (blue)
        green_pane = colors["accent"]       # Top-right (green) 
        yellow_pane = colors["orange"]      # Bottom-left (yellow/orange)
        red_pane = colors["secondary"]      # Bottom-right (red)
        
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Windows Logo - Classic Four Panes -->
            <!-- Top-left pane (blue) -->
            <rect x="5" y="5" width="6.5" height="6.5" fill="{blue_pane}"/>
            
            <!-- Top-right pane (green) -->
            <rect x="12.5" y="5" width="6.5" height="6.5" fill="{green_pane}"/>
            
            <!-- Bottom-left pane (yellow) -->
            <rect x="5" y="12.5" width="6.5" height="6.5" fill="{yellow_pane}"/>
            
            <!-- Bottom-right pane (red) -->
            <rect x="12.5" y="12.5" width="6.5" height="6.5" fill="{red_pane}"/>
            
            <!-- Subtle borders for definition -->
            <rect x="5" y="5" width="14" height="14" fill="none" stroke="{colors["dark"]}" stroke-width="0.2"/>
            <line x1="12" y1="5" x2="12" y2="19" stroke="{colors["dark"]}" stroke-width="0.2"/>
            <line x1="5" y1="12" x2="19" y2="12" stroke="{colors["dark"]}" stroke-width="0.2"/>
        </svg>'''
    
    def _generic_computer(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate generic computer icon fallback
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Use multiple themed colors for the computer
        monitor_frame = colors["dark"]        # Monitor frame (dark)
        monitor_screen = colors["primary"]    # Screen (main color)
        screen_glow = colors["accent"]        # Screen glow/activity
        stand_color = colors["secondary"]     # Monitor stand
        base_color = colors["highlight"]      # Base
        
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Generic Computer Monitor -->
            <!-- Monitor frame -->
            <rect x="4" y="6" width="16" height="10" rx="1" fill="{monitor_frame}"/>
            
            <!-- Screen -->
            <rect x="5" y="7" width="14" height="8" fill="{monitor_screen}"/>
            
            <!-- Screen activity/glow -->
            <rect x="6" y="8" width="12" height="2" fill="{screen_glow}" opacity="0.6"/>
            <rect x="6" y="11" width="8" height="1" fill="{screen_glow}" opacity="0.4"/>
            <rect x="6" y="13" width="6" height="1" fill="{screen_glow}" opacity="0.3"/>
            
            <!-- Monitor stand -->
            <rect x="10" y="16" width="4" height="2" fill="{stand_color}"/>
            
            <!-- Base -->
            <ellipse cx="12" cy="18.5" rx="4" ry="0.5" fill="{base_color}"/>
            
            <!-- Power indicator -->
            <circle cx="18" cy="15" r="0.5" fill="{colors["orange"]}"/>
        </svg>'''


def get_platform_mascot_icon(color_manager: Any = None, size: int = 24) -> str:
    """
    @brief Get the platform-specific mascot icon for the current system
    @param color_manager: Optional color manager for theming  
    @param size: Icon size in pixels
    @return SVG content as string
    """
    generator = PlatformMascotGenerator(color_manager)
    return generator.get_platform_mascot(size)
