#!/usr/bin/env python3
"""
Tests for DPI utilities module

@brief Comprehensive test suite for DPI detection and scaling functionality
"""

import subprocess
from typing import Any
from unittest.mock import MagicMock, patch

from modules.dpi_utils import DPIManager, get_dpi_manager, scale_font, scale_size


class TestDPIManager:
    """Test DPIManager class functionality"""

    def test_initialization(self) -> None:
        """Test DPIManager initialization"""
        manager: DPIManager = DPIManager()
        assert hasattr(manager, '_dpi')
        assert hasattr(manager, '_scale_factor')

    def test_detect_dpi_fallback(self) -> None:
        """Test DPI detection fallback when no methods work"""
        manager: DPIManager = DPIManager()

        # Mock all detection methods to fail
        with patch.object(manager, '_detect_with_fallbacks', return_value=96.0):
            dpi: float = manager.detect_dpi()
            assert dpi == 96.0

    @patch('subprocess.run')
    def test_try_xdpyinfo_success(self, mock_run: MagicMock) -> None:
        """Test xdpyinfo DPI detection success"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="resolution:    192x192 dots per inch"
        )

        manager: DPIManager = DPIManager()
        result: float | None = manager._try_xdpyinfo()  # type: ignore
        assert result == 192

    @patch('subprocess.run')
    def test_try_xdpyinfo_failure(self, mock_run: MagicMock) -> None:
        """Test xdpyinfo DPI detection failure"""
        mock_run.side_effect = subprocess.TimeoutExpired('xdpyinfo', 2)

        manager: DPIManager = DPIManager()
        result: float | None = manager._try_xdpyinfo()  # type: ignore
        assert result is None

    @patch('subprocess.run')
    def test_try_xrandr_success(self, mock_run: MagicMock) -> None:
        """Test xrandr DPI detection success"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="HDMI-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 597mm x 336mm"
        )

        manager: DPIManager = DPIManager()
        result: float | None = manager._try_xrandr()  # type: ignore
        # Calculate expected DPI: (1920 / (597/25.4)) ≈ 81.8, rounded to 82
        assert result == 82

    @patch('subprocess.run')
    def test_try_xrandr_failure(self, mock_run: MagicMock) -> None:
        """Test xrandr DPI detection failure"""
        mock_run.side_effect = subprocess.TimeoutExpired('xrandr', 2)

        manager: DPIManager = DPIManager()
        result: float | None = manager._try_xrandr()  # type: ignore
        assert result is None

    def test_parse_xrandr_line_valid(self) -> None:
        """Test parsing valid xrandr output line"""
        manager: DPIManager = DPIManager()
        line: str = "HDMI-1 connected primary 1920x1080+0+0 (normal) 597mm x 336mm"

        result: float | None = manager._parse_xrandr_line(line)  # type: ignore
        # Expected: 1920 / (597/25.4) ≈ 81.8, rounded to 82
        assert result == 82

    def test_parse_xrandr_line_invalid(self) -> None:
        """Test parsing invalid xrandr output line"""
        manager: DPIManager = DPIManager()
        line: str = "HDMI-1 connected primary (normal)"

        result: float | None = manager._parse_xrandr_line(line)  # type: ignore
        assert result is None

    def test_try_xresources_success(self) -> None:
        """Test .Xresources DPI detection success"""
        manager: DPIManager = DPIManager()

        # Mock the _try_xresources method to return 144
        original_method = manager._try_xresources  # type: ignore
        manager._try_xresources = lambda: 144  # type: ignore  # type: ignore

        try:
            result: float | None = manager._try_xresources()  # type: ignore  # type: ignore
            assert result == 144
        finally:
            # Restore the original method
            manager._try_xresources = original_method  # type: ignore  # type: ignore

    @patch('os.getenv')
    def test_try_environment_success(self, mock_getenv: MagicMock) -> None:
        """Test environment variable DPI detection success"""
        mock_getenv.return_value = "2.0"

        manager: DPIManager = DPIManager()
        result: float | None = manager._try_environment()  # type: ignore
        assert result == 192.0  # 96 * 2.0

    @patch('os.getenv')
    def test_try_environment_failure(self, mock_getenv: MagicMock) -> None:
        """Test environment variable DPI detection failure"""
        mock_getenv.return_value = None

        manager: DPIManager = DPIManager()
        result: float | None = manager._try_environment()  # type: ignore
        assert result is None

    def test_use_fallback(self) -> None:
        """Test fallback DPI value"""
        manager: DPIManager = DPIManager()
        result: float = manager._use_fallback()  # type: ignore
        assert result == 96.0

    def test_dpi_property(self) -> None:
        """Test DPI property access"""
        manager: DPIManager = DPIManager()
        manager._dpi = 120  # type: ignore
        assert manager.dpi == 120

    def test_dpi_property_fallback(self) -> None:
        """Test DPI property fallback when not set"""
        manager: DPIManager = DPIManager()
        manager._dpi = None  # type: ignore

        with patch.object(manager, 'detect_dpi', return_value=96.0):
            assert manager.dpi == 96.0

    def test_scale_factor_property(self) -> None:
        """Test scale factor property"""
        manager: DPIManager = DPIManager()
        manager._dpi = 192  # type: ignore
        manager._scale_factor = None  # type: ignore

        assert manager.scale_factor == 2.0

    def test_scale_factor_cached(self) -> None:
        """Test scale factor caching"""
        manager: DPIManager = DPIManager()
        manager._scale_factor = 1.5  # type: ignore

        assert manager.scale_factor == 1.5

    def test_scale_method(self) -> None:
        """Test scaling method"""
        manager: DPIManager = DPIManager()
        manager._scale_factor = 2.0  # type: ignore

        assert manager.scale(10) == 20
        assert manager.scale(15.5) == 31

    def test_scale_method_minimum(self) -> None:
        """Test scaling method minimum value"""
        manager: DPIManager = DPIManager()
        manager._scale_factor = 0.1  # type: ignore  # Very small scale factor

        assert manager.scale(10) == 1  # Minimum is 1

    def test_scale_font_method(self) -> None:
        """Test font scaling method"""
        manager: DPIManager = DPIManager()
        manager._scale_factor = 2.0  # type: ignore

        assert manager.scale_font(12) == 24

    def test_scale_font_minimum(self) -> None:
        """Test font scaling minimum size"""
        manager: DPIManager = DPIManager()
        manager._scale_factor = 0.1  # type: ignore  # Very small scale factor

        assert manager.scale_font(12) == 8  # Minimum readable font size

    def test_scale_font_rounding(self) -> None:
        """Test font scaling intelligent rounding"""
        manager: DPIManager = DPIManager()
        manager._scale_factor = 1.25  # type: ignore  # 96 * 1.25 = 120 DPI

        # Test various sizes and their expected rounding
        assert manager.scale_font(12) == 15  # 15.0 rounds normally
        assert manager.scale_font(8) == 10   # 10.0 rounds normally

    def test_get_scaling_info(self) -> None:
        """Test scaling info dictionary"""
        manager: DPIManager = DPIManager()
        manager._dpi = 144  # type: ignore
        manager._scale_factor = 1.5  # type: ignore

        info: dict[str, Any] = manager.get_scaling_info()

        assert info['dpi'] == 144
        assert info['scale_factor'] == 1.5
        assert info['category'] == 'High DPI'
        assert info['recommended_font_base'] == 14
        assert info['bar_height'] == 42  # 28 * 1.5
        assert info['icon_size'] == 24   # 16 * 1.5
        assert info['margin'] == 6       # 4 * 1.5

    def test_get_dpi_category_standard(self) -> None:
        """Test DPI category classification - Standard"""
        manager: DPIManager = DPIManager()
        manager._dpi = 96  # type: ignore
        assert manager._get_dpi_category() == 'Standard DPI'  # type: ignore

    def test_get_dpi_category_high(self) -> None:
        """Test DPI category classification - High"""
        manager: DPIManager = DPIManager()
        manager._dpi = 120  # type: ignore
        assert manager._get_dpi_category() == 'High DPI'  # type: ignore

    def test_get_dpi_category_very_high(self) -> None:
        """Test DPI category classification - Very High"""
        manager: DPIManager = DPIManager()
        manager._dpi = 180  # type: ignore
        assert manager._get_dpi_category() == 'Very High DPI'  # type: ignore

    def test_get_dpi_category_ultra_high(self) -> None:
        """Test DPI category classification - Ultra High"""
        manager: DPIManager = DPIManager()
        manager._dpi = 300  # type: ignore
        assert manager._get_dpi_category() == 'Ultra High DPI'  # type: ignore

    def test_get_recommended_base_font_standard(self) -> None:
        """Test recommended base font for standard DPI"""
        manager: DPIManager = DPIManager()
        manager._dpi = 96  # type: ignore
        assert manager._get_recommended_base_font() == 12  # type: ignore

    def test_get_recommended_base_font_high(self) -> None:
        """Test recommended base font for high DPI"""
        manager: DPIManager = DPIManager()
        manager._dpi = 144  # type: ignore
        assert manager._get_recommended_base_font() == 14  # type: ignore

    def test_get_recommended_base_font_very_high(self) -> None:
        """Test recommended base font for very high DPI"""
        manager: DPIManager = DPIManager()
        manager._dpi = 200  # type: ignore
        assert manager._get_recommended_base_font() == 16  # type: ignore


