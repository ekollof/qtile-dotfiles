#!/usr/bin/env python3
"""
Tests for groups module

@brief Basic test suite for the groups module
"""

from unittest.mock import MagicMock, patch

from modules.groups import create_group_manager


class TestGroupsModule:
    """Test groups module functionality"""

    def test_create_group_manager_function_exists(self) -> None:
        """Test that create_group_manager function exists and is callable"""
        assert callable(create_group_manager)

    def test_create_group_manager_with_config(self) -> None:
        """Test creating group manager with a config"""
        mock_config = MagicMock()
        mock_config.groups = [("1", {}), ("2", {})]
        mock_config.floating_rules = []
        mock_color_manager = MagicMock()
        
        with patch('modules.groups.get_config', return_value=mock_config):
            group_manager = create_group_manager(mock_color_manager)
            assert group_manager is not None

    def test_create_group_manager_returns_object(self) -> None:
        """Test that create_group_manager returns a valid object"""
        mock_config = MagicMock()
        mock_config.groups = [("web", {}), ("term", {})]
        mock_config.floating_rules = []
        mock_color_manager = MagicMock()
        
        with patch('modules.groups.get_config', return_value=mock_config):
            group_manager = create_group_manager(mock_color_manager)
            # Should return some kind of object/manager
            assert group_manager is not None