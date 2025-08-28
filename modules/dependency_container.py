#!/usr/bin/env python3
"""
@brief Dependency injection container for qtile managers
@file dependency_container.py

Centralized dependency injection system for qtile managers and components.

Features:
- Type-safe dependency injection
- Easy testing with mock dependencies
- Clean separation of concerns

@author Qtile configuration system
@note This module follows Python 3.10+ standards and project guidelines
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from modules.color_management import ColorManager
    from modules.dpi_utils import DPIManager
    from modules.platform import PlatformConfig


@dataclass
class ManagerDependencies:
    """
    @brief Container for all manager dependencies

    Centralizes all dependencies required by various managers,
    enabling clean dependency injection and improved testability.
    """

    color_manager: "ColorManager"
    dpi_manager: "DPIManager"
    platform_config: "PlatformConfig"
    config: Any

    def __post_init__(self) -> None:
        """Validate dependencies after initialization"""
        self._validate_dependencies()

    def _validate_dependencies(self) -> None:
        """
        @brief Validate that all required dependencies are present
        @throws ValueError if any required dependency is missing
        """
        required_deps = {
            "color_manager": self.color_manager,
            "dpi_manager": self.dpi_manager,
            "platform_config": self.platform_config,
            "config": self.config,
        }

        missing_deps = [name for name, dep in required_deps.items() if dep is None]

        if missing_deps:
            raise ValueError(
                f"Missing required dependencies: {', '.join(missing_deps)}"
            )


def create_dependency_container(
    color_manager: "ColorManager",
    dpi_manager: "DPIManager",
    platform_config: "PlatformConfig",
    config: Any,
) -> ManagerDependencies:
    """
    @brief Create a dependency container with all required dependencies
    @param color_manager Color manager instance
    @param dpi_manager DPI manager instance
    @param platform_config Platform configuration
    @param config Main qtile configuration
    @return Configured ManagerDependencies instance
    @throws ValueError if any dependency is invalid
    """
    return ManagerDependencies(
        color_manager=color_manager,
        dpi_manager=dpi_manager,
        platform_config=platform_config,
        config=config,
    )


def create_mock_dependencies() -> ManagerDependencies:
    """
    @brief Create mock dependencies for testing
    @return ManagerDependencies with mock implementations
    @note This is primarily for testing purposes
    """
    from unittest.mock import MagicMock

    # Mock color manager
    mock_color_manager = MagicMock()
    mock_color_manager.get_colors.return_value = {
        "special": {"background": "#000000", "foreground": "#ffffff"},
        "colors": {"color0": "#000000", "color1": "#ff0000"},
    }
    mock_color_manager.is_monitoring.return_value = False

    # Mock DPI manager
    mock_dpi_manager = MagicMock()
    mock_dpi_manager.dpi = 96.0
    mock_dpi_manager.scale_size = MagicMock(return_value=lambda x: x)  # type: ignore

    # Mock platform config
    mock_platform_config = MagicMock()
    mock_platform_config.system = "Linux"
    mock_platform_config.is_bsd = False

    return ManagerDependencies(
        color_manager=mock_color_manager,
        dpi_manager=mock_dpi_manager,
        platform_config=mock_platform_config,
        config=MagicMock(),
    )


# Maintain backward compatibility
__all__ = [
    "ManagerDependencies",
    "create_dependency_container",
    "create_mock_dependencies",
]
