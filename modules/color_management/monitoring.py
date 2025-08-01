#!/usr/bin/env python3
"""
Color file monitoring and watching functionality
"""

import os
import threading
import time
from typing import Optional, Callable, Any
from libqtile.log_utils import logger

try:
    from watchdog.observers import Observer
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    PollingObserver = None
    FileSystemEventHandler = None

from .utils import get_file_hash


class OptimizedColorsFileHandler:
    """Optimized file system event handler for color file changes"""
    
    def __init__(self, colors_file: str, update_callback: Callable[[], None]):
        self.colors_file = colors_file
        self.update_callback = update_callback
        self.last_update = 0
        self.consecutive_errors = 0
        self.debounce_timer: Optional[threading.Timer] = None

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
                if not os.path.exists(self.colors_file):
                    logger.warning("Colors file disappeared during update")
                    return
                    
                # Check file size to ensure it's not empty/corrupted
                try:
                    file_size = os.path.getsize(self.colors_file)
                    if file_size < 50:  # Minimum reasonable JSON size
                        logger.warning(f"Colors file too small ({file_size} bytes), skipping update")
                        return
                except OSError:
                    logger.warning("Cannot access colors file, skipping update")
                    return
                
                self.update_callback()
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
        if hasattr(event, 'is_directory') and event.is_directory:
            return
        if hasattr(event, 'src_path') and event.src_path != self.colors_file:
            return
        self._handle_color_change("modified")

    def on_created(self, event):
        if hasattr(event, 'is_directory') and event.is_directory:
            return
        if hasattr(event, 'src_path') and event.src_path != self.colors_file:
            return
        self._handle_color_change("created")

    def on_moved(self, event):
        if hasattr(event, 'is_directory') and event.is_directory:
            return
        if hasattr(event, 'dest_path') and event.dest_path != self.colors_file:
            return
        self._handle_color_change("moved")


class FileWatcher:
    """Manages file watching with optimized performance"""
    
    def __init__(self, colors_file: str, update_callback: Callable[[], None], 
                 shutdown_event: threading.Event):
        self.colors_file = colors_file
        self.update_callback = update_callback
        self.shutdown_event = shutdown_event
        self.observer: Optional[Any] = None

    def setup_watchdog_observer(self) -> Optional[Any]:
        """Setup enhanced file watcher with better resource management"""
        if not WATCHDOG_AVAILABLE:
            logger.info("Watchdog not available, falling back to manual polling")
            return None

        try:
            # Use PollingObserver for better reliability across filesystems
            observer = PollingObserver(timeout=1.0)  # Check every 1 second
        except Exception:
            try:
                # Fallback to regular Observer
                observer = Observer()
            except Exception:
                logger.info("Watchdog not available, falling back to manual polling")
                return None

        event_handler = OptimizedColorsFileHandler(self.colors_file, self.update_callback)
        watch_dir = os.path.dirname(self.colors_file)
        
        try:
            observer.schedule(event_handler, watch_dir, recursive=False)
            observer.start()
            logger.info("Started optimized file watcher for color changes")
            return observer
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            return None

    def watch_with_watchdog(self) -> bool:
        """Monitor using watchdog with fallback handling"""
        observer = self.setup_watchdog_observer()
        if not observer:
            return False

        observer_start_time = time.time()
        
        try:
            while not self.shutdown_event.is_set():
                if not observer.is_alive():
                    observer_uptime = time.time() - observer_start_time
                    logger.warning(f"Watchdog observer died after {observer_uptime:.1f}s, restarting...")
                    try:
                        observer.stop()
                        observer.join(timeout=3)
                    except Exception:
                        pass
                    
                    observer = self.setup_watchdog_observer()
                    if not observer:
                        logger.error("Failed to restart watchdog, falling back to polling")
                        return False
                    observer_start_time = time.time()
                
                # Check every 5 seconds instead of 1 for better performance
                self.shutdown_event.wait(5.0)
                
        except Exception as e:
            logger.error(f"Watchdog monitoring error: {e}")
            return False
        finally:
            if observer and observer.is_alive():
                try:
                    observer.stop()
                    observer.join(timeout=5)
                except Exception as e:
                    logger.error(f"Error stopping observer: {e}")
        
        return True

    def watch_with_polling(self):
        """Optimized polling fallback with exponential backoff"""
        logger.info("Using optimized polling for file monitoring")
        
        consecutive_errors = 0
        max_errors = 10
        check_interval = 2.0  # Start with 2-second intervals
        max_interval = 30.0   # Maximum 30-second intervals
        
        # Performance monitoring
        last_performance_log = time.time()
        update_count = 0
        
        last_modified = 0
        last_hash = None
        last_size = 0

        if os.path.exists(self.colors_file):
            try:
                stat = os.stat(self.colors_file)
                last_modified = stat.st_mtime
                last_size = stat.st_size
                last_hash = get_file_hash(self.colors_file)
            except OSError as e:
                logger.warning(f"Initial file stat failed: {e}")

        while not self.shutdown_event.is_set():
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
                            current_hash = get_file_hash(self.colors_file)
                            if current_hash != last_hash and current_hash is not None:
                                logger.info("Colors file changed (optimized polling detection)")
                                file_changed = True
                                
                                # Verify file is complete and valid before updating
                                if current_size > 50:  # Minimum reasonable size
                                    def delayed_update():
                                        try:
                                            # Shorter delay for better responsiveness
                                            time.sleep(0.8)
                                            
                                            # Final verification before update
                                            if os.path.exists(self.colors_file):
                                                final_hash = get_file_hash(self.colors_file)
                                                if final_hash == current_hash:
                                                    self.update_callback()
                                                    nonlocal update_count
                                                    update_count += 1
                                                else:
                                                    logger.debug("File changed again during delay, skipping update")
                                            
                                            nonlocal consecutive_errors
                                            consecutive_errors = 0
                                            
                                        except Exception as e:
                                            consecutive_errors += 1
                                            logger.error(f"Error in optimized polling update: {e}")

                                    threading.Thread(target=delayed_update, daemon=True).start()
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
                if not self.shutdown_event.wait(check_interval):
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
                self.shutdown_event.wait(error_delay)

    def start_watching(self):
        """Start file watching with automatic fallback"""
        try:
            # Try watchdog first, fall back to polling if it fails
            if WATCHDOG_AVAILABLE:
                logger.info("Attempting to use optimized watchdog for file monitoring")
                if self.watch_with_watchdog():
                    return
            
            # Fallback to polling
            self.watch_with_polling()
            
        except Exception as e:
            logger.error(f"Error in file watching: {e}")


class RestartTriggerChecker:
    """Handles restart trigger file checking with optimized performance"""
    
    def __init__(self, restart_trigger_file: str, check_callback: Callable[[], bool], 
                 shutdown_event: threading.Event):
        self.restart_trigger_file = restart_trigger_file
        self.check_callback = check_callback
        self.shutdown_event = shutdown_event

    def start_checking(self):
        """Optimized restart trigger checker with exponential backoff"""
        consecutive_errors = 0
        max_errors = 10
        check_interval = 1.0  # Start with 1-second checks
        max_interval = 15.0   # Maximum 15-second intervals
        last_check_time = time.time()

        while not self.shutdown_event.is_set():
            try:
                # Only check if enough time has passed (adaptive interval)
                current_time = time.time()
                if current_time - last_check_time >= check_interval:
                    trigger_found = self.check_callback()
                    last_check_time = current_time
                    
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
                if self.shutdown_event.wait(sleep_time):
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
                
                if self.shutdown_event.wait(error_delay):
                    break
