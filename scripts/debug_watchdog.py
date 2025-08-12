#!/usr/bin/env python3
"""
Enhanced watchdog debugging script to investigate file path issues
with wal colors.json monitoring
"""

import sys
import json
import time
import threading
from pathlib import Path

# Add qtile config to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    print("❌ Watchdog not available")
    sys.exit(1)

class DebugFileHandler(FileSystemEventHandler):
    """Enhanced file handler that logs all events with detailed path info"""

    def __init__(self, target_file):
        self.target_file = Path(target_file).resolve()
        self.events = []
        self.lock = threading.Lock()

    def log_event(self, event_type, event):
        """Log detailed event information"""
        with self.lock:
            event_path = Path(event.src_path).resolve()

            info = {
                'type': event_type,
                'timestamp': time.time(),
                'src_path': str(event.src_path),
                'src_path_resolved': str(event_path),
                'target_path': str(self.target_file),
                'is_directory': event.is_directory,
                'paths_equal_str': event.src_path == str(self.target_file),
                'paths_equal_pathlib': event_path == self.target_file,
                'target_exists': self.target_file.exists(),
                'src_exists': event_path.exists(),
            }

            # Add file size if it's a file
            if not event.is_directory and event_path.exists():
                try:
                    info['file_size'] = event_path.stat().st_size
                except:
                    info['file_size'] = 'unknown'

            self.events.append(info)

            # Print immediate feedback
            match_indicator = "🎯" if event_path == self.target_file else "📄"
            print(f"{match_indicator} {event_type}: {event.src_path}")
            if event_path == self.target_file:
                print(f"   ✅ TARGET FILE MATCHED!")

    def on_modified(self, event):
        self.log_event("MODIFIED", event)

    def on_created(self, event):
        self.log_event("CREATED", event)

    def on_deleted(self, event):
        self.log_event("DELETED", event)

    def on_moved(self, event):
        self.log_event("MOVED", event)

def test_basic_monitoring():
    """Test basic file monitoring of wal colors.json"""
    print("🔍 Testing Basic Wal Colors.json Monitoring")
    print("=" * 45)

    colors_file = Path("~/.cache/wal/colors.json").expanduser()
    watch_dir = colors_file.parent

    print(f"Target file: {colors_file}")
    print(f"Resolved: {colors_file.resolve()}")
    print(f"Watch dir: {watch_dir}")
    print(f"File exists: {colors_file.exists()}")

    if not colors_file.exists():
        print("❌ Colors file doesn't exist!")
        return False

    # Create handler and observer
    handler = DebugFileHandler(colors_file)
    observer = Observer()

    try:
        observer.schedule(handler, str(watch_dir), recursive=False)
        observer.start()
        print(f"✅ Started monitoring {watch_dir}")

        # Wait for setup
        time.sleep(0.5)

        print("\n📝 Making test modification...")

        # Read current content
        original_content = colors_file.read_text()
        colors_data = json.loads(original_content)

        # Make a small change
        original_bg = colors_data['special']['background']
        colors_data['special']['background'] = "#999999"

        # Write the change
        colors_file.write_text(json.dumps(colors_data, indent=4))
        print(f"   Changed background: {original_bg} → #999999")

        # Wait for events
        print("⏰ Waiting for file events (3 seconds)...")
        time.sleep(3)

        # Restore original content
        colors_file.write_text(original_content)
        print("✅ Restored original content")

        # Wait a bit more for restore events
        time.sleep(1)

        # Stop observer
        observer.stop()
        observer.join()

        # Print results
        print(f"\n📊 Results: {len(handler.events)} events detected")

        target_events = 0
        for i, event in enumerate(handler.events):
            print(f"\nEvent {i+1}:")
            print(f"  Type: {event['type']}")
            print(f"  Path: {event['src_path']}")
            print(f"  Resolved: {event['src_path_resolved']}")
            print(f"  Target match (str): {event['paths_equal_str']}")
            print(f"  Target match (Path): {event['paths_equal_pathlib']}")
            print(f"  Is directory: {event['is_directory']}")
            print(f"  File size: {event.get('file_size', 'N/A')}")

            if event['paths_equal_pathlib']:
                target_events += 1

        print(f"\n🎯 Target file events: {target_events}")
        return target_events > 0

    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_path_variations():
    """Test different path comparison methods"""
    print("\n🔍 Testing Path Comparison Methods")
    print("=" * 35)

    colors_file = Path("~/.cache/wal/colors.json").expanduser()

    variations = [
        str(colors_file),
        str(colors_file.resolve()),
        str(colors_file.absolute()),
        colors_file.as_posix(),
        colors_file.resolve().as_posix(),
    ]

    print(f"Original path: {colors_file}")
    print("Path variations:")
    for i, variation in enumerate(variations):
        print(f"  {i+1}. {variation}")

    # Test what wal actually creates
    print(f"\nFile properties:")
    if colors_file.exists():
        stat = colors_file.stat()
        print(f"  Size: {stat.st_size} bytes")
        print(f"  Modified: {time.ctime(stat.st_mtime)}")
        print(f"  Inode: {stat.st_ino}")
    else:
        print("  File does not exist!")

