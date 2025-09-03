#!/usr/bin/env python3
"""
Tests for dependency_container module

@brief Basic test suite for the dependency_container module
"""

from unittest.mock import MagicMock

from modules.dependency_container import ManagerDependencies


class TestManagerDependencies:
    """Test ManagerDependencies functionality"""

    def test_initialization(self) -> None:
        """Test ManagerDependencies initialization"""
        mock_color_manager = MagicMock()
        mock_dpi_manager = MagicMock()
        mock_platform_config = MagicMock()
        mock_config = MagicMock()
        
        deps = ManagerDependencies(
            color_manager=mock_color_manager,
            dpi_manager=mock_dpi_manager,
            platform_config=mock_platform_config,
            config=mock_config
        )
        
        assert deps.color_manager == mock_color_manager
        assert deps.dpi_manager == mock_dpi_manager
        assert deps.platform_config == mock_platform_config
        assert deps.config == mock_config

    def test_has_required_attributes(self) -> None:
        """Test that all required attributes are present"""
        mock_color_manager = MagicMock()
        mock_dpi_manager = MagicMock()
        mock_platform_config = MagicMock()
        mock_config = MagicMock()
        
        deps = ManagerDependencies(
            color_manager=mock_color_manager,
            dpi_manager=mock_dpi_manager,
            platform_config=mock_platform_config,
            config=mock_config
        )
        
        # Check that all expected attributes exist
        assert hasattr(deps, 'color_manager')
        assert hasattr(deps, 'dpi_manager')
        assert hasattr(deps, 'platform_config')
        assert hasattr(deps, 'config')

    def test_dependency_types(self) -> None:
        """Test dependency types are maintained"""
        mock_color_manager = MagicMock()
        mock_dpi_manager = MagicMock()
        mock_platform_config = MagicMock()
        mock_config = MagicMock()
        
        deps = ManagerDependencies(
            color_manager=mock_color_manager,
            dpi_manager=mock_dpi_manager,
            platform_config=mock_platform_config,
            config=mock_config
        )
        
        # Should not modify the dependencies
        assert type(deps.color_manager) == type(mock_color_manager)
        assert type(deps.dpi_manager) == type(mock_dpi_manager)
        assert type(deps.platform_config) == type(mock_platform_config)
        assert type(deps.config) == type(mock_config)