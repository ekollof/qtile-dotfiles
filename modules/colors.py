#!/usr/bin/env python3
"""
Color management module for qtile
Handles pywal/wallust color loading and automatic reloading
"""

import hashlib
import json
import libqtile
import os
import shutil
import tempfile
import threading
import time
import traceback
from libqtile.log_utils import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ColorManager:
    """Manages color loading and automatic reloading from pywal/wallust"""
    
    colors_file: str
    backup_dir: str
    restart_trigger_file: str
    last_good_colors_file: str
    colordict: dict[str, dict[str, str] | str]
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

        self._startup_time = time.time()

        # Create initial backup
        self._backup_current_colors()

    def _ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        try:
            for directory in [self.backup_dir, os.path.dirname(self.restart_trigger_file)]:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
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

    def _validate_colors(self, colors: dict[str, dict[str, str] | str]) -> bool:
        """Validate color dictionary structure"""
        try:
            # Check required sections
            if 'special' not in colors or 'colors' not in colors:
                return False

            # Check special colors
            special = colors['special']
            if not isinstance(special, dict):
                return False
            required_special = ['background', 'foreground', 'cursor']
            for key in required_special:
                if key not in special:
                    return False
                value = special[key]
                if not isinstance(value, str) or not value.startswith('#') or len(value) != 7:
                    return False

            # Check color palette
            color_palette = colors['colors']
            if not isinstance(color_palette, dict):
                return False
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

    def _load_colors_safely(self) -> dict[str, dict[str, str] | str]:
        """Load colors with validation and fallback"""
        # Try to load current colors file
        if os.path.exists(self.colors_file):
            try:
                with open(self.colors_file, 'r', encoding="utf-8") as f:
                    loaded_colors: dict[str, dict[str, str] | str] = json.load(f)
                if self._validate_colors(loaded_colors):
                    logger.info("Loaded colors from wal cache")
                    return loaded_colors
                else:
                    logger.warning("Invalid colors in wal cache, trying backup")
            except Exception as e:
                logger.error(f"Error loading colors from wal cache: {e}")

        # Try to load last good colors
        if os.path.exists(self.last_good_colors_file):
            try:
                with open(self.last_good_colors_file, 'r', encoding="utf-8") as f:
                    backup_colors: dict[str, dict[str, str] | str] = json.load(f)
                if self._validate_colors(backup_colors):
                    logger.info("Loaded colors from last good backup")
                    return backup_colors
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
                        archived_colors: dict[str, dict[str, str] | str] = json.load(f)
                    if self._validate_colors(archived_colors):
                        logger.info(f"Loaded colors from backup: {backups[-1]}")
                        return archived_colors
        except Exception as e:
            logger.error(f"Error loading from backup: {e}")

        # Fall back to default colors
        logger.warning("Using default colors due to validation failures")
        return self._load_default_colors()

    def _load_default_colors(self) -> dict[str, dict[str, str] | str]:
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

    def get_colors(self) -> dict[str, dict[str, str] | str]:
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
            logger.error(traceback.format_exc())

    def check_restart_trigger(self) -> bool:
        """Check if qtile should restart due to color changes. Returns True if trigger was found."""
        try:
            if os.path.exists(self.restart_trigger_file):
                logger.info("Color change detected - restarting qtile")
                os.remove(self.restart_trigger_file)

                # Use qtile's built-in restart
                if hasattr(libqtile, 'qtile') and libqtile.qtile:
                    libqtile.qtile.restart()
                else:
                    # Fallback
                    _ = os.system("qtile cmd-obj -o cmd -f restart")
                return True
            return False
        except Exception as e:
            logger.error(f"Error in restart check: {e}")
            return False

    def setup_file_watcher(self):
        """Enhanced file watcher with better resource management"""
        try:
            from watchdog.observers.polling import PollingObserver
            # Use PollingObserver for better reliability across filesystems
            observer = PollingObserver(timeout=1.0)  # Check every 1 second instead of continuous
        except ImportError:
            try:
                # Fallback to regular Observer
                observer = Observer()
            except ImportError:
                logger.info("Watchdog not available, falling back to manual polling")
                return None

        class OptimizedColorsFileHandler(FileSystemEventHandler):
            color_manager: "ColorManager"
            last_update: float
            consecutive_errors: int
            debounce_timer: threading.Timer | None
            
            def __init__(self, color_manager: "ColorManager"):
                self.color_manager = color_manager
                self.last_update = 0
                self.consecutive_errors = 0
                self.debounce_timer = None

            def _handle_color_change(self, event_type: str):
                """Optimized color change handler with debouncing"""
                current_time = time.time()
                
                # Enhanced debouncing - only process if enough time has passed
                if current_time - self.last_update < 2.0:
                    logger.debug(f"Debouncing {event_type} event")
                    return
                
                self.last_update = current_time
                logger.info(f"Colors file {event_type}, scheduling update...")

                # Cancel any existing timer
                if self.debounce_timer and self.debounce_timer.is_alive():
                    self.debounce_timer.cancel()

                def optimized_update():
                    try:
                        # Reduced wait time for better responsiveness
                        time.sleep(0.8)
                        
                        # Verify file exists and is readable before updating
                        if not os.path.exists(self.color_manager.colors_file):
                            logger.warning("Colors file disappeared during update")
                            return
                            
                        # Check file size to ensure it's not empty/corrupted
                        try:
                            file_size = os.path.getsize(self.color_manager.colors_file)
                            if file_size < 50:  # Minimum reasonable JSON size
                                logger.warning(f"Colors file too small ({file_size} bytes), skipping update")
                                return
                        except OSError:
                            logger.warning("Cannot access colors file, skipping update")
                            return
                        
                        self.color_manager.update_colors()
                        self.consecutive_errors = 0
                        logger.debug("Color update completed successfully")
                        
                    except Exception as e:
                        self.consecutive_errors += 1
                        logger.error(f"Error in optimized color update: {e}")
                        
                        # Progressive error handling
                        if self.consecutive_errors > 3:
                            logger.warning(f"Multiple consecutive errors ({self.consecutive_errors}), increasing delays")
                        if self.consecutive_errors > 8:
                            logger.error("Too many consecutive errors, pausing updates temporarily")
                            time.sleep(30)  # Pause for 30 seconds

                # Use timer for better resource management
                self.debounce_timer = threading.Timer(0.1, optimized_update)
                self.debounce_timer.daemon = True
                self.debounce_timer.start()

            def on_modified(self, event):
                if event.is_directory or event.src_path != self.color_manager.colors_file:
                    return
                self._handle_color_change("modified")

            def on_created(self, event):
                if event.is_directory or event.src_path != self.color_manager.colors_file:
                    return
                self._handle_color_change("created")

            def on_moved(self, event):
                if event.is_directory or event.dest_path != self.color_manager.colors_file:
                    return
                self._handle_color_change("moved")

        event_handler = OptimizedColorsFileHandler(self)
        watch_dir = os.path.dirname(self.colors_file)
        
        try:
            observer.schedule(event_handler, watch_dir, recursive=False)
            observer.start()
            logger.info("Started optimized file watcher for color changes")
            return observer
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            return None

    def watch_colors_file(self):
        """Optimized file watching loop with exponential backoff and better resource management"""
        consecutive_errors = 0
        max_errors = 10
        check_interval = 2.0  # Start with 2-second intervals
        max_interval = 30.0   # Maximum 30-second intervals
        
        # Performance monitoring
        last_performance_log = time.time()
        update_count = 0

        try:
            # Ensure directories exist
            self._ensure_directories()

            # Try to use optimized watchdog first
            observer = self.setup_file_watcher()
            if observer:
                logger.info("Using optimized watchdog for file monitoring")
                observer_start_time = time.time()
                
                try:
                    while not self._shutdown_event.is_set():
                        if not observer.is_alive():
                            observer_uptime = time.time() - observer_start_time
                            logger.warning(f"Watchdog observer died after {observer_uptime:.1f}s, restarting...")
                            try:
                                observer.stop()
                                observer.join(timeout=3)
                            except Exception:
                                pass
                            
                            observer = self.setup_file_watcher()
                            if not observer:
                                logger.error("Failed to restart watchdog, falling back to polling")
                                break
                            observer_start_time = time.time()
                        
                        # Check every 5 seconds instead of 1 for better performance
                        self._shutdown_event.wait(5.0)
                        
                except Exception as e:
                    logger.error(f"Watchdog monitoring error: {e}")
                finally:
                    if observer and observer.is_alive():
                        try:
                            observer.stop()
                            observer.join(timeout=5)
                        except Exception as e:
                            logger.error(f"Error stopping observer: {e}")

            # Optimized polling fallback with exponential backoff
            logger.info("Using optimized polling for file monitoring")
            last_modified = 0
            last_hash = None
            last_size = 0

            if os.path.exists(self.colors_file):
                try:
                    stat = os.stat(self.colors_file)
                    last_modified = stat.st_mtime
                    last_size = stat.st_size
                    last_hash = self._get_file_hash(self.colors_file)
                except OSError as e:
                    logger.warning(f"Initial file stat failed: {e}")

            while not self._shutdown_event.is_set():
                loop_start = time.time()
                
                try:
                    file_changed = False
                    
                    if os.path.exists(self.colors_file):
                        try:
                            stat = os.stat(self.colors_file)
                            current_modified = stat.st_mtime
                            current_size = stat.st_size
                            
                            # Quick check: size or modification time changed
                            if current_modified != last_modified or current_size != last_size:
                                # Double-check with hash only if initial checks indicate change
                                current_hash = self._get_file_hash(self.colors_file)
                                if current_hash != last_hash and current_hash is not None:
                                    logger.info("Colors file changed (optimized polling detection)")
                                    file_changed = True
                                    
                                    # Verify file is complete and valid before updating
                                    if current_size > 50:  # Minimum reasonable size
                                        def optimized_delayed_update():
                                            try:
                                                # Shorter delay for better responsiveness
                                                time.sleep(0.8)
                                                
                                                # Final verification before update
                                                if os.path.exists(self.colors_file):
                                                    final_hash = self._get_file_hash(self.colors_file)
                                                    if final_hash == current_hash:
                                                        self.update_colors()
                                                        nonlocal update_count
                                                        update_count += 1
                                                    else:
                                                        logger.debug("File changed again during delay, skipping update")
                                                
                                                nonlocal consecutive_errors
                                                consecutive_errors = 0
                                                
                                            except Exception as e:
                                                consecutive_errors += 1
                                                logger.error(f"Error in optimized polling update: {e}")

                                        threading.Thread(target=optimized_delayed_update, daemon=True).start()
                                    else:
                                        logger.warning(f"Colors file too small ({current_size} bytes), skipping update")
                                
                                last_modified = current_modified
                                last_size = current_size
                                last_hash = current_hash
                        except OSError as e:
                            logger.warning(f"File stat error: {e}")
                            # Reset values on error
                            last_modified = 0
                            last_size = 0
                            last_hash = None
                    
                    # Dynamic interval adjustment with exponential backoff
                    if file_changed:
                        check_interval = 2.0  # Reset to fast checking after change
                    else:
                        # Gradually increase interval when no changes
                        check_interval = min(check_interval * 1.05, max_interval)
                    
                    consecutive_errors = 0
                    
                    # Performance logging every 5 minutes
                    current_time = time.time()
                    if current_time - last_performance_log > 300:
                        logger.debug(f"Polling performance: {update_count} updates, interval: {check_interval:.1f}s")
                        last_performance_log = current_time
                        update_count = 0
                    
                    # Efficient sleep with early wake on shutdown
                    if not self._shutdown_event.wait(check_interval):
                        continue

                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Optimized polling error: {e}")
                    
                    if consecutive_errors >= max_errors:
                        logger.error(f"Too many consecutive polling errors ({consecutive_errors}), stopping watcher")
                        break
                    
                    # Exponential backoff for errors
                    error_delay = min(2.0 ** consecutive_errors, 60.0)
                    logger.warning(f"Backing off for {error_delay:.1f}s due to error")
                    self._shutdown_event.wait(error_delay)

        except Exception as e:
            logger.error(f"Watch thread error: {e}")
            logger.error(traceback.format_exc())

    def restart_trigger_checker(self):
        """Optimized restart trigger checker with exponential backoff and better resource management"""
        consecutive_errors = 0
        max_errors = 10
        check_interval = 1.0  # Start with 1-second checks
        max_interval = 15.0   # Maximum 15-second intervals
        last_check_time = time.time()

        while not self._shutdown_event.is_set():
            loop_start = time.time()
            
            try:
                # Only check if enough time has passed (adaptive interval)
                if loop_start - last_check_time >= check_interval:
                    trigger_found = self.check_restart_trigger()
                    last_check_time = loop_start
                    
                    # Adjust interval based on activity
                    if trigger_found:
                        # If we found a trigger, reset to fast checking
                        check_interval = 1.0
                    else:
                        # Gradually increase interval when no triggers found
                        check_interval = min(check_interval * 1.02, max_interval)
                
                consecutive_errors = 0
                
                # Efficient sleep that can be interrupted by shutdown
                sleep_time = min(check_interval, 1.0)  # Never sleep more than 1 second at a time
                if self._shutdown_event.wait(sleep_time):
                    break  # Shutdown requested
                    
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in optimized restart trigger checker: {e}")
                
                if consecutive_errors >= max_errors:
                    logger.error(f"Too many consecutive restart checker errors ({consecutive_errors}), stopping")
                    break
                
                # Exponential backoff for errors, but cap at reasonable maximum
                error_delay = min(2.0 ** consecutive_errors, 30.0)
                logger.warning(f"Restart checker backing off for {error_delay:.1f}s due to error")
                
                if self._shutdown_event.wait(error_delay):
                    break

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
        """Start color file monitoring with improved error handling and resource management"""
        try:
            # Clear shutdown event
            self._shutdown_event.clear()

            # Check if monitoring is already active
            if self.is_monitoring():
                logger.info("Color monitoring is already active")
                return

            # Start color file watcher if not already running
            if self.watcher_thread is None or not self.watcher_thread.is_alive():
                logger.info("Starting optimized color file watcher...")
                self.watcher_thread = threading.Thread(
                    target=self.watch_colors_file, 
                    daemon=True,
                    name="ColorWatcher"
                )
                self.watcher_thread.start()
                logger.info("Optimized color file watcher started")

            # Start restart trigger checker if not already running
            if not hasattr(self, 'restart_checker_thread') or self.restart_checker_thread is None or not self.restart_checker_thread.is_alive():
                logger.info("Starting optimized restart trigger checker...")
                self.restart_checker_thread = threading.Thread(
                    target=self.restart_trigger_checker, 
                    daemon=True,
                    name="RestartChecker"
                )
                self.restart_checker_thread.start()
                logger.info("Optimized restart trigger checker started")

            # Verify threads started successfully
            time.sleep(0.1)  # Give threads a moment to start
            if not self.is_monitoring():
                logger.error("Failed to start color monitoring threads")
            else:
                logger.info("Color monitoring started successfully with performance optimizations")

        except Exception as e:
            logger.error(f"Error starting optimized color monitoring: {e}")
            logger.error(traceback.format_exc())

    def restart_monitoring(self):
        """Restart color monitoring with performance optimizations (useful for recovery)"""
        logger.info("Restarting color monitoring with optimizations...")
        
        # Get current status for debugging
        old_status = self.get_monitoring_status()
        logger.debug(f"Pre-restart status: {old_status}")
        
        # Stop existing monitoring
        self.stop_monitoring()
        
        # Apply performance optimizations
        self.optimize_monitoring_performance()
        
        # Wait a bit longer to ensure clean shutdown
        time.sleep(3)
        
        # Start fresh monitoring
        self.start_monitoring()
        
        # Verify restart was successful
        time.sleep(1)
        new_status = self.get_monitoring_status()
        logger.info(f"Post-restart status: monitoring_active={new_status['monitoring_active']}")
        
        if new_status['monitoring_active']:
            logger.info("Color monitoring restarted successfully with performance optimizations")
        else:
            logger.error("Failed to restart color monitoring")

    def is_monitoring(self):
        """Check if color monitoring is active"""
        watcher_running = self.watcher_thread is not None and self.watcher_thread.is_alive()
        checker_running = hasattr(
            self,
            'restart_checker_thread') and self.restart_checker_thread is not None and self.restart_checker_thread.is_alive()
        return watcher_running and checker_running

    def get_monitoring_status(self) -> dict[str, any]:
        """Get detailed monitoring status for diagnostics"""
        status = {
            'monitoring_active': self.is_monitoring(),
            'watcher_thread_alive': self.watcher_thread is not None and self.watcher_thread.is_alive(),
            'restart_checker_alive': hasattr(self, 'restart_checker_thread') and 
                                   self.restart_checker_thread is not None and 
                                   self.restart_checker_thread.is_alive(),
            'shutdown_event_set': self._shutdown_event.is_set(),
            'startup_time': getattr(self, '_startup_time', 0),
            'uptime_seconds': time.time() - getattr(self, '_startup_time', time.time()),
        }
        
        # Add thread names if available
        if self.watcher_thread and self.watcher_thread.is_alive():
            status['watcher_thread_name'] = getattr(self.watcher_thread, 'name', 'Unknown')
        if hasattr(self, 'restart_checker_thread') and self.restart_checker_thread and self.restart_checker_thread.is_alive():
            status['restart_checker_name'] = getattr(self.restart_checker_thread, 'name', 'Unknown')
            
        return status
    
    def optimize_monitoring_performance(self):
        """Apply runtime performance optimizations"""
        try:
            # Force garbage collection to free memory
            import gc
            collected = gc.collect()
            if collected > 0:
                logger.debug(f"Garbage collected {collected} objects")
            
            # Check and log current resource usage
            try:
                import resource
                memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                logger.debug(f"Current memory usage: {memory_usage} KB")
            except ImportError:
                pass
                
        except Exception as e:
            logger.warning(f"Error in performance optimization: {e}")
    
    def validate_colors_public(self, colors: dict[str, dict[str, str] | str]) -> bool:
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


def get_colors() -> dict[str, dict[str, str] | str]:
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


def get_color_file_status():
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


def get_monitoring_performance_status():
    """Get comprehensive monitoring performance status for debugging"""
    status = color_manager.get_monitoring_status()
    file_status = get_color_file_status()
    
    # Combine both status reports
    combined_status = {
        **status,
        **file_status,
        'performance_optimizations_active': True,
        'color_manager_type': type(color_manager).__name__,
    }
    
    return combined_status


def optimize_color_monitoring():
    """Manually trigger color monitoring performance optimizations"""
    color_manager.optimize_monitoring_performance()
    logger.info("Applied color monitoring performance optimizations")


def restart_color_monitoring_optimized():
    """Restart color monitoring with all performance optimizations"""
    color_manager.restart_monitoring()


# Load initial colors
color_manager.colordict = color_manager.load_colors()
