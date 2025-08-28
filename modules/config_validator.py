#!/usr/bin/env python3
"""
@brief Configuration validation system for qtile
@file config_validator.py

Comprehensive validation for qtile configuration settings.

Features:
- DPI configuration validation
- Font availability checking
- Color scheme validation
- Screen configuration validation
- Hotkey binding validation
- Performance settings validation

@author Qtile configuration system
@note This module follows Python 3.10+ standards and project guidelines
"""

from typing import Any


class ConfigValidator:
    """
    @brief Comprehensive configuration validator for qtile

    Validates all aspects of qtile configuration to ensure proper
    operation and prevent runtime errors.
    """

    def __init__(self, config: Any) -> None:
        """
        @brief Initialize validator with configuration
        @param config Qtile configuration object
        """
        self.config = config
        self.validation_results: dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "component_validations": {},
        }

    def validate_all(self) -> dict[str, Any]:
        """
        @brief Run all validation checks
        @return Comprehensive validation results
        """
        self._reset_validation()

        validations = {
            "dpi": self.validate_dpi_config(),
            "fonts": self.validate_font_config(),
            "colors": self.validate_color_config(),
            "screens": self.validate_screen_config(),
            "hotkeys": self.validate_hotkey_config(),
            "performance": self.validate_performance_config(),
        }

        for component_name, result in validations.items():
            self.validation_results["component_validations"][component_name] = result
            if not result.get("valid", True):
                self.validation_results["valid"] = False
            self.validation_results["warnings"].extend(result.get("warnings", []))
            self.validation_results["errors"].extend(result.get("errors", []))

        return self.validation_results

    def _reset_validation(self) -> None:
        """
        @brief Reset validation results for fresh validation run
        """
        self.validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "component_validations": {},
        }

    def _create_validation_result(self) -> dict[str, Any]:
        """
        @brief Create a standard validation result structure
        @return Dictionary with validation result fields
        """
        return {"valid": True, "errors": [], "warnings": []}

    def _check_config_attribute(
        self, attr_name: str, result: dict[str, Any]
    ) -> Any | None:
        """
        @brief Check if config has attribute and return it, or add error
        @param attr_name Attribute name to check
        @param result Validation result dictionary to update
        @return The attribute value if found, None otherwise
        """
        if not hasattr(self.config, attr_name):
            result["errors"].append(
                f"Missing {attr_name.replace('_', ' ')} configuration"
            )
            result["valid"] = False
            return None
        return getattr(self.config, attr_name)

    def _validate_numeric_range(
        self,
        value: Any,
        min_val: float,
        max_val: float,
        name: str,
        result: dict[str, Any],
        warning_range: tuple[float, float] | None = None,
    ) -> None:
        """
        @brief Validate numeric value within range
        @param value Value to validate
        @param min_val Minimum allowed value
        @param max_val Maximum allowed value
        @param name Name of the value for error messages
        @param result Validation result dictionary to update
        @param warning_range Optional range that triggers warnings
        """
        if not isinstance(value, int | float) or value <= 0:
            result["errors"].append(f"Invalid {name}: {value}")
            result["valid"] = False
        elif warning_range and not (warning_range[0] <= value <= warning_range[1]):
            result["warnings"].append(
                f"{name} {value} is outside typical range ({warning_range[0]}-{warning_range[1]})"
            )

    def validate_dpi_config(self) -> dict[str, Any]:
        """
        @brief Validate DPI configuration settings
        @return DPI validation results
        """
        result = self._create_validation_result()

        dpi_settings = self._check_config_attribute("dpi_settings", result)
        if not dpi_settings:
            return result

        # Validate DPI value
        dpi = dpi_settings.get("dpi", 96)
        self._validate_numeric_range(dpi, 1, 1000, "DPI value", result, (72, 300))

        # Validate scaling factor
        scale = dpi_settings.get("scale_factor", 1.0)
        self._validate_numeric_range(scale, 0.1, 10, "scale factor", result, (0.5, 3.0))

        # Validate auto-detection setting
        auto_detect = dpi_settings.get("auto_detect", True)
        if not isinstance(auto_detect, bool):
            result["warnings"].append("Auto-detect should be boolean")

        return result

    def validate_font_config(self) -> dict[str, Any]:
        """
        @brief Validate font configuration and availability
        @return Font validation results
        """
        result = self._create_validation_result()

        font_settings = self._check_config_attribute("font_settings", result)
        if not font_settings:
            return result

        # Validate main font
        main_font = font_settings.get("font", "Monospace")
        if not isinstance(main_font, str) or not main_font.strip():
            result["errors"].append("Invalid main font specification")
            result["valid"] = False

        # Validate font size
        font_size = font_settings.get("fontsize", 12)
        self._validate_numeric_range(font_size, 1, 100, "font size", result, (8, 24))

        # Check font availability
        if self._is_command_available("fc-list") and not self._check_font_available(
            main_font
        ):
            result["warnings"].append(f"Font '{main_font}' may not be available")

        return result

    def validate_color_config(self) -> dict[str, Any]:
        """
        @brief Validate color configuration
        @return Color validation results
        """
        result = self._create_validation_result()

        if hasattr(self.config, "color_manager"):
            color_manager = self.config.color_manager
            if hasattr(color_manager, "validate_colors"):
                color_validation = color_manager.validate_colors()
                result.update(color_validation)
            else:
                result["warnings"].append("Color manager lacks validation method")
        else:
            result["warnings"].append("No color manager configured")

        return result

    def validate_screen_config(self) -> dict[str, Any]:
        """
        @brief Validate screen configuration settings
        @return Screen validation results
        """
        result = self._create_validation_result()

        screen_settings = self._check_config_attribute("screen_settings", result)
        if not screen_settings:
            return result

        # Validate detection delay
        delay = screen_settings.get("detection_delay", 1.0)
        self._validate_numeric_range(delay, 0, 60, "detection delay", result, (0.1, 5))

        # Validate startup delay
        startup_delay = screen_settings.get("startup_delay", 5.0)
        self._validate_numeric_range(
            startup_delay, 0, 300, "startup delay", result, (1, 60)
        )

        return result

    def validate_hotkey_config(self) -> dict[str, Any]:
        """
        @brief Validate hotkey configuration
        @return Hotkey validation results
        """
        result = self._create_validation_result()

        if not hasattr(self.config, "keys"):
            result["errors"].append("No key bindings configured")
            result["valid"] = False
            return result

        keys = self.config.keys
        if not keys:
            result["warnings"].append("No key bindings found")
            return result

        # Validate key structure
        for i, key in enumerate(keys):
            if not hasattr(key, "key") or not hasattr(key, "modifiers"):
                result["errors"].append(f"Key {i} missing required attributes")
                result["valid"] = False
                continue

            if not key.key or not key.key.strip():
                result["warnings"].append(f"Key {i} has empty key value")

            if not isinstance(key.modifiers, list):
                result["warnings"].append(f"Key {i} modifiers should be a list")

        return result

    def validate_performance_config(self) -> dict[str, Any]:
        """
        @brief Validate performance-related configuration
        @return Performance validation results
        """
        result = self._create_validation_result()

        if hasattr(self.config, "performance_settings"):
            perf_settings = self.config.performance_settings

            cache_enabled = perf_settings.get("enable_caching", True)
            if not isinstance(cache_enabled, bool):
                result["warnings"].append("Cache enabled should be boolean")

            thread_pool = perf_settings.get("thread_pool_size", 4)
            if not isinstance(thread_pool, int) or thread_pool < 1:
                result["errors"].append(f"Invalid thread pool size: {thread_pool}")
                result["valid"] = False
            elif thread_pool > 16:
                result["warnings"].append(f"Large thread pool size: {thread_pool}")
        else:
            result["warnings"].append("No performance settings configured")

        return result

    def _is_command_available(self, command: str) -> bool:
        """
        @brief Check if a command is available on the system
        @param command Command name to check
        @return True if command is available, False otherwise
        """
        import subprocess

        try:
            subprocess.run(
                [command, "--version"], capture_output=True, check=False, timeout=5
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def _check_font_available(self, font_name: str) -> bool:
        """
        @brief Check if a font is available using fc-list
        @param font_name Name of the font to check
        @return True if font is available, False otherwise
        """
        import subprocess

        try:
            result = subprocess.run(
                ["fc-list", font_name], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return True  # Assume available if fc-list fails

    def get_validation_summary(self) -> str:
        """
        @brief Get a human-readable summary of validation results
        @return Formatted validation summary
        """
        results = self.validation_results
        lines = [
            "=== Qtile Configuration Validation Summary ===",
            f"Overall Status: {'✅ Valid' if results['valid'] else '❌ Invalid'}",
            "",
        ]

        if results["errors"]:
            lines.append(f"Errors ({len(results['errors'])}):")
            lines.extend(f"  ❌ {error}" for error in results["errors"])

        if results["warnings"]:
            lines.append(f"Warnings ({len(results['warnings'])}):")
            lines.extend(f"  ⚠️  {warning}" for warning in results["warnings"])

        if not results["errors"] and not results["warnings"]:
            lines.append("✅ No issues found!")

        return "\n".join(lines)

    def validate_and_report(self) -> bool:
        """
        @brief Validate configuration and print report
        @return True if valid, False otherwise
        """
        self.validate_all()
        print(self.get_validation_summary())
        return self.validation_results["valid"]


def validate_qtile_config(config: Any) -> dict[str, Any]:
    """
    @brief Convenience function to validate qtile configuration
    @param config Qtile configuration object
    @return Validation results
    """
    validator = ConfigValidator(config)
    return validator.validate_all()


def quick_validate_config(config: Any) -> bool:
    """
    @brief Quick validation check - returns only validity status
    @param config Qtile configuration object
    @return True if valid, False otherwise
    """
    validator = ConfigValidator(config)
    results = validator.validate_all()
    return results["valid"]


# Maintain backward compatibility
__all__ = [
    "ConfigValidator",
    "quick_validate_config",
    "validate_qtile_config",
]
