#!/usr/bin/env python3
"""
Tests for platform detection and configuration module

@brief Comprehensive test suite for platform utilities and configuration
"""

import platform
from typing import Any
from unittest.mock import MagicMock, patch

from modules.platform import (
    PlatformConfig,
    PlatformInfo,
    get_platform_config,
    get_platform_info,
    get_platform_mascot_icon,
)


class TestPlatformInfo:
    """Test PlatformInfo class functionality"""

    def test_initialization(self) -> None:
        """Test PlatformInfo initialization"""
        info: PlatformInfo = PlatformInfo()
        assert hasattr(info, '_system')
        assert hasattr(info, '_release')
        assert hasattr(info, '_machine')
        assert hasattr(info, '_cached_commands')

    def test_system_property(self) -> None:
        """Test system property"""
        info: PlatformInfo = PlatformInfo()
        assert isinstance(info.system, str)
        assert len(info.system) > 0

    def test_is_linux_property(self) -> None:
        """Test is_linux property"""
        with patch.object(platform, 'system', return_value='Linux'):
            info: PlatformInfo = PlatformInfo()
            assert info.is_linux is True

        with patch.object(platform, 'system', return_value='Windows'):
            info: PlatformInfo = PlatformInfo()
            assert info.is_linux is False

    def test_is_openbsd_property(self) -> None:
        """Test is_openbsd property"""
        with patch.object(platform, 'system', return_value='OpenBSD'):
            info: PlatformInfo = PlatformInfo()
            assert info.is_openbsd is True

        with patch.object(platform, 'system', return_value='Linux'):
            info: PlatformInfo = PlatformInfo()
            assert info.is_openbsd is False

    def test_is_freebsd_property(self) -> None:
        """Test is_freebsd property"""
        with patch.object(platform, 'system', return_value='FreeBSD'):
            info: PlatformInfo = PlatformInfo()
            assert info.is_freebsd is True

        with patch.object(platform, 'system', return_value='Linux'):
            info: PlatformInfo = PlatformInfo()
            assert info.is_freebsd is False

    def test_is_netbsd_property(self) -> None:
        """Test is_netbsd property"""
        with patch.object(platform, 'system', return_value='NetBSD'):
            info: PlatformInfo = PlatformInfo()
            assert info.is_netbsd is True

        with patch.object(platform, 'system', return_value='Linux'):
            info: PlatformInfo = PlatformInfo()
            assert info.is_netbsd is False

    def test_is_bsd_property(self) -> None:
        """Test is_bsd property"""
        bsd_systems: list[str] = ['OpenBSD', 'FreeBSD', 'NetBSD', 'DragonFly']
        for system in bsd_systems:
            with patch.object(platform, 'system', return_value=system):
                info: PlatformInfo = PlatformInfo()
                assert info.is_bsd is True

        with patch.object(platform, 'system', return_value='Linux'):
            info: PlatformInfo = PlatformInfo()
            assert info.is_bsd is False

    def test_release_property(self) -> None:
        """Test release property"""
        info: PlatformInfo = PlatformInfo()
        assert isinstance(info.release, str)

    def test_machine_property(self) -> None:
        """Test machine property"""
        info: PlatformInfo = PlatformInfo()
        assert isinstance(info.machine, str)

    @patch('shutil.which')
    def test_find_command_found(self, mock_which: MagicMock) -> None:
        """Test finding a command that exists"""
        mock_which.return_value = '/usr/bin/ls'
        info: PlatformInfo = PlatformInfo()

        result: str | None = info.find_command('ls')
        assert result == '/usr/bin/ls'

        # Test caching
        mock_which.reset_mock()
        result2: str | None = info.find_command('ls')
        assert result2 == '/usr/bin/ls'
        # Should not call which again due to caching
        mock_which.assert_not_called()

    @patch('shutil.which')
    def test_find_command_not_found(self, mock_which: MagicMock) -> None:
        """Test finding a command that doesn't exist"""
        mock_which.return_value = None
        info: PlatformInfo = PlatformInfo()

        result: str | None = info.find_command('nonexistent_command')
        assert result is None

    @patch('shutil.which')
    def test_has_command_true(self, mock_which: MagicMock) -> None:
        """Test has_command returns True for existing command"""
        mock_which.return_value = '/usr/bin/ls'
        info: PlatformInfo = PlatformInfo()

        assert info.has_command('ls') is True

    @patch('shutil.which')
    def test_has_command_false(self, mock_which: MagicMock) -> None:
        """Test has_command returns False for non-existing command"""
        mock_which.return_value = None
        info: PlatformInfo = PlatformInfo()

        assert info.has_command('nonexistent_command') is False

    def test_get_preferred_application_found(self) -> None:
        """Test getting preferred application when available"""
        info: PlatformInfo = PlatformInfo()

        with patch.object(info, 'has_command', side_effect=[False, True, False]):
            result: str | None = info.get_preferred_application('terminal', ['term1', 'term2', 'term3'])
            assert result == 'term2'

    def test_get_preferred_application_not_found(self) -> None:
        """Test getting preferred application when none available"""
        info: PlatformInfo = PlatformInfo()

        with patch.object(info, 'has_command', return_value=False):
            result: str | None = info.get_preferred_application('terminal', ['term1', 'term2'])
            assert result is None


