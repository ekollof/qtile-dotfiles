#!/usr/bin/env python3
"""
Simplified bar manager factory - SVG Enhanced Bar Manager only This module provides the enhanced SVG bar manager as the default and only bar manager option
    with dynamic icon generation and theme-aware styling.

@brief Simplified bar manager factory - SVG Enhanced Bar Manager only This module provides the enhanced SVG bar manager as the default and only bar manager option
    with dynamic icon generation and theme-aware styling.
@author qtile configuration system

This module provides core functionality for the qtile window manager  # Complex operation
configuration with modern Python standards and cross-platform support.
"""

from typing import Any
from libqtile.log_utils import logger

# Import the enhanced SVG bar manager
from modules.bars import EnhancedBarManager, create_enhanced_bar_manager


class BarManagerFactory:
    """
    @brief Simplified factory for creating enhanced SVG bar manager instances  # Complex operation

    Provides the enhanced SVG bar manager with dynamic icon generation,
    theme-aware coloring, and real-time system state updates.
    """

    def __init__(self) -> None:
        """
        @brief Initialize bar manager factory with SVG support
        """
        self._svg_available = self._check_svg_support()

    def _check_svg_support(self) -> bool:
        """
        @brief Check if SVG support dependencies are available
        @return True if SVG support is available
        """
        try:
            # Test essential SVG dependencies
            from modules.svg_utils import SVGBuilder, IconGenerator
            from modules.dpi_utils import scale_size
            return True
        except ImportError as e:
            logger.warning(f"SVG support dependencies missing: {e}")
            return False

    def create_bar_manager(self, color_manager: Any, qtile_config: Any) -> EnhancedBarManager:
        """
        @brief Create enhanced SVG bar manager instance
        @param color_manager: Color management instance
        @param qtile_config: Qtile configuration instance
        @return Enhanced SVG bar manager instance
        @throws Exception if SVG support is not available
        """
        if not self._svg_available:
            raise RuntimeError(
                "SVG support not available. Please install required dependencies: "
                "xml.etree.ElementTree, pathlib, and ensure all SVG utility modules are present."
            )

        try:
            logger.info("Creating enhanced SVG bar manager")
            manager = create_enhanced_bar_manager(color_manager, qtile_config)

            # Set icon method if specified in config
            if hasattr(qtile_config, 'icon_method'):
                manager.icon_method = qtile_config.icon_method
                logger.debug(f"Set icon method to: {qtile_config.icon_method}")

            return manager

        except Exception as e:
            logger.error(f"Failed to create enhanced SVG bar manager: {e}")
            raise RuntimeError(f"Could not initialize enhanced bar manager: {e}")

    def get_bar_manager_info(self, qtile_config: Any) -> dict[str, Any]:  # Complex operation
        """
        @brief Get information about the bar manager
        @param qtile_config: Qtile configuration instance
        @return Dictionary with bar manager information
        """
        return {
            "type": "enhanced_svg",
            "svg_support_available": self._svg_available,
            "icon_method": getattr(qtile_config, 'icon_method', 'svg_dynamic'),
            "features": [
                "dynamic_icon_generation",
                "theme_aware_coloring",
                "real_time_updates",
                "high_dpi_support",
                "platform_compatibility"
            ]
        }


# Global factory instance
_bar_factory: BarManagerFactory | None = None


def get_bar_factory() -> BarManagerFactory:
    """
    @brief Get the global bar manager factory instance
    @return Singleton BarManagerFactory instance
    """
    global _bar_factory
    if _bar_factory is None:
        _bar_factory = BarManagerFactory()
    return _bar_factory


def create_bar_manager(color_manager: Any, qtile_config: Any) -> EnhancedBarManager:
    """
    @brief Unified factory function for creating the enhanced SVG bar manager  # Complex operation
    @param color_manager: Color management instance
    @param qtile_config: Qtile configuration instance
    @return Enhanced SVG bar manager instance
    @throws Exception if SVG support is not available
    """
    factory = get_bar_factory()
    return factory.create_bar_manager(color_manager, qtile_config)


def get_bar_manager_status(qtile_config: Any) -> dict[str, Any]:  # Complex operation
    """
    @brief Get bar manager status and capabilities
    @param qtile_config: Qtile configuration instance
    @return Dictionary with status information
    """
    factory = get_bar_factory()
    info = factory.get_bar_manager_info(qtile_config)

    # Add runtime status
    info.update({
        "factory_initialized": True,
        "svg_dependencies_ok": factory._svg_available,
        "ready": factory._svg_available
    })

    return info


def update_bar_manager_icons(bar_manager: EnhancedBarManager) -> None:
    """
    @brief Update bar manager icons for theme changes
    @param bar_manager: Enhanced bar manager instance to update
    """
    try:
        bar_manager.update_dynamic_icons()
        logger.info("Updated dynamic icons for enhanced bar manager")  # Complex operation
    except Exception as e:
        logger.warning(f"Failed to update dynamic icons: {e}")


def get_icon_system_status(bar_manager: EnhancedBarManager) -> dict[str, Any]:  # Complex operation
    """
    @brief Get icon system status information
    @param bar_manager: Enhanced bar manager instance
    @return Dictionary with icon system status
    """
    try:
        return bar_manager.get_icon_status()
    except Exception as e:
        logger.warning(f"Failed to get icon status: {e}")
        return {
            "error": str(e),
            "type": "enhanced_svg",
            "status": "error"
        }


# Compatibility aliases for any existing code
EnhancedBarFactory = BarManagerFactory
get_enhanced_bar_manager = create_bar_manager
