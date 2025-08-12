#!/usr/bin/env python3
"""
Unified bar manager factory for qtile
Provides dynamic selection between standard and enhanced SVG bar managers

@brief Factory module for creating appropriate bar manager based on configuration
@author qtile configuration system
"""

from typing import Any, Union
from libqtile.log_utils import logger

# Import bar managers
from modules.bars import BarManager as StandardBarManager, create_bar_manager as create_standard_bar_manager
from modules.bars_svg import EnhancedBarManager, create_enhanced_bar_manager


class BarManagerFactory:
    """
    @brief Factory class for creating appropriate bar manager instances

    Selects between standard and enhanced SVG bar managers based on
    configuration settings and system capabilities.
    """

    def __init__(self) -> None:
        """
        @brief Initialize bar manager factory
        """
        self._svg_available = self._check_svg_support()

    def _check_svg_support(self) -> bool:
        """
        @brief Check if SVG utilities are available and working
        @return True if SVG support is available
        """
        try:
            from modules.svg_utils import get_svg_utils
            # Try to create SVG utilities to ensure they work
            manipulator, generator = get_svg_utils()
            return manipulator is not None and generator is not None
        except Exception as e:
            logger.warning(f"SVG utilities not available: {e}")
            return False

    def create_bar_manager(self, color_manager: Any, qtile_config: Any) -> Union[StandardBarManager, EnhancedBarManager]:
        """
        @brief Create appropriate bar manager based on configuration
        @param color_manager: Color management instance
        @param qtile_config: Qtile configuration instance
        @return Configured bar manager instance
        """
        # Check if enhanced SVG bar manager is requested and available
        if hasattr(qtile_config, 'use_svg_bar_manager') and qtile_config.use_svg_bar_manager:
            if self._svg_available:
                try:
                    logger.info("Creating enhanced SVG bar manager")
                    manager = create_enhanced_bar_manager(color_manager, qtile_config)

                    # Set icon method if specified in config
                    if hasattr(qtile_config, 'svg_icon_method'):
                        manager.icon_method = qtile_config.svg_icon_method

                    return manager
                except Exception as e:
                    logger.error(f"Failed to create enhanced SVG bar manager: {e}")
                    logger.info("Falling back to standard bar manager")
            else:
                logger.warning("SVG support not available, falling back to standard bar manager")

        # Fall back to standard bar manager
        logger.info("Creating standard bar manager")
        return create_standard_bar_manager(color_manager, qtile_config)

    def get_bar_manager_info(self, qtile_config: Any) -> dict[str, Any]:
        """
        @brief Get information about available bar managers
        @param qtile_config: Qtile configuration instance
        @return Dictionary with bar manager information
        """
        info = {
            "svg_support_available": self._svg_available,
            "enhanced_requested": getattr(qtile_config, 'use_svg_bar_manager', False),
            "will_use_enhanced": False,
            "icon_method": "standard",
        }

        if info["enhanced_requested"] and info["svg_support_available"]:
            info["will_use_enhanced"] = True
            info["icon_method"] = getattr(qtile_config, 'svg_icon_method', 'svg_dynamic')

        return info


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


def create_bar_manager(color_manager: Any, qtile_config: Any) -> Union[StandardBarManager, EnhancedBarManager]:
    """
    @brief Unified factory function for creating bar managers
    @param color_manager: Color management instance
    @param qtile_config: Qtile configuration instance
    @return Configured bar manager instance (standard or enhanced)
    """
    factory = get_bar_factory()
    return factory.create_bar_manager(color_manager, qtile_config)


def get_bar_manager_status(qtile_config: Any) -> dict[str, Any]:
    """
    @brief Get status information about bar manager selection
    @param qtile_config: Qtile configuration instance
    @return Dictionary with bar manager status information
    """
    factory = get_bar_factory()
    return factory.get_bar_manager_info(qtile_config)


def force_svg_bar_manager(color_manager: Any, qtile_config: Any) -> EnhancedBarManager:
    """
    @brief Force creation of enhanced SVG bar manager
    @param color_manager: Color management instance
    @param qtile_config: Qtile configuration instance
    @return Enhanced bar manager instance
    @throws Exception if SVG support is not available
    """
    factory = get_bar_factory()

    if not factory._svg_available:
        raise RuntimeError("SVG support is not available")

    logger.info("Force creating enhanced SVG bar manager")
    manager = create_enhanced_bar_manager(color_manager, qtile_config)

    # Set icon method if specified in config
    if hasattr(qtile_config, 'svg_icon_method'):
        manager.icon_method = qtile_config.svg_icon_method

    return manager


def force_standard_bar_manager(color_manager: Any, qtile_config: Any) -> StandardBarManager:
    """
    @brief Force creation of standard bar manager
    @param color_manager: Color management instance
    @param qtile_config: Qtile configuration instance
    @return Standard bar manager instance
    """
    logger.info("Force creating standard bar manager")
    return create_standard_bar_manager(color_manager, qtile_config)


def update_bar_manager_icons(bar_manager: Union[StandardBarManager, EnhancedBarManager]) -> None:
    """
    @brief Update bar manager icons (for enhanced managers)
    @param bar_manager: Bar manager instance to update
    """
    if isinstance(bar_manager, EnhancedBarManager):
        try:
            bar_manager.update_dynamic_icons()
            logger.info("Updated dynamic icons for enhanced bar manager")
        except Exception as e:
            logger.warning(f"Failed to update dynamic icons: {e}")
    else:
        logger.debug("Icon update not applicable for standard bar manager")


def get_icon_system_status(bar_manager: Union[StandardBarManager, EnhancedBarManager]) -> dict[str, Any]:
    """
    @brief Get icon system status information
    @param bar_manager: Bar manager instance
    @return Dictionary with icon system status
    """
    if isinstance(bar_manager, EnhancedBarManager):
        try:
            return bar_manager.get_icon_status()
        except Exception as e:
            logger.warning(f"Failed to get icon status: {e}")
            return {"error": str(e)}
    else:
        return {
            "type": "standard",
            "icon_method": getattr(bar_manager, 'icon_method', 'unknown'),
            "svg_support": False,
        }