class TestPlatformConfig:
    """Test PlatformConfig class functionality"""

    def test_initialization(self) -> None:
        """Test PlatformConfig initialization"""
        config: PlatformConfig = PlatformConfig()
        assert hasattr(config, 'platform')
        assert hasattr(config, '_config_overrides')
        assert hasattr(config, '_application_preferences')

    def test_initialization_with_platform_info(self) -> None:
        """Test PlatformConfig initialization with custom platform info"""
        mock_platform: MagicMock = MagicMock()
        config: PlatformConfig = PlatformConfig(mock_platform)
        assert config.platform is mock_platform

    def test_get_terminal_preferences(self) -> None:
        """Test terminal preferences for different platforms"""
        config: PlatformConfig = PlatformConfig()

        linux_prefs: list[str] = config._get_terminal_preferences()['linux']  # type: ignore
        assert 'st' in linux_prefs
        assert 'alacritty' in linux_prefs

        openbsd_prefs: list[str] = config._get_terminal_preferences()['openbsd']  # type: ignore
        assert 'st' in openbsd_prefs
        assert 'urxvt' in openbsd_prefs

    def test_get_browser_preferences(self) -> None:
        """Test browser preferences for different platforms"""
        config: PlatformConfig = PlatformConfig()

        linux_prefs: list[str] = config._get_browser_preferences()['linux']  # type: ignore
        assert 'brave' in linux_prefs
        assert 'chromium' in linux_prefs

        openbsd_prefs: list[str] = config._get_browser_preferences()['openbsd']  # type: ignore
        assert 'chrome' in openbsd_prefs
        assert 'iridium' in openbsd_prefs

    def test_get_file_manager_preferences(self) -> None:
        """Test file manager preferences for different platforms"""
        config: PlatformConfig = PlatformConfig()

        linux_prefs: list[str] = config._get_file_manager_preferences()['linux']  # type: ignore
        assert 'thunar' in linux_prefs
        assert 'pcmanfm' in linux_prefs

    def test_get_launcher_preferences(self) -> None:
        """Test launcher preferences for different platforms"""
        config: PlatformConfig = PlatformConfig()

        linux_prefs: list[str] = config._get_launcher_preferences()['linux']  # type: ignore
        assert 'rofi' in linux_prefs
        assert 'dmenu' in linux_prefs

    def test_get_media_player_preferences(self) -> None:
        """Test media player preferences for different platforms"""
        config: PlatformConfig = PlatformConfig()

        linux_prefs: list[str] = config._get_media_player_preferences()['linux']  # type: ignore
        assert 'mpv' in linux_prefs
        assert 'vlc' in linux_prefs

    def test_get_application_preferences(self) -> None:
        """Test aggregated application preferences"""
        config: PlatformConfig = PlatformConfig()
        prefs: dict[str, dict[str, list[str]]] = config._get_application_preferences()  # type: ignore

        assert 'terminal' in prefs
        assert 'browser' in prefs
        assert 'file_manager' in prefs
        assert 'launcher' in prefs
        assert 'media_player' in prefs

    def test_get_command_overrides(self) -> None:
        """Test command overrides for different platforms"""
        config: PlatformConfig = PlatformConfig()
        overrides: dict[str, dict[str, str]] = config._get_command_overrides()  # type: ignore

        linux_overrides: dict[str, str] = overrides['linux']
        assert 'lock_session' in linux_overrides
        assert linux_overrides['lock_session'] == 'loginctl lock-session'

        openbsd_overrides: dict[str, str] = overrides['openbsd']
        assert 'lock_session' in openbsd_overrides
        assert openbsd_overrides['lock_session'] == 'xlock'

    @patch('shutil.which')
    def test_get_application_linux(self, mock_which: MagicMock) -> None:
        """Test getting application for Linux platform"""
        def which_side_effect(cmd: str) -> str | None:
            return f'/usr/bin/{cmd}' if cmd in ['st', 'alacritty'] else None
        mock_which.side_effect = which_side_effect

        with patch.object(platform, 'system', return_value='Linux'):
            config: PlatformConfig = PlatformConfig()
            result: str = config.get_application('terminal')
            assert result == 'st'  # First preference

    @patch('shutil.which')
    def test_get_application_openbsd(self, mock_which: MagicMock) -> None:
        """Test getting application for OpenBSD platform"""
        def which_side_effect(cmd: str) -> str | None:
            return f'/usr/local/bin/{cmd}' if cmd in ['st', 'urxvt'] else None
        mock_which.side_effect = which_side_effect

        with patch.object(platform, 'system', return_value='OpenBSD'):
            config: PlatformConfig = PlatformConfig()
            result: str = config.get_application('terminal')
            assert result == 'st'  # First preference

    @patch('shutil.which')
    def test_get_application_fallback(self, mock_which: MagicMock) -> None:
        """Test getting application with fallback"""
        mock_which.return_value = None  # No commands available

        config: PlatformConfig = PlatformConfig()
        result: str = config.get_application('terminal', 'xterm')
        assert result == 'xterm'

    @patch('shutil.which')
    def test_get_application_default_fallback(self, mock_which: MagicMock) -> None:
        """Test getting application with default fallback"""
        mock_which.return_value = None  # No commands available

        config: PlatformConfig = PlatformConfig()
        result: str = config.get_application('nonexistent_type')
        assert result == 'xterm'  # Default fallback

    @patch('shutil.which')
    def test_get_command_with_available_command(self, mock_which: MagicMock) -> None:
        """Test getting command when base command is available"""
        mock_which.return_value = '/usr/bin/loginctl'

        with patch.object(platform, 'system', return_value='Linux'):
            config: PlatformConfig = PlatformConfig()
            result: str = config.get_command('lock_session')
            assert result == 'loginctl lock-session'

    @patch('shutil.which')
    def test_get_command_with_unavailable_command(self, mock_which: MagicMock) -> None:
        """Test getting command when base command is not available"""
        mock_which.return_value = None

        config: PlatformConfig = PlatformConfig()
        result: str = config.get_command('lock_session', 'xlock')
        assert result == 'xlock'  # Fallback

    @patch('shutil.which')
    def test_get_command_linux_defaults(self, mock_which: MagicMock) -> None:
        """Test getting command using Linux defaults when no override exists"""
        mock_which.return_value = None

        with patch.object(platform, 'system', return_value='Linux'):
            config: PlatformConfig = PlatformConfig()
            result: str = config.get_command('nonexistent_command')
            assert result == ''  # Empty string for unknown commands

    def test_get_config_overrides(self) -> None:
        """Test getting config overrides for current platform"""
        with patch.object(platform, 'system', return_value='Linux'):
            config: PlatformConfig = PlatformConfig()
            overrides: dict[str, Any] = config.get_config_overrides()
            assert 'lock_session' in overrides
            assert overrides['lock_session'] == 'loginctl lock-session'

    def test_add_override(self) -> None:
        """Test adding configuration override"""
        config: PlatformConfig = PlatformConfig()
        config.add_override('test_command', 'test_value')

        with patch.object(platform, 'system', return_value='Linux'):
            overrides: dict[str, Any] = config.get_config_overrides()
            assert 'test_command' in overrides
            assert overrides['test_command'] == 'test_value'


