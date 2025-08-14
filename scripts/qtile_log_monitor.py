#!/usr/bin/env python3
"""
Qtile Log Monitor Script

@brief Set qtile log level and monitor log output in real-time
@author Andrath

This script provides functionality to:
- Set qtile log level using qtile CLI commands
- Tail and monitor qtile log files in real-time
- Support different log levels and output formats
- Cross-platform compatibility for qtile log locations

Usage:
    python3 scripts/qtile_log_monitor.py [OPTIONS]
    
Examples:
    # Monitor with default settings
    python3 scripts/qtile_log_monitor.py
    
    # Set debug level and monitor
    python3 scripts/qtile_log_monitor.py --level debug
    
    # Only tail log without changing level
    python3 scripts/qtile_log_monitor.py --no-set-level
    
    # Monitor specific number of lines
    python3 scripts/qtile_log_monitor.py --lines 100
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


class QtileLogMonitor:
    """
    @brief Monitor and manage qtile log output
    
    Provides functionality to set log levels via qtile CLI and monitor
    log files in real-time with various filtering and display options.
    """

    def __init__(self) -> None:
        """@brief Initialize qtile log monitor"""
        self.log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.qtile_cmd = self._find_qtile_command()
        self.log_path = self._find_log_path()

    def _find_qtile_command(self) -> str:
        """
        @brief Find qtile command executable
        @return Path to qtile command or 'qtile' as fallback
        """
        # Try common qtile command locations
        possible_commands = ["qtile", "qtile-cmd", "python3 -m qtile"]
        
        for cmd in possible_commands:
            try:
                # Test if command exists and works
                result = subprocess.run(
                    f"{cmd} --help",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"✅ Found qtile command: {cmd}")
                    return cmd
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue
        
        print("⚠️  Could not verify qtile command - using 'qtile' as fallback")
        return "qtile"

    def _find_log_path(self) -> Path | None:
        """
        @brief Find qtile log file location
        @return Path to qtile log file or None if not found
        """
        # Common qtile log locations
        possible_paths = [
            # XDG standard locations
            Path.home() / ".cache" / "qtile" / "qtile.log",
            Path.home() / ".local" / "share" / "qtile" / "qtile.log",
            
            # Legacy/alternative locations  
            Path.home() / ".qtile" / "qtile.log",
            Path("/tmp") / f"qtile-{os.getuid()}" / "qtile.log",
            Path("/var/log") / "qtile" / "qtile.log",
            
            # Check if qtile is running and has a log
            Path("/tmp") / "qtile.log",
        ]
        
        # Try to get log path from qtile itself
        try:
            result = subprocess.run(
                f"{self.qtile_cmd} cmd-obj -o core -f info",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "log" in result.stdout.lower():
                print(f"📋 Qtile info: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        # Check each possible path
        for log_path in possible_paths:
            if log_path.exists() and log_path.is_file():
                print(f"📄 Found qtile log: {log_path}")
                return log_path
        
        print("❌ Could not find qtile log file")
        print("💡 Possible locations checked:")
        for path in possible_paths:
            print(f"   - {path}")
        return None

    def set_log_level(self, level: str) -> bool:
        """
        @brief Set qtile log level using CLI
        @param level: Log level to set (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        @return True if successful, False otherwise
        """
        level = level.upper()
        if level not in self.log_levels:
            print(f"❌ Invalid log level: {level}")
            print(f"Valid levels: {', '.join(self.log_levels)}")
            return False
        
        print(f"🔧 Setting qtile log level to: {level}")
        
        try:
            # Try different qtile CLI approaches to set log level
            commands_to_try = [
                f"{self.qtile_cmd} cmd-obj -o core -f set_log_level -a {level}",
                f"{self.qtile_cmd} shell -c \"qtile.core.set_log_level('{level}')\"",
                f"{self.qtile_cmd} cmd-obj -o cmd -f set_log_level -a {level}",
            ]
            
            for cmd in commands_to_try:
                try:
                    print(f"⚙️  Trying command: {cmd}")
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ Successfully set log level to {level}")
                        if result.stdout.strip():
                            print(f"📤 Output: {result.stdout.strip()}")
                        return True
                    else:
                        print(f"⚠️  Command failed with return code {result.returncode}")
                        if result.stderr.strip():
                            print(f"📥 Error: {result.stderr.strip()}")
                            
                except subprocess.TimeoutExpired:
                    print(f"⏰ Command timed out: {cmd}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error setting log level: {e}")
        
        print(f"❌ Could not set log level to {level}")
        print("💡 Try setting log level manually in qtile config or using qtile shell")
        return False

    def tail_log(self, lines: int = 50, follow: bool = True) -> None:
        """
        @brief Tail qtile log file
        @param lines: Number of initial lines to show
        @param follow: Whether to follow the log file for new entries
        """
        if not self.log_path or not self.log_path.exists():
            print("❌ No qtile log file found to monitor")
            return
        
        print(f"📖 Monitoring qtile log: {self.log_path}")
        print(f"📊 Showing last {lines} lines{' and following...' if follow else ''}")
        print("🛑 Press Ctrl+C to stop")
        print("-" * 60)
        
        try:
            if follow:
                # Use tail -f equivalent
                cmd = ["tail", "-f", "-n", str(lines), str(self.log_path)]
            else:
                # Just show last N lines
                cmd = ["tail", "-n", str(lines), str(self.log_path)]
            
            # Try to use system tail command first
            try:
                subprocess.run(cmd, check=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                # Fallback to Python implementation
                print("📝 Using Python log monitoring (system 'tail' not available)")
                self._python_tail(lines, follow)
                
        except KeyboardInterrupt:
            print("\n🛑 Log monitoring stopped")

    def _python_tail(self, lines: int, follow: bool) -> None:
        """
        @brief Python implementation of tail functionality
        @param lines: Number of lines to show initially
        @param follow: Whether to follow the file
        """
        if not self.log_path:
            return
            
        try:
            with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read initial lines
                all_lines = f.readlines()
                if len(all_lines) > lines:
                    initial_lines = all_lines[-lines:]
                else:
                    initial_lines = all_lines
                
                # Print initial lines
                for line in initial_lines:
                    print(line.rstrip())
                
                if not follow:
                    return
                
                # Follow the file for new content
                f.seek(0, 2)  # Seek to end
                while True:
                    line = f.readline()
                    if line:
                        print(line.rstrip())
                    else:
                        time.sleep(0.1)
                        
        except Exception as e:
            print(f"❌ Error reading log file: {e}")

    def show_log_info(self) -> None:
        """@brief Show information about qtile logging setup"""
        print("🔍 Qtile Log Monitor Information")
        print("=" * 50)
        print(f"Qtile command: {self.qtile_cmd}")
        print(f"Log file: {self.log_path or 'Not found'}")
        print(f"Available log levels: {', '.join(self.log_levels)}")
        print()
        
        if self.log_path and self.log_path.exists():
            stat = self.log_path.stat()
            print(f"Log file size: {stat.st_size} bytes")
            print(f"Last modified: {time.ctime(stat.st_mtime)}")
        
        # Try to get current qtile status
        try:
            result = subprocess.run(
                f"{self.qtile_cmd} cmd-obj -o core -f info",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("🎯 Current qtile status:")
                print(result.stdout.strip())
        except:
            print("⚠️  Could not get current qtile status")


def main() -> None:
    """@brief Main entry point for qtile log monitor"""
    parser = argparse.ArgumentParser(
        description="Monitor qtile logs with configurable log level",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Monitor with default settings
  %(prog)s --level debug            # Set debug level and monitor  
  %(prog)s --no-set-level           # Only tail without changing level
  %(prog)s --lines 100 --no-follow  # Show 100 lines without following
  %(prog)s --info                   # Show log configuration info
        """
    )
    
    parser.add_argument(
        "--level", "-l",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="Set qtile log level (default: info)"
    )
    
    parser.add_argument(
        "--lines", "-n",
        type=int,
        default=50,
        help="Number of initial log lines to show (default: 50)"
    )
    
    parser.add_argument(
        "--no-follow", "-f",
        action="store_true",
        help="Don't follow log file for new entries"
    )
    
    parser.add_argument(
        "--no-set-level",
        action="store_true", 
        help="Don't attempt to set log level, just monitor"
    )
    
    parser.add_argument(
        "--info", "-i",
        action="store_true",
        help="Show qtile log configuration info and exit"
    )
    
    args = parser.parse_args()
    
    # Create monitor instance
    monitor = QtileLogMonitor()
    
    # Show info and exit if requested
    if args.info:
        monitor.show_log_info()
        return
    
    # Set log level unless disabled
    if not args.no_set_level:
        if not monitor.set_log_level(args.level):
            print("⚠️  Continuing with log monitoring despite level setting failure...")
    
    # Monitor the log
    try:
        monitor.tail_log(lines=args.lines, follow=not args.no_follow)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
