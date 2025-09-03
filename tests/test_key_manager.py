#!/usr/bin/env python3
"""
Tests for key_manager module

@brief Basic test suite for the key_manager module
"""

from unittest.mock import MagicMock, patch

import pytest

from modules.key_manager import KeyManager


class TestKeyManager:
    """Test KeyManager functionality"""

    @pytest.fixture
    def key_manager(self) -> KeyManager:
        """Create KeyManager instance for testing"""
        mock_color_manager = MagicMock()
        with patch('modules.key_manager.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.mod_key = "mod4"
            mock_config.alt_key = "mod1"
            mock_config.terminal = "alacritty"
            mock_config.browser = "firefox"
            mock_config.applications = {
                "launcher": "dmenu_run",
                "password_manager": "keepassxc",
                "totp_manager": "otpapp",
                "clipboard": "clipmenu",
                "wallpaper_picker": "wallpaper",
                "lock_session": "slock",
                "wallpaper_random": "wallpaper-random"
            }
            mock_get_config.return_value = mock_config
            return KeyManager(mock_color_manager)

    def test_initialization(self, key_manager: KeyManager) -> None:
        """Test KeyManager initialization"""
        assert hasattr(key_manager, 'color_manager')
        assert hasattr(key_manager, 'config')
        assert hasattr(key_manager, 'layout_commands')
        assert hasattr(key_manager, 'window_commands')
        assert hasattr(key_manager, 'system_commands')

    def test_get_keys_method_exists(self, key_manager: KeyManager) -> None:
        """Test that get_keys method exists and returns a list"""
        keys = key_manager.get_keys()
        assert isinstance(keys, list)

    def test_get_keys_by_category_method_exists(self, key_manager: KeyManager) -> None:
        """Test that get_keys_by_category method exists and returns a dict"""
        keys_by_category = key_manager.get_keys_by_category()
        assert isinstance(keys_by_category, dict)

    def test_methods_are_callable(self, key_manager: KeyManager) -> None:
        """Test that key manager methods are callable"""
        assert callable(getattr(key_manager, 'get_keys'))
        assert callable(getattr(key_manager, 'get_keys_by_category'))

    def test_key_creation_doesnt_error(self, key_manager: KeyManager) -> None:
        """Test that key creation methods don't raise exceptions"""
        # This should not raise an exception
        keys = key_manager.get_keys()
        keys_by_category = key_manager.get_keys_by_category()
        
        # Basic sanity checks
        assert isinstance(keys, list)
        assert isinstance(keys_by_category, dict)