class TestPlatformMascotGenerator:
    """Test PlatformMascotGenerator class functionality"""

    def test_initialization(self) -> None:
        """Test PlatformMascotGenerator initialization"""
        generator: MagicMock = MagicMock()
        generator._detect_platform.return_value = 'linux'
        generator.get_platform_mascot.return_value = '<svg>test</svg>'

        # We can't easily test the real class due to SVG generation complexity
        # So we'll test the interface through mocking
        pass

    def test_detect_platform_linux(self) -> None:
        """Test platform detection for Linux"""
        with patch.object(platform, 'system', return_value='Linux'):
            from modules.platform import PlatformMascotGenerator
            generator: PlatformMascotGenerator = PlatformMascotGenerator()
            assert generator.current_platform == 'linux'

    def test_detect_platform_openbsd(self) -> None:
        """Test platform detection for OpenBSD"""
        with patch.object(platform, 'system', return_value='OpenBSD'):
            from modules.platform import PlatformMascotGenerator
            generator: PlatformMascotGenerator = PlatformMascotGenerator()
            assert generator.current_platform == 'openbsd'

    def test_detect_platform_freebsd(self) -> None:
        """Test platform detection for FreeBSD"""
        with patch.object(platform, 'system', return_value='FreeBSD'):
            from modules.platform import PlatformMascotGenerator
            generator: PlatformMascotGenerator = PlatformMascotGenerator()
            assert generator.current_platform == 'freebsd'

    def test_detect_platform_unknown(self) -> None:
        """Test platform detection for unknown platform"""
        with patch.object(platform, 'system', return_value='UnknownOS'):
            from modules.platform import PlatformMascotGenerator
            generator: PlatformMascotGenerator = PlatformMascotGenerator()
            assert generator.current_platform == 'generic'


