#!/usr/bin/env python3
"""
Simple X11 compositor for transparency effects
Lightweight replacement for picom focused on transparency only

@brief Simple X11 compositor using xcffib for transparency effects
@author qtile configuration system
"""

import threading
import time

import xcffib
import xcffib.xproto
from libqtile.log_utils import logger


class SimpleCompositor:
    """
    @brief Lightweight compositor for window transparency effects
    
    Provides basic window transparency functionality using X11 properties.
    Designed to replace picom for users who only need transparency effects.
    """
    
    def __init__(self, config: object) -> None:
        """
        @param config Configuration object containing compositor settings
        """
        self.config = config
        self.conn: xcffib.Connection | None = None
        self.root: int | None = None
        self.running = False
        self.windows: dict[int, dict[str, object]] = {}
        self.transparency_rules: dict[str, float] = {}
        self._event_thread: threading.Thread | None = None
        
        # Load transparency rules from config
        if hasattr(config, 'compositor_settings'):
            compositor_settings = getattr(config, 'compositor_settings')
            transparency_config = compositor_settings.get('transparency', {})
            if transparency_config.get('enabled', True):
                for rule in transparency_config.get('rules', []):
                    wm_class = rule.get('wm_class', '')
                    opacity = rule.get('opacity', 1.0)
                    if wm_class:
                        self.transparency_rules[wm_class.lower()] = opacity
        
        logger.debug(f"Loaded transparency rules: {self.transparency_rules}")

    def start(self) -> bool:
        """
        @brief Start the compositor
        @return True if successfully started, False otherwise
        """
        try:
            # Connect to X11
            self.conn = xcffib.connect()
            if not self.conn:
                logger.error("Failed to connect to X11 display")
                return False
                
            # Get root window - suppress type checking for xcffib internals
            setup = self.conn.get_setup()
            self.root = setup.roots[0].root  # type: ignore[attr-defined]
            
            # Check if we can set window properties
            if not self._test_x11_capabilities():
                logger.error("X11 capabilities test failed")
                return False
            
            self.running = True
            
            # Start event monitoring thread
            self._event_thread = threading.Thread(
                target=self._monitor_windows, 
                daemon=True,
                name="SimpleCompositor"
            )
            self._event_thread.start()
            
            # Apply transparency to existing windows
            self._apply_transparency_to_existing_windows()
            
            logger.info("Simple compositor started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start compositor: {e}")
            self.stop()
            return False

    def stop(self) -> None:
        """@brief Stop the compositor and clean up resources"""
        self.running = False
        
        if self._event_thread and self._event_thread.is_alive():
            self._event_thread.join(timeout=2.0)
            
        if self.conn:
            try:
                self.conn.disconnect()
            except Exception as e:
                logger.debug(f"Error disconnecting from X11: {e}")
            finally:
                self.conn = None
                
        logger.info("Simple compositor stopped")

    def reload_config(self, new_config: object) -> None:
        """
        @brief Reload compositor configuration without restarting
        @param new_config New configuration object
        """
        self.config = new_config
        self.transparency_rules.clear()
        
        # Reload transparency rules
        if hasattr(new_config, 'compositor_settings'):
            compositor_settings = getattr(new_config, 'compositor_settings')
            transparency_config = compositor_settings.get('transparency', {})
            if transparency_config.get('enabled', True):
                for rule in transparency_config.get('rules', []):
                    wm_class = rule.get('wm_class', '')
                    opacity = rule.get('opacity', 1.0)
                    if wm_class:
                        self.transparency_rules[wm_class.lower()] = opacity
        
        # Reapply transparency to all windows
        self._apply_transparency_to_existing_windows()
        logger.info("Compositor configuration reloaded")

    def set_window_opacity(self, window_id: int, opacity: float) -> bool:
        """
        @brief Set opacity for a specific window
        @param window_id X11 window ID
        @param opacity Opacity value (0.0 = transparent, 1.0 = opaque)
        @return True if successfully set, False otherwise
        """
        if not self.conn or not self.running:
            return False
            
        try:
            # Clamp opacity to valid range
            opacity = max(0.0, min(1.0, opacity))
            
            # Convert to X11 opacity value (0 to 0xffffffff)
            x11_opacity = int(opacity * 0xffffffff)
            
            # Get the _NET_WM_WINDOW_OPACITY atom
            opacity_atom = self._get_atom("_NET_WM_WINDOW_OPACITY")
            cardinal_atom = self._get_atom("CARDINAL")
            
            if opacity_atom and cardinal_atom:
                # Set the property
                self.conn.core.ChangeProperty(
                    xcffib.xproto.PropMode.Replace,
                    window_id,
                    opacity_atom,
                    cardinal_atom,
                    32,  # Format: 32-bit
                    1,   # Length: 1 element
                    [x11_opacity]
                )
                self.conn.flush()
                logger.debug(f"Set window {window_id} opacity to {opacity}")
                return True
                
        except Exception as e:
            logger.debug(f"Failed to set window opacity: {e}")
            
        return False

    def _test_x11_capabilities(self) -> bool:
        """@brief Test if we can perform required X11 operations"""
        try:
            # Test if we can get atoms
            test_atom = self._get_atom("WM_CLASS")
            return test_atom is not None
        except Exception as e:
            logger.debug(f"X11 capabilities test failed: {e}")
            return False

    def _get_atom(self, name: str) -> int | None:
        """
        @brief Get X11 atom for given name
        @param name Atom name
        @return Atom ID or None if failed
        """
        try:
            if not self.conn:
                return None
                
            cookie = self.conn.core.InternAtom(False, len(name), name)
            reply = cookie.reply()
            return reply.atom if reply else None
            
        except Exception as e:
            logger.debug(f"Failed to get atom {name}: {e}")
            return None

    def _get_window_class(self, window_id: int) -> str | None:
        """
        @brief Get WM_CLASS property for window
        @param window_id X11 window ID
        @return Window class or None if failed
        """
        try:
            if not self.conn:
                return None
                
            wm_class_atom = self._get_atom("WM_CLASS")
            if not wm_class_atom:
                return None
                
            cookie = self.conn.core.GetProperty(
                False,  # delete
                window_id,
                wm_class_atom,
                xcffib.xproto.Atom.STRING,
                0,  # long_offset
                1024  # long_length
            )
            
            reply = cookie.reply()
            if reply and reply.value:
                # WM_CLASS contains instance\0class\0
                value = bytes(reply.value).decode('utf-8', errors='ignore')
                parts = value.split('\0')
                if len(parts) >= 2:
                    return parts[1]  # Return class name (second part)
                    
        except Exception as e:
            logger.debug(f"Failed to get window class for {window_id}: {e}")
            
        return None

    def _apply_transparency_to_window(self, window_id: int) -> None:
        """
        @brief Apply transparency rule to a specific window
        @param window_id X11 window ID
        """
        wm_class = self._get_window_class(window_id)
        if not wm_class:
            return
            
        wm_class_lower = wm_class.lower()
        if wm_class_lower in self.transparency_rules:
            opacity = self.transparency_rules[wm_class_lower]
            if self.set_window_opacity(window_id, opacity):
                logger.debug(f"Applied transparency {opacity} to {wm_class} (window {window_id})")

    def _apply_transparency_to_existing_windows(self) -> None:
        """@brief Apply transparency to all existing windows"""
        try:
            if not self.conn or not self.root:
                return
                
            # Get all windows
            cookie = self.conn.core.QueryTree(self.root)
            reply = cookie.reply()
            
            if reply and reply.children:
                for window_id in reply.children:
                    self._apply_transparency_to_window(window_id)
                    
        except Exception as e:
            logger.debug(f"Failed to apply transparency to existing windows: {e}")

    def _monitor_windows(self) -> None:
        """@brief Monitor window events and apply transparency as needed"""
        try:
            if not self.conn or not self.root:
                return
                
            # Subscribe to window events
            self.conn.core.ChangeWindowAttributes(
                self.root,
                xcffib.xproto.CW.EventMask,
                [xcffib.xproto.EventMask.SubstructureNotify]
            )
            self.conn.flush()
            
            logger.debug("Started monitoring window events")
            
            while self.running:
                try:
                    # Poll for events (non-blocking)
                    event = self.conn.poll_for_event()
                    if event:
                        self._handle_x11_event(event)
                    else:
                        # No events, sleep briefly to avoid busy waiting
                        time.sleep(0.01)
                        
                except Exception as e:
                    logger.debug(f"Error in window monitoring: {e}")
                    time.sleep(0.1)  # Sleep longer on error
                    
        except Exception as e:
            logger.error(f"Window monitoring thread failed: {e}")

    def _handle_x11_event(self, event: object) -> None:
        """
        @brief Handle X11 events
        @param event X11 event object
        """
        try:
            # Handle window creation events
            if hasattr(event, 'event') and hasattr(event, 'window'):
                event_window = getattr(event, 'event')
                window_id = getattr(event, 'window')
                if event_window == self.root:  # Event on root window
                    # New window created, apply transparency
                    self._apply_transparency_to_window(window_id)
                    
        except Exception as e:
            logger.debug(f"Error handling X11 event: {e}")