def test_wal_integration():
    """Test actual wal command integration"""
    print("\n🔍 Testing Wal Command Integration")
    print("=" * 35)

    import subprocess

    colors_file = Path("~/.cache/wal/colors.json").expanduser()

    # Check if wal is available
    try:
        result = subprocess.run(['wal', '--version'], capture_output=True, text=True)
        print(f"✅ Wal available: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Wal command not found")
        return False

    # Set up monitoring
    handler = DebugFileHandler(colors_file)
    observer = Observer()

    try:
        observer.schedule(handler, str(colors_file.parent), recursive=False)
        observer.start()
        print("✅ Started monitoring for wal changes")

        # Find a wallpaper to use
        wallpaper_dirs = [
            Path("~/Wallpapers").expanduser(),
            Path("~/Pictures").expanduser(),
            Path("/usr/share/pixmaps").expanduser(),
        ]

        test_image = None
        for wdir in wallpaper_dirs:
            if wdir.exists():
                for ext in ['*.jpg', '*.png', '*.jpeg']:
                    images = list(wdir.glob(f"**/{ext}"))
                    if images:
                        test_image = images[0]
                        break
                if test_image:
                    break

        if not test_image:
            print("❌ No test wallpaper found")
            return False

        print(f"📸 Using test wallpaper: {test_image}")

        # Run wal command
        print("🎨 Running wal command...")
        result = subprocess.run(['wal', '-i', str(test_image)],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Wal command completed successfully")
        else:
            print(f"❌ Wal command failed: {result.stderr}")
            return False

        # Wait for file changes
        print("⏰ Waiting for wal file changes (5 seconds)...")
        time.sleep(5)

        observer.stop()
        observer.join()

        print(f"\n📊 Wal generated {len(handler.events)} file events")

        colors_events = 0
        for event in handler.events:
            if event['paths_equal_pathlib']:
                colors_events += 1
                print(f"🎯 Colors.json event: {event['type']}")

        return colors_events > 0

    except Exception as e:
        print(f"❌ Wal integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all watchdog debugging tests"""
    print("🔧 Watchdog File Monitoring Debug Suite")
    print("=" * 40)

    results = {}

    # Test 1: Basic monitoring
    results['basic'] = test_basic_monitoring()

    # Test 2: Path variations
    test_path_variations()

    # Test 3: Wal integration
    results['wal'] = test_wal_integration()

    # Summary
    print("\n📊 Debug Results")
    print("=" * 16)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test:10} {status}")

    if not any(results.values()):
        print("\n🔧 Debugging Recommendations:")
        print("• Check file permissions on ~/.cache/wal/")
        print("• Verify watchdog version compatibility")
        print("• Try running as different user")
        print("• Check if file is on special filesystem (tmpfs, etc.)")

    return any(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Debug interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