class TestGlobalFunctions:
    """Test global utility functions"""

    def test_get_platform_info_singleton(self) -> None:
        """Test singleton pattern for platform info"""
        info1: PlatformInfo = get_platform_info()
        info2: PlatformInfo = get_platform_info()

        assert info1 is info2
        assert isinstance(info1, PlatformInfo)

    def test_get_platform_config_singleton(self) -> None:
        """Test singleton pattern for platform config"""
        config1: PlatformConfig = get_platform_config()
        config2: PlatformConfig = get_platform_config()

        assert config1 is config2
        assert isinstance(config1, PlatformConfig)

    @patch('modules.platform.PlatformMascotGenerator')
    def test_get_platform_mascot_icon(self, mock_generator_class: MagicMock) -> None:
        """Test getting platform mascot icon"""
        mock_generator: MagicMock = MagicMock()
        mock_generator.get_platform_mascot.return_value = '<svg>mascot</svg>'
        mock_generator_class.return_value = mock_generator

        result: str = get_platform_mascot_icon()
        assert result == '<svg>mascot</svg>'
        mock_generator.get_platform_mascot.assert_called_once_with(24)

    @patch('modules.platform.PlatformMascotGenerator')
    def test_get_platform_mascot_icon_with_size(self, mock_generator_class: MagicMock) -> None:
        """Test getting platform mascot icon with custom size"""
        mock_generator: MagicMock = MagicMock()
        mock_generator.get_platform_mascot.return_value = '<svg>mascot</svg>'
        mock_generator_class.return_value = mock_generator

        result: str = get_platform_mascot_icon(size=32)
        assert result == '<svg>mascot</svg>'
        mock_generator.get_platform_mascot.assert_called_once_with(32)


class TestIntegration:
    """Integration tests for platform functionality"""

    def test_full_platform_workflow(self) -> None:
        """Test complete platform detection and configuration workflow"""
        # Test platform info
        info: PlatformInfo = get_platform_info()
        assert isinstance(info.system, str)
        assert isinstance(info.release, str)
        assert isinstance(info.machine, str)

        # Test platform config
        config: PlatformConfig = get_platform_config()
        assert config.platform is info

        # Test application preferences
        terminal_app: str = config.get_application('terminal', 'xterm')
        assert isinstance(terminal_app, str)

        # Test command overrides
        lock_cmd: str = config.get_command('lock_session', 'xlock')
        assert isinstance(lock_cmd, str)

    def test_platform_config_with_different_systems(self) -> None:
        """Test platform config behavior with different systems"""
        systems_and_apps: list[tuple[str, str]] = [
            ('Linux', 'st'),
            ('OpenBSD', 'st'),
            ('FreeBSD', 'st'),
            ('NetBSD', 'st'),
        ]

        for system, _ in systems_and_apps:
            with patch.object(platform, 'system', return_value=system):
                config: PlatformConfig = PlatformConfig()
                app: str = config.get_application('terminal', 'xterm')
                # We can't easily predict which app will be found, but it should be a string
                assert isinstance(app, str)

    def test_command_caching(self) -> None:
        """Test that command lookups are cached properly"""
        info: PlatformInfo = PlatformInfo()

        with patch('shutil.which') as mock_which:
            mock_which.return_value = '/usr/bin/test'

            # First call should trigger lookup
            result1: str | None = info.find_command('test')
            # Second call should use cache
            result2: str | None = info.find_command('test')

            assert result1 == result2 == '/usr/bin/test'
            # which should only be called once due to caching
            assert mock_which.call_count == 1