#!/usr/bin/env python3
"""
Color management module for qtile
Handles pywal/wallust color loading and automatic reloading
"""

import os
import json
import time
import threading
import shutil
import hashlib
from libqtile.log_utils import logger


class ColorManager:
    """Manages color loading and automatic reloading from pywal/wallust"""
    
    colors_file: str
    backup_dir: str
    restart_trigger_file: str
    last_good_colors_file: str
    colordict: dict
    last_file_hash: str | None
    watcher_thread: threading.Thread | None
    restart_checker_thread: threading.Thread | None
    _shutdown_event: threading.Event
    _startup_time: float

    def __init__(self):
        self.colors_file = os.path.expanduser("~/.cache/wal/colors.json")
        self.backup_dir = os.path.expanduser("~/.cache/wal/backups")
        self.restart_trigger_file = os.path.expanduser("~/.config/qtile/restart_trigger")
        self.last_good_colors_file = os.path.expanduser("~/.cache/wal/last_good_colors.json")

        # Initialize directories
        self._ensure_directories()

        # Load colors with validation
        self.colordict = self._load_colors_safely()
        self.last_file_hash = self._get_file_hash(self.colors_file)

        # Threading and monitoring
        self.watcher_thread = None
        self.restart_checker_thread = None
        self._shutdown_event = threading.Event()

        import time
        self._startup_time = time.time()

        # Create initial backup
        self._backup_current_colors()

    def _ensure_directories(self):
        """Ensure required directories exist"""
        try:
            os.makedirs(os.path.dirname(self.colors_file), exist_ok=True)
            os.makedirs(self.backup_dir, exist_ok=True)
            os.makedirs(os.path.dirname(self.restart_trigger_file), exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")

    def _get_file_hash(self, filepath: str) -> str | None:
        """Get SHA256 hash of file content"""
        try:
            if not os.path.exists(filepath):
                return None
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error getting file hash: {e}")
            return None

    def _validate_colors(self, colors: dict) -> bool:
        """Validate color dictionary structure"""
        try:
            if not isinstance(colors, dict):
                return False

            # Check required sections
            if 'special' not in colors or 'colors' not in colors:
                return False

            # Check special colors
            special = colors['special']
            required_special = ['background', 'foreground', 'cursor']
            for key in required_special:
                if key not in special or not isinstance(special[key], str):
                    return False
                if not special[key].startswith('#') or len(special[key]) != 7:
                    return False

            # Check color palette
            color_palette = colors['colors']
            for i in range(16):
                color_key = f'color{i}'
                if color_key not in color_palette:
                    return False
                color_val = color_palette[color_key]
                if not isinstance(color_val, str) or not color_val.startswith(
                        '#') or len(color_val) != 7:
                    return False

            return True
        except Exception as e:
            logger.error(f"Error validating colors: {e}")
            return False

    def _backup_current_colors(self):
        """Create backup of current colors"""
        try:
            if os.path.exists(self.colors_file):
                # Create timestamped backup
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(self.backup_dir, f"colors_{timestamp}.json")
                _ = shutil.copy2(self.colors_file, backup_file)

                # Keep only last 10 backups
                backups = sorted([f for f in os.listdir(
                    self.backup_dir) if f.startswith('colors_')])
                while len(backups) > 10:
                    old_backup = backups.pop(0)
                    os.remove(os.path.join(self.backup_dir, old_backup))

                # Update last good colors file
                if self._validate_colors(json.load(open(self.colors_file))):
                    _ = shutil.copy2(self.colors_file, self.last_good_colors_file)
                    logger.debug(f"Created color backup: {backup_file}")
        except Exception as e:
            logger.error(f"Error creating color backup: {e}")

    def _load_colors_safely(self):
        """Load colors with validation and fallback"""
        # Try to load current colors file
        if os.path.exists(self.colors_file):
            try:
                with open(self.colors_file, 'r', encoding="utf-8") as f:
                    colors = json.load(f)
                if self._validate_colors(colors):
                    logger.info("Loaded colors from wal cache")
                    return colors
                else:
                    logger.warning("Invalid colors in wal cache, trying backup")
            except Exception as e:
                logger.error(f"Error loading colors from wal cache: {e}")

        # Try to load last good colors
        if os.path.exists(self.last_good_colors_file):
            try:
                with open(self.last_good_colors_file, 'r', encoding="utf-8") as f:
                    colors = json.load(f)
                if self._validate_colors(colors):
                    logger.info("Loaded colors from last good backup")
                    return colors
            except Exception as e:
                logger.error(f"Error loading last good colors: {e}")

        # Try to load from most recent backup
        try:
            if os.path.exists(self.backup_dir):
                backups = sorted([f for f in os.listdir(
                    self.backup_dir) if f.startswith('colors_')])
                if backups:
                    latest_backup = os.path.join(self.backup_dir, backups[-1])
                    with open(latest_backup, 'r', encoding="utf-8") as f:
                        colors = json.load(f)
                    if self._validate_colors(colors):
                        logger.info(f"Loaded colors from backup: {backups[-1]}")
                        return colors
        except Exception as e:
            logger.error(f"Error loading from backup: {e}")

        # Fall back to default colors
        logger.warning("Using default colors due to validation failures")
        return self._load_default_colors()

    def _load_default_colors(self):
        """Load default colors if pywal colors don't exist"""
        colors = {
            "wallpaper": "/home/ekollof/Wallpapers/derektaylor/0270.jpg",
            "alpha": "100",
            "special": {
                "background": "#0F0F0F",
                "foreground": "#d3d9db",
                "cursor": "#d3d9db"
            },
            "colors": {
                "color0": "#0F0F0F",
                "color1": "#9B8A77",
                "color2": "#4B768A",
                "color3": "#6A8FA0",
                "color4": "#97A1A1",
                "color5": "#AFB6B4",
                "color6": "#C2BEB5",
                "color7": "#d3d9db",
                "color8": "#939799",
                "color9": "#9B8A77",
                "color10": "#4B768A",
                "color11": "#6A8FA0",
                "color12": "#97A1A1",
                "color13": "#AFB6B4",
                "color14": "#E4A3A8",
                "color15": "#E9D2D4"
            }
        }
        return colors

    def load_colors(self):
        """Load colors from pywal colors.json file with validation"""
        return self._load_colors_safely()

    def get_colors(self):
        """Get current color dictionary"""
        return self.colordict

    def update_colors(self):
        """Update colors and trigger qtile restart with validation"""
        logger.info("Reloading colors due to file change")
        try:
            # Check if file actually changed
            current_hash = self._get_file_hash(self.colors_file)
            if current_hash == self.last_file_hash:
                logger.debug("Colors file hash unchanged, skipping update")
                return

            logger.info("Loading new colors...")
            new_colors = self._load_colors_safely()

            # Validate new colors
            if not self._validate_colors(new_colors):
                logger.error("New colors failed validation, keeping current colors")
                return

            # Update colors if different
            if new_colors != self.colordict:
                self.colordict = new_colors
                self.last_file_hash = current_hash
                logger.info(f"Updated colors: background={new_colors['special']['background']}")

                # Create backup of new colors
                self._backup_current_colors()

                # Create restart trigger file only if Qtile has been running for a while
                import time
                startup_time = getattr(self, '_startup_time', time.time())
                if time.time() - startup_time > 30:  # Only restart after 30 seconds of runtime
                    logger.info("Creating restart trigger...")
                    try:
                        with open(self.restart_trigger_file, "w") as f:
                            _ = f.write(f"restart_{int(time.time())}")
                    except Exception as e:
                        logger.error(f"Error creating restart trigger: {e}")
                else:
                    logger.info("Colors updated without restart (too soon after startup)")
            else:
                logger.debug("Colors unchanged after reload")

        except Exception as e:
            logger.error(f"Error updating colors: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def check_restart_trigger(self):
        """Check if qtile should restart due to color changes"""
        try:
            if os.path.exists(self.restart_trigger_file):
                logger.info("Color change detected - restarting qtile")
                os.remove(self.restart_trigger_file)

                # Use qtile's built-in restart
                import libqtile
                if hasattr(libqtile, 'qtile') and libqtile.qtile:
                    libqtile.qtile.restart()
                else:
                    # Fallback
                    _ = os.system("qtile cmd-obj -o cmd -f restart")
        except Exception as e:
            logger.error(f"Error in restart check: {e}")

    def setup_file_watcher(self):
        """Set up file monitoring for color changes"""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            logger.info("Watchdog not available, falling back to polling")
            return None

        class ColorsFileHandler(FileSystemEventHandler):
            color_manager: "ColorManager"
            last_update: float
            consecutive_errors: int
            
            def __init__(self, color_manager: "ColorManager"):
                self.color_manager = color_manager
                self.last_update = 0
                self.consecutive_errors = 0

            def on_modified(self, event):
                if event.is_directory:
                    return
                if event.src_path == self.color_manager.colors_file:
                    current_time = time.time()
                    # Debounce rapid changes
                    if current_time - self.last_update > 2.0:
                        self.last_update = current_time
                        logger.info("Colors file changed, updating colors...")

                        def delayed_update():
                            try:
                                # Wait for file to be fully written
                                time.sleep(1.5)
                                self.color_manager.update_colors()
                                self.consecutive_errors = 0
                            except Exception as e:
                                self.consecutive_errors += 1
                                logger.error(f"Error in delayed color update: {e}")
                                if self.consecutive_errors > 5:
                                    logger.error("Too many consecutive errors, stopping updates")
                                    return

                        threading.Thread(target=delayed_update, daemon=True).start()

            def on_created(self, event):
                """Handle file creation (e.g., when pywal creates new colors.json)"""
                if not event.is_directory and event.src_path == self.color_manager.colors_file:
                    logger.info("Colors file created")
                    current_time = time.time()
                    if current_time - self.last_update > 2.0:
                        self.last_update = current_time

                        def delayed_update():
                            try:
                                time.sleep(1.5)
                                self.color_manager.update_colors()
                                self.consecutive_errors = 0
                            except Exception as e:
                                self.consecutive_errors += 1
                                logger.error(f"Error in delayed color update: {e}")

                        threading.Thread(target=delayed_update, daemon=True).start()

            def on_moved(self, event):
                """Handle file moves (e.g., atomic writes)"""
                if not event.is_directory and event.dest_path == self.color_manager.colors_file:
                    logger.info("Colors file moved/renamed")
                    current_time = time.time()
                    if current_time - self.last_update > 2.0:
                        self.last_update = current_time

                        def delayed_update():
                            try:
                                time.sleep(1.5)
                                self.color_manager.update_colors()
                                self.consecutive_errors = 0
                            except Exception as e:
                                self.consecutive_errors += 1
                                logger.error(f"Error in delayed color update: {e}")

                        threading.Thread(target=delayed_update, daemon=True).start()

        event_handler = ColorsFileHandler(self)
        observer = Observer()
        watch_dir = os.path.dirname(self.colors_file)
        _ = observer.schedule(event_handler, watch_dir, recursive=False)
        observer.start()
        logger.info("Started file watcher for color changes")
        return observer

    def watch_colors_file(self):
        """Main file watching loop with robust error handling"""
        consecutive_errors = 0
        max_errors = 10

        try:
            # Ensure directories exist
            self._ensure_directories()

            # Try to use watchdog first
            observer = self.setup_file_watcher()
            if observer:
                logger.info("Using watchdog for file monitoring")
                try:
                    while not self._shutdown_event.is_set():
                        if not observer.is_alive():
                            logger.warning("Watchdog observer died, restarting...")
                            observer.stop()
                            observer = self.setup_file_watcher()
                            if not observer:
                                break
                        time.sleep(1)
                except Exception as e:
                    logger.error(f"Watchdog monitoring error: {e}")
                finally:
                    if observer and observer.is_alive():
                        observer.stop()
                        observer.join(timeout=5)

            # Fallback to polling method
            logger.info("Using polling for file monitoring")
            last_modified = 0
            last_hash = None

            if os.path.exists(self.colors_file):
                last_modified = os.path.getmtime(self.colors_file)
                last_hash = self._get_file_hash(self.colors_file)

            while not self._shutdown_event.is_set():
                try:
                    if os.path.exists(self.colors_file):
                        current_modified = os.path.getmtime(self.colors_file)
                        current_hash = self._get_file_hash(self.colors_file)

                        # Check both modification time and hash for better detection
                        if (current_modified != last_modified or current_hash != last_hash):
                            logger.info("Colors file changed (polling detection)")

                            def delayed_update():
                                try:
                                    time.sleep(1.5)
                                    self.update_colors()
                                    nonlocal consecutive_errors
                                    consecutive_errors = 0
                                except Exception as e:
                                    consecutive_errors += 1
                                    logger.error(f"Error in polling update: {e}")

                            threading.Thread(target=delayed_update, daemon=True).start()
                            last_modified = current_modified
                            last_hash = current_hash

                    consecutive_errors = 0
                    time.sleep(1.0)  # Slightly longer polling interval

                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Polling error: {e}")
                    if consecutive_errors >= max_errors:
                        logger.error(
                            f"Too many consecutive polling errors ({consecutive_errors}), stopping watcher")
                        break
                    time.sleep(min(5.0 * consecutive_errors, 30.0))  # Exponential backoff

        except Exception as e:
            logger.error(f"Watch thread error: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def restart_trigger_checker(self):
        """Periodically check for restart trigger with better error handling"""
        consecutive_errors = 0
        max_errors = 10

        while not self._shutdown_event.is_set():
            try:
                self.check_restart_trigger()
                consecutive_errors = 0
                time.sleep(1)
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in restart trigger checker: {e}")
                if consecutive_errors >= max_errors:
                    logger.error("Too many consecutive restart checker errors, stopping")
                    break
                time.sleep(min(5.0 * consecutive_errors, 30.0))

    def stop_monitoring(self):
        """Gracefully stop all monitoring threads"""
        logger.info("Stopping color monitoring...")
        self._shutdown_event.set()

        # Wait for threads to finish
        if self.watcher_thread and self.watcher_thread.is_alive():
            self.watcher_thread.join(timeout=10)
        if hasattr(
                self,
                'restart_checker_thread') and self.restart_checker_thread and self.restart_checker_thread.is_alive():
            self.restart_checker_thread.join(timeout=5)

        logger.info("Color monitoring stopped")

    def start_monitoring(self):
        """Start color file monitoring with improved error handling"""
        try:
            # Clear shutdown event
            self._shutdown_event.clear()

            # Start color file watcher if not already running
            if self.watcher_thread is None or not self.watcher_thread.is_alive():
                logger.info("Starting color file watcher...")
                self.watcher_thread = threading.Thread(target=self.watch_colors_file, daemon=True)
                self.watcher_thread.start()
                logger.info("Color file watcher started")

            # Start restart trigger checker if not already running
            if not hasattr(
                    self,
                    'restart_checker_thread') or self.restart_checker_thread is None or not self.restart_checker_thread.is_alive():
                logger.info("Starting restart trigger checker...")
                self.restart_checker_thread = threading.Thread(
                    target=self.restart_trigger_checker, daemon=True)
                self.restart_checker_thread.start()
                logger.info("Restart trigger checker started")

        except Exception as e:
            logger.error(f"Error starting color monitoring: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def restart_monitoring(self):
        """Restart color monitoring (useful for recovery)"""
        logger.info("Restarting color monitoring...")
        self.stop_monitoring()
        time.sleep(2)  # Give threads time to stop
        self.start_monitoring()

    def is_monitoring(self):
        """Check if color monitoring is active"""
        watcher_running = self.watcher_thread is not None and self.watcher_thread.is_alive()
        checker_running = hasattr(
            self,
            'restart_checker_thread') and self.restart_checker_thread is not None and self.restart_checker_thread.is_alive()
        return watcher_running and checker_running
    
    def validate_colors_public(self, colors: dict) -> bool:
        """Public interface for color validation"""
        return self._validate_colors(colors)
        
    def get_file_hash_public(self, filepath: str) -> str | None:
        """Public interface for getting file hash"""
        return self._get_file_hash(filepath)


# Singleton pattern to prevent multiple instances
_color_manager_instance = None


def get_color_manager():
    """Get or create the singleton color manager instance"""
    global _color_manager_instance
    if _color_manager_instance is None:
        _color_manager_instance = ColorManager()
    return _color_manager_instance


# Global color manager instance
color_manager = get_color_manager()


def get_colors():
    """Get current color dictionary"""
    return color_manager.get_colors()


def manual_color_reload():
    """Manually trigger color reload"""
    color_manager.update_colors()


def start_color_monitoring():
    """Start automatic color monitoring"""
    color_manager.start_monitoring()


def setup_color_monitoring():
    """Setup color monitoring after qtile startup"""
    try:
        if color_manager.is_monitoring():
            logger.info("Color file watcher is running")
        else:
            logger.warning("Color file watcher is not running - restarting")
            color_manager.start_monitoring()
    except Exception as e:
        logger.error(f"Error in setup_color_monitoring: {e}")


def restart_color_monitoring():
    """Restart color monitoring (for recovery)"""
    color_manager.restart_monitoring()


def validate_current_colors():
    """Validate current color configuration"""
    colors = color_manager.get_colors()
    is_valid = color_manager.validate_colors_public(colors)
    logger.info(f"Current colors validation: {'PASSED' if is_valid else 'FAILED'}")
    return is_valid


def get_color_file_status() -> dict:
    """Get status information about color files"""
    status = {
        'colors_file_exists': os.path.exists(color_manager.colors_file),
        'last_good_colors_exists': os.path.exists(color_manager.last_good_colors_file),
        'backup_dir_exists': os.path.exists(color_manager.backup_dir),
        'monitoring_active': color_manager.is_monitoring(),
        'current_hash': color_manager.get_file_hash_public(color_manager.colors_file),
        'validation_passed': color_manager.validate_colors_public(color_manager.colordict)
    }

    if os.path.exists(color_manager.backup_dir):
        backups = [f for f in os.listdir(color_manager.backup_dir) if f.startswith('colors_')]
        status['backup_count'] = len(backups)
        status['latest_backup'] = max(backups) if backups else None
    else:
        status['backup_count'] = 0
        status['latest_backup'] = None

    return status


# Load initial colors
color_manager.colordict = color_manager.load_colors()
