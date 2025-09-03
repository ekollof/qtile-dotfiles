#!/usr/bin/env python3
"""
Tests for config_validator module

@brief Basic test suite for the config_validator module
"""

from unittest.mock import MagicMock

import pytest

from modules.config_validator import ConfigValidator


class TestConfigValidator:
    """Test ConfigValidator functionality"""

    @pytest.fixture
    def config_validator(self) -> ConfigValidator:
        """Create ConfigValidator instance for testing"""
        mock_config = MagicMock()
        return ConfigValidator(mock_config)

    def test_initialization(self, config_validator: ConfigValidator) -> None:
        """Test ConfigValidator initialization"""
        assert hasattr(config_validator, 'config')
        assert hasattr(config_validator, 'validation_results')

    def test_validate_all_basic(self, config_validator: ConfigValidator) -> None:
        """Test basic validation functionality"""
        # This should not raise an exception
        result = config_validator.validate_all()
        assert isinstance(result, dict)
        assert 'valid' in result
        assert 'errors' in result
        assert 'warnings' in result

    def test_validation_results_structure(self, config_validator: ConfigValidator) -> None:
        """Test that validation results have proper structure"""
        results = config_validator.validation_results
        assert isinstance(results, dict)
        assert 'valid' in results
        assert 'errors' in results
        assert 'warnings' in results
        assert 'component_validations' in results

    def test_validation_methods_exist(self, config_validator: ConfigValidator) -> None:
        """Test that validation methods exist and are callable"""
        # These should not raise exceptions
        assert hasattr(config_validator, 'validate_all')
        assert callable(getattr(config_validator, 'validate_all'))

    def test_reset_validation_internal(self, config_validator: ConfigValidator) -> None:
        """Test internal validation reset functionality"""
        # Access private method for testing
        config_validator._reset_validation()  # type: ignore
        results = config_validator.validation_results
        assert results['valid'] is True
        assert len(results['errors']) == 0
        assert len(results['warnings']) == 0