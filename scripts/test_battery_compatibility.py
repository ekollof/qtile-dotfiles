#!/usr/bin/env python3
"""
Battery Widget Compatibility Test Script

Tests qtile Battery widget compatibility across different platforms.
Helps diagnose platform-specific battery detection issues.

Usage:
    python3 scripts/test_battery_compatibility.py
"""

import sys
import platform
import subprocess
from pathlib import Path

# Add qtile config to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(title: str) -> None:
    """Print formatted section header"""
    print(f"\n🔍 {title}")
    print("=" * (len(title) + 4))


def print_result(test_name: str, passed: bool, details: str = "") -> None:
    """Print test result with consistent formatting"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        for line in details.split('\n'):
            if line.strip():
                print(f"   {line}")


def test_platform_detection() -> dict:
    """Test basic platform detection"""
    print_header("Platform Detection")

    try:
        system = platform.system()
        release = platform.release()
        machine = platform.machine()

        print(f"   System: {system}")
        print(f"   Release: {release}")
        print(f"   Machine: {machine}")

        supported_platforms = ["Linux", "OpenBSD", "FreeBSD", "NetBSD", "DragonFly"]
        is_supported = system in supported_platforms

        print_result("Platform detection", True, f"Detected: {system}")
        print_result("Platform supported", is_supported,
                    f"{'Supported' if is_supported else 'Unsupported'} platform")

        return {
            "system": system,
            "supported": is_supported,
            "details": f"{system} {release}"
        }

    except Exception as e:
        print_result("Platform detection", False, f"Error: {e}")
        return {"system": "unknown", "supported": False, "details": str(e)}


def test_linux_battery() -> dict:
    """Test Linux battery detection"""
    print_header("Linux Battery Detection")

    battery_paths = [
        "/sys/class/power_supply/BAT0",
        "/sys/class/power_supply/BAT1",
        "/sys/class/power_supply/battery"
    ]

    found_batteries = []
    details = []

    for path in battery_paths:
        path_obj = Path(path)
        exists = path_obj.exists()
        details.append(f"Path {path}: {'EXISTS' if exists else 'MISSING'}")

        if exists:
            type_file = path_obj / "type"
            if type_file.exists():
                try:
                    battery_type = type_file.read_text().strip()
                    details.append(f"  Type: {battery_type}")
                    if battery_type.lower() == "battery":
                        found_batteries.append(path)
                except Exception as e:
                    details.append(f"  Error reading type: {e}")

    has_battery = len(found_batteries) > 0
    print_result("Linux battery detection", has_battery, '\n'.join(details))

    return {
        "method": "sysfs",
        "detected": has_battery,
        "batteries": found_batteries,
        "details": details
    }


def test_openbsd_battery() -> dict:
    """Test OpenBSD battery detection"""
    print_header("OpenBSD Battery Detection")

    try:
        result = subprocess.run(['apm'], capture_output=True, text=True, timeout=5)

        details = [
            f"Command: apm",
            f"Return code: {result.returncode}",
            f"Stdout: '{result.stdout.strip()}'",
            f"Stderr: '{result.stderr.strip()}'"
        ]

        if result.returncode != 0:
            print_result("OpenBSD apm command", False, '\n'.join(details))
            return {"method": "apm", "detected": False, "details": details}

        output_lower = result.stdout.lower()
        has_battery = 'battery' in output_lower

        # Check for negative indicators
        negative_indicators = ['no battery', 'not present', 'unavailable']
        has_negative = any(indicator in output_lower for indicator in negative_indicators)

        if has_negative:
            has_battery = False
            details.append(f"Negative indicator found in output")

        details.append(f"Battery detected: {has_battery}")
        print_result("OpenBSD battery detection", has_battery, '\n'.join(details))

        return {
            "method": "apm",
            "detected": has_battery,
            "output": result.stdout.strip(),
            "details": details
        }

    except subprocess.TimeoutExpired:
        details = ["Command: apm", "Error: Command timed out"]
        print_result("OpenBSD apm command", False, '\n'.join(details))
        return {"method": "apm", "detected": False, "details": details}
    except FileNotFoundError:
        details = ["Command: apm", "Error: Command not found"]
        print_result("OpenBSD apm command", False, '\n'.join(details))
        return {"method": "apm", "detected": False, "details": details}
    except Exception as e:
        details = ["Command: apm", f"Error: {e}"]
        print_result("OpenBSD apm command", False, '\n'.join(details))
        return {"method": "apm", "detected": False, "details": details}


def test_bsd_battery(system: str) -> dict:
    """Test other BSD battery detection"""
    print_header(f"{system} Battery Detection")

    try:
        result = subprocess.run(['acpiconf', '-i', '0'], capture_output=True, text=True, timeout=5)

        details = [
            f"Command: acpiconf -i 0",
            f"Return code: {result.returncode}",
            f"Stdout: '{result.stdout.strip()}'",
            f"Stderr: '{result.stderr.strip()}'"
        ]

        has_battery = result.returncode == 0
        details.append(f"Battery detected: {has_battery}")

        print_result(f"{system} battery detection", has_battery, '\n'.join(details))

        return {
            "method": "acpiconf",
            "detected": has_battery,
            "output": result.stdout.strip(),
            "details": details
        }

    except subprocess.TimeoutExpired:
        details = ["Command: acpiconf -i 0", "Error: Command timed out"]
        print_result(f"{system} acpiconf command", False, '\n'.join(details))
        return {"method": "acpiconf", "detected": False, "details": details}
    except FileNotFoundError:
        details = ["Command: acpiconf -i 0", "Error: Command not found"]
        print_result(f"{system} acpiconf command", False, '\n'.join(details))
        return {"method": "acpiconf", "detected": False, "details": details}
    except Exception as e:
        details = ["Command: acpiconf -i 0", f"Error: {e}"]
        print_result(f"{system} acpiconf command", False, '\n'.join(details))
        return {"method": "acpiconf", "detected": False, "details": details}


def test_qtile_battery_widget() -> dict:
    """Test actual qtile Battery widget creation"""
    print_header("Qtile Battery Widget Compatibility")

    try:
        from libqtile import widget

        # Test basic widget creation
        test_widget = widget.Battery(format='{percent:2.0%}')

        details = [
            "Successfully created Battery widget",
            f"Widget type: {type(test_widget).__name__}",
            "No platform compatibility issues detected"
        ]

        print_result("Battery widget creation", True, '\n'.join(details))

        return {
            "compatible": True,
            "widget_created": True,
            "details": details
        }

    except RuntimeError as e:
        if "Unknown platform" in str(e):
            details = [
                f"RuntimeError: {e}",
                "Battery widget not supported on this platform",
                "This is the expected error for unsupported platforms"
            ]
            print_result("Battery widget creation", False, '\n'.join(details))
            return {
                "compatible": False,
                "widget_created": False,
                "error": "unknown_platform",
                "details": details
            }
        else:
            details = [
                f"RuntimeError: {e}",
                "Unexpected runtime error during widget creation"
            ]
            print_result("Battery widget creation", False, '\n'.join(details))
            return {
                "compatible": False,
                "widget_created": False,
                "error": "runtime_error",
                "details": details
            }
    except ImportError as e:
        details = [
            f"ImportError: {e}",
            "libqtile not available or not properly installed"
        ]
        print_result("Battery widget creation", False, '\n'.join(details))
        return {
            "compatible": False,
            "widget_created": False,
            "error": "import_error",
            "details": details
        }
    except Exception as e:
        details = [
            f"Unexpected error: {type(e).__name__}: {e}",
            "Unknown error during battery widget creation"
        ]
        print_result("Battery widget creation", False, '\n'.join(details))
        return {
            "compatible": False,
            "widget_created": False,
            "error": "unknown_error",
            "details": details
        }


def test_enhanced_bar_manager() -> dict:
    """Test the enhanced bar manager battery detection"""
    print_header("Enhanced Bar Manager Battery Check")

    try:
        from modules.bars_svg import EnhancedBarManager
        from modules.simple_color_management import color_manager
        from modules.qtile_config import get_config

        # Create bar manager instance
        qtile_config = get_config()
        bar_manager = EnhancedBarManager(color_manager, qtile_config)

        # Test battery support check
        battery_supported = bar_manager._check_battery_support()

        details = [
            f"Battery support result: {battery_supported}",
            "Enhanced bar manager battery check completed"
        ]

        print_result("Enhanced bar manager check", True, '\n'.join(details))

        return {
            "manager_available": True,
            "battery_supported": battery_supported,
            "details": details
        }

    except Exception as e:
        details = [
            f"Error: {type(e).__name__}: {e}",
            "Could not test enhanced bar manager"
        ]
        print_result("Enhanced bar manager check", False, '\n'.join(details))
        return {
            "manager_available": False,
            "battery_supported": False,
            "error": str(e),
            "details": details
        }


def run_comprehensive_test():
    """Run all battery compatibility tests"""
    print("🔧 Battery Widget Compatibility Test Suite")
    print("=" * 45)

    results = {}

    # Test 1: Platform detection
    results["platform"] = test_platform_detection()

    # Test 2: Platform-specific battery detection
    system = results["platform"]["system"]

    if system == "Linux":
        results["battery_detection"] = test_linux_battery()
    elif system == "OpenBSD":
        results["battery_detection"] = test_openbsd_battery()
    elif system in ["FreeBSD", "NetBSD", "DragonFly"]:
        results["battery_detection"] = test_bsd_battery(system)
    else:
        results["battery_detection"] = {
            "method": "none",
            "detected": False,
            "details": [f"No battery detection method for {system}"]
        }

    # Test 3: Qtile widget compatibility
    results["qtile_widget"] = test_qtile_battery_widget()

    # Test 4: Enhanced bar manager
    results["bar_manager"] = test_enhanced_bar_manager()

    # Summary
    print_header("Test Summary")

    platform_ok = results["platform"]["supported"]
    battery_detected = results["battery_detection"]["detected"]
    widget_compatible = results["qtile_widget"]["compatible"]
    manager_ok = results["bar_manager"]["manager_available"]

    print(f"Platform supported: {'✅' if platform_ok else '❌'} {results['platform']['system']}")
    print(f"Battery detected: {'✅' if battery_detected else '❌'} {results['battery_detection']['method']}")
    print(f"Widget compatible: {'✅' if widget_compatible else '❌'}")
    print(f"Bar manager works: {'✅' if manager_ok else '❌'}")

    # Recommendations
    print_header("Recommendations")

    if not platform_ok:
        print("• Platform not officially supported for battery widgets")
    elif not battery_detected:
        print("• No battery hardware detected on this system")
        print("• Battery widget will be skipped (expected behavior)")
    elif not widget_compatible:
        print("• Qtile battery widget not compatible with this platform")
        print("• This may indicate a qtile version or platform issue")
    elif not manager_ok:
        print("• Enhanced bar manager could not be tested")
        print("• Check qtile configuration and module imports")
    else:
        print("• ✅ Battery widget should work correctly on this system")
        print("• All compatibility checks passed")

    # Overall result
    should_work = platform_ok and battery_detected and widget_compatible
    overall = "✅ COMPATIBLE" if should_work else "❌ NOT COMPATIBLE"
    print(f"\nOverall battery widget compatibility: {overall}")

    return results


if __name__ == "__main__":
    try:
        results = run_comprehensive_test()

        # Exit with appropriate code
        compatible = (results["platform"]["supported"] and
                     results["qtile_widget"]["compatible"])
        sys.exit(0 if compatible else 1)

    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
