#!/usr/bin/env python3
"""
Enhanced diagnostic script for qtile color monitoring system
Tests all aspects of the color monitoring pipeline
"""

import sys
import json
import time
import threading
from pathlib import Path

# Add qtile config to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_watchdog_availability():
    """Test if watchdog is available and working"""
    print("🔍 Testing Watchdog Availability")
    print("=" * 40)

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        print("✅ Watchdog module imported successfully")

        # Test basic functionality
        class TestHandler(FileSystemEventHandler):
            def __init__(self):
                self.events = []

            def on_modified(self, event):
                self.events.append(event)

        observer = Observer()
        handler = TestHandler()
        test_dir = Path("/tmp")
        observer.schedule(handler, str(test_dir), recursive=False)
        observer.start()
        print("✅ Watchdog observer started successfully")
        observer.stop()
        observer.join()
        print("✅ Watchdog observer stopped successfully")
        return True

    except ImportError as e:
        print(f"❌ Watchdog not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Watchdog test failed: {e}")
        return False

def test_color_manager_init():
    """Test color manager initialization"""
    print("\n🔍 Testing Color Manager Initialization")
    print("=" * 45)

    try:
        from modules.simple_color_management import SimpleColorManager

        # Test basic initialization
        manager = SimpleColorManager()
        print(f"✅ Color manager created")
        print(f"   Colors file: {manager.colors_file}")
        print(f"   File exists: {manager.colors_file.exists()}")
        print(f"   Monitoring active: {manager.is_monitoring()}")

        # Test color loading
        colors = manager.get_colors()
        bg_color = colors.get('special', {}).get('background', 'Unknown')
        print(f"   Current background: {bg_color}")

        return manager

    except Exception as e:
        print(f"❌ Color manager initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_monitoring_start(manager):
    """Test starting monitoring"""
    print("\n🔍 Testing Monitoring Start")
    print("=" * 30)

    if not manager:
        print("❌ No manager available")
        return False

    try:
        print(f"Before start - Monitoring active: {manager.is_monitoring()}")

        # Try to start monitoring
        manager.start_monitoring()
        time.sleep(0.5)  # Give it time to start

        print(f"After start - Monitoring active: {manager.is_monitoring()}")
        print(f"Observer exists: {manager._observer is not None}")
        print(f"Polling thread exists: {manager._polling_thread is not None}")

        if manager._observer:
            print(f"Observer is alive: {manager._observer.is_alive()}")
        if manager._polling_thread:
            print(f"Polling thread is alive: {manager._polling_thread.is_alive()}")

        return manager.is_monitoring()

    except Exception as e:
        print(f"❌ Failed to start monitoring: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_change_detection(manager):
    """Test file change detection"""
    print("\n🔍 Testing File Change Detection")
    print("=" * 35)

    if not manager or not manager.is_monitoring():
        print("❌ Monitoring not active, cannot test file detection")
        return False

    try:
        # Create a backup of current colors
        original_colors = manager.colors_file.read_text()
        print(f"✅ Backed up original colors file")

        # Track changes
        change_detected = threading.Event()
        original_handle_change = manager._handle_color_change

        def mock_handle_change():
            print("🔔 File change detected!")
            change_detected.set()
            # Don't actually restart qtile during testing

        manager._handle_color_change = mock_handle_change

        print("📝 Modifying colors file...")

        # Parse and modify the colors
        colors_data = json.loads(original_colors)
        original_bg = colors_data['special']['background']

        # Change background color
        colors_data['special']['background'] = "#123456"

        # Write modified colors
        manager.colors_file.write_text(json.dumps(colors_data, indent=4))
        print(f"   Changed background from {original_bg} to #123456")

        # Wait for change detection
        print("⏰ Waiting for change detection (5 seconds)...")
        detected = change_detected.wait(timeout=5.0)

        if detected:
            print("✅ File change detected successfully!")
        else:
            print("❌ File change NOT detected")

        # Restore original colors
        manager.colors_file.write_text(original_colors)
        manager._handle_color_change = original_handle_change

        # Reload original colors
        manager.colordict = manager._load_colors()
        print("✅ Original colors restored")

        return detected

    except Exception as e:
        print(f"❌ File change test failed: {e}")
        import traceback
        traceback.print_exc()

        # Try to restore original colors
        try:
            if 'original_colors' in locals():
                manager.colors_file.write_text(original_colors)
                print("✅ Original colors restored after error")
        except:
            print("❌ Could not restore original colors")

        return False

def test_qtile_integration():
    """Test qtile integration"""
    print("\n🔍 Testing Qtile Integration")
    print("=" * 30)

    try:
        from libqtile import qtile
        if qtile is not None:
            print("✅ Qtile instance available")
            print(f"   Qtile running: {hasattr(qtile, 'config')}")
            return True
        else:
            print("❌ Qtile instance not available")
            return False

    except Exception as e:
        print(f"❌ Qtile integration test failed: {e}")
        return False

def test_force_restart_monitoring():
    """Test restarting monitoring"""
    print("\n🔍 Testing Monitoring Restart")
    print("=" * 32)

    try:
        from modules.simple_color_management import color_manager

        print(f"Before restart - Active: {color_manager.is_monitoring()}")

        # Stop monitoring
        color_manager.stop_monitoring()
        time.sleep(0.5)
        print(f"After stop - Active: {color_manager.is_monitoring()}")

        # Force restart
        result = color_manager.force_start_monitoring()
        time.sleep(0.5)
        print(f"After restart - Active: {color_manager.is_monitoring()}")
        print(f"Force start result: {result}")

        return color_manager.is_monitoring()

    except Exception as e:
        print(f"❌ Restart test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all diagnostic tests"""
    print("🔧 Qtile Color Monitoring Diagnostic Suite")
    print("=" * 45)

    results = {}

    # Test 1: Watchdog availability
    results['watchdog'] = test_watchdog_availability()

    # Test 2: Color manager initialization
    manager = test_color_manager_init()
    results['init'] = manager is not None

    # Test 3: Monitoring start
    results['monitoring'] = test_monitoring_start(manager)

    # Test 4: File change detection
    results['file_detection'] = test_file_change_detection(manager)

    # Test 5: Qtile integration
    results['qtile'] = test_qtile_integration()

    # Test 6: Restart monitoring
    results['restart'] = test_force_restart_monitoring()

    # Summary
    print("\n📊 Diagnostic Summary")
    print("=" * 20)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test:15} {status}")

    # Overall status
    all_passed = all(results.values())
    overall = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"\nOverall: {overall}")

    # Recommendations
    if not all_passed:
        print("\n🔧 Recommendations:")
        if not results['watchdog']:
            print("• Install watchdog: pip install watchdog")
        if not results['monitoring']:
            print("• Check qtile logs for monitoring startup errors")
        if not results['file_detection']:
            print("• File change detection not working - check permissions")
        if not results['qtile']:
            print("• Run this script from within qtile session")

    return all_passed

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
