#!/usr/bin/env python3
"""
Startup hooks for qtile
"""

import os
import subprocess
from libqtile import hook, qtile
from libqtile.log_utils import logger


class StartupHooks:
    """Handles startup-related hooks and autostart functionality"""
    
    def __init__(self, config, color_manager, window_manager):
        self.config = config
        self.color_manager = color_manager
        self.window_manager = window_manager

    def setup_startup_hooks(self):
        """Setup all startup-related hooks"""
        logger.debug("Setting up startup hooks")
        
        @hook.subscribe.startup_once
        def start_color_watcher():
            """Start the color file watcher when qtile starts"""
            logger.info("Qtile startup_once hook called")

        @hook.subscribe.startup_once
        def run_autostart():
            """Run autostart script when qtile starts"""
            self.run_autostart_script()

        @hook.subscribe.startup_complete
        def setup_color_watching():
            """Additional setup after qtile is fully loaded"""
            logger.info("Qtile startup completed - starting color monitoring")
            self.color_manager.start_monitoring()

        @hook.subscribe.startup_complete
        def enforce_tiling_on_restart():
            """Force all windows to tile after qtile restart (except explicitly floating ones)"""
            self._schedule_window_retiling()

    def run_autostart_script(self):
        """Run the autostart script"""
        autostart_script = self.config.autostart_script

        if os.path.exists(autostart_script) and os.access(autostart_script, os.X_OK):
            try:
                logger.info(f"Running autostart script: {autostart_script}")
                # Run completely detached - don't wait for completion
                subprocess.Popen([autostart_script],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL,
                                 stdin=subprocess.DEVNULL,
                                 start_new_session=True)
                logger.info("Autostart script launched successfully")
            except Exception as e:
                logger.error(f"Failed to launch autostart script: {e}")
        else:
            logger.error(f"Autostart script not found or not executable: {autostart_script}")

    def _schedule_window_retiling(self):
        """Schedule window retiling with a delay"""
        def retile_windows():
            if qtile:
                try:
                    retiled_count = self.window_manager.retile_windows_after_startup(qtile)
                    logger.info(f"Startup retiling completed - {retiled_count} windows processed")
                except Exception as e:
                    logger.error(f"Error during startup window retiling: {e}")

        # Schedule retiling with a small delay to ensure all windows are restored
        if qtile:
            qtile.call_later(1.0, retile_windows)

    def validate_autostart_script(self) -> dict:
        """Validate the autostart script configuration"""
        validation = {
            'valid': True,
            'exists': False,
            'executable': False,
            'path': self.config.autostart_script,
            'errors': []
        }

        try:
            script_path = self.config.autostart_script
            
            if os.path.exists(script_path):
                validation['exists'] = True
                
                if os.access(script_path, os.X_OK):
                    validation['executable'] = True
                else:
                    validation['errors'].append("Autostart script is not executable")
                    validation['valid'] = False
            else:
                validation['errors'].append("Autostart script does not exist")
                validation['valid'] = False

        except AttributeError:
            validation['errors'].append("No autostart script configured")
            validation['valid'] = False
        except Exception as e:
            validation['errors'].append(f"Error checking autostart script: {e}")
            validation['valid'] = False

        return validation

    def get_startup_status(self) -> dict:
        """Get status of startup components"""
        return {
            'color_monitoring': self.color_manager.is_monitoring() if self.color_manager else False,
            'autostart_validation': self.validate_autostart_script(),
            'hooks_registered': self._count_registered_hooks()
        }

    def _count_registered_hooks(self) -> dict:
        """Count registered startup hooks"""
        # This is a simplified count - in practice, qtile doesn't expose hook counts easily
        return {
            'startup_once': 2,  # start_color_watcher, run_autostart
            'startup_complete': 2  # setup_color_watching, enforce_tiling_on_restart
        }