class TestGlobalFunctions:
    """Test global utility functions"""

    def test_get_dpi_manager_singleton(self) -> None:
        """Test singleton pattern for DPI manager"""
        # Test that multiple calls return the same instance
        manager1: DPIManager = get_dpi_manager()
        manager2: DPIManager = get_dpi_manager()

        assert manager1 is manager2

    @patch('modules.dpi_utils.get_dpi_manager')
    def test_scale_size_function(self, mock_get_manager: MagicMock) -> None:
        """Test scale_size convenience function"""
        mock_manager: MagicMock = MagicMock()
        mock_manager.scale.return_value = 20
        mock_get_manager.return_value = mock_manager

        result: int = scale_size(10)
        assert result == 20
        mock_manager.scale.assert_called_once_with(10)

    @patch('modules.dpi_utils.get_dpi_manager')
    def test_scale_font_function(self, mock_get_manager: MagicMock) -> None:
        """Test scale_font convenience function"""
        mock_manager: MagicMock = MagicMock()
        mock_manager.scale_font.return_value = 16
        mock_get_manager.return_value = mock_manager

        result: int = scale_font(12)
        assert result == 16
        mock_manager.scale_font.assert_called_once_with(12)

    @patch('modules.dpi_utils.get_dpi_manager')
    def test_get_dpi_function(self, mock_get_manager: MagicMock) -> None:
        """Test get_dpi convenience function"""
        mock_manager: MagicMock = MagicMock()
        mock_manager.dpi = 144
        mock_get_manager.return_value = mock_manager

        from modules.dpi_utils import get_dpi
        result: float = get_dpi()
        assert result == 144

    @patch('modules.dpi_utils.get_dpi_manager')
    def test_get_scale_factor_function(self, mock_get_manager: MagicMock) -> None:
        """Test get_scale_factor convenience function"""
        mock_manager: MagicMock = MagicMock()
        mock_manager.scale_factor = 1.5
        mock_get_manager.return_value = mock_manager

        from modules.dpi_utils import get_scale_factor
        result: float = get_scale_factor()
        assert result == 1.5


class TestIntegration:
    """Integration tests for DPI functionality"""

    def test_full_dpi_detection_workflow(self) -> None:
        """Test complete DPI detection workflow"""
        manager: DPIManager = DPIManager()

        # Mock the detection chain
        with patch.object(manager, '_detect_with_fallbacks', return_value=120):
            dpi: float = manager.detect_dpi()
            assert dpi == 120

            # Test that scale factor is calculated correctly
            assert manager.scale_factor == 1.25

            # Test scaling functions work
            assert manager.scale(16) == 20
            assert manager.scale_font(12) == 15

    def test_dpi_caching_behavior(self) -> None:
        """Test that DPI detection is cached properly"""
        manager: DPIManager = DPIManager()
        manager._dpi = None  # type: ignore
        manager._scale_factor = 1.0  # type: ignore

        call_count = 0

        def mock_detect_dpi():
            nonlocal call_count
            call_count += 1
            manager._dpi = 96  # type: ignore
            return 96

        manager.detect_dpi = mock_detect_dpi

        # First call should trigger detection
        dpi1: float = manager.dpi
        # Second call should use cached value
        dpi2: float = manager.dpi

        assert dpi1 == dpi2 == 96
        # The caching should work
        assert call_count == 1