# Global compositor instance
_compositor_instance: SimpleCompositor | None = None


def start_compositor(config: object) -> bool:
    """
    @brief Start the global compositor instance
    @param config Configuration object
    @return True if started successfully
    """
    global _compositor_instance
    
    if _compositor_instance and _compositor_instance.running:
        logger.warning("Compositor already running")
        return True
        
    # Check if compositor is enabled in config
    if hasattr(config, 'compositor_settings'):
        compositor_settings = getattr(config, 'compositor_settings')
        if not compositor_settings.get('enabled', False):
            logger.info("Compositor disabled in configuration")
            return False
    else:
        logger.info("No compositor settings found, compositor disabled")
        return False
    
    _compositor_instance = SimpleCompositor(config)
    return _compositor_instance.start()


def stop_compositor() -> None:
    """@brief Stop the global compositor instance"""
    global _compositor_instance
    
    if _compositor_instance:
        _compositor_instance.stop()
        _compositor_instance = None


def reload_compositor_config(config: object) -> None:
    """
    @brief Reload compositor configuration
    @param config New configuration object
    """
    global _compositor_instance
    
    if _compositor_instance and _compositor_instance.running:
        _compositor_instance.reload_config(config)


def is_compositor_running() -> bool:
    """
    @brief Check if compositor is currently running
    @return True if running, False otherwise
    """
    global _compositor_instance
    return _compositor_instance is not None and _compositor_instance.running


def toggle_compositor(config: object) -> bool:
    """
    @brief Toggle compositor on/off
    @param config Configuration object
    @return True if now running, False if stopped
    """
    if is_compositor_running():
        stop_compositor()
        return False
    else:
        return start_compositor(config)