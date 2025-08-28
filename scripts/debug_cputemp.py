#!/usr/bin/env python3
"""
CPU Temperature Script Debugger

@brief Debug script for troubleshooting cputemp widget issues after qtile restart
@author Andrath

This script helps diagnose why the cputemp script widget shows N/A after qtile restart.
It checks various aspects of the script environment, permissions, and execution.
"""

import os
import subprocess
import time
from pathlib import Path


def test_script_execution():
    """Test the cputemp script execution in various ways"""
    print("🔍 CPU Temperature Script Debugger")
    print("=" * 50)

    # 1. Check script path resolution
    script_path = "~/bin/cputemp"
    expanded_path = Path(script_path).expanduser()

    print(f"Script path: {script_path}")
    print(f"Expanded path: {expanded_path}")
    print(f"Script exists: {expanded_path.exists()}")

    if expanded_path.exists():
        stat = expanded_path.stat()
        print(f"Script permissions: {oct(stat.st_mode)[-3:]}")
        print(f"Script is executable: {os.access(expanded_path, os.X_OK)}")
        print(f"Script owner: uid={stat.st_uid}, gid={stat.st_gid}")
        print(f"Current user: uid={os.getuid()}, gid={os.getgid()}")

    print()

    # 2. Check environment differences
    print("Environment Information:")
    print("-" * 25)
    print(f"Current working directory: {os.getcwd()}")
    print(f"HOME: {os.environ.get('HOME', 'Not set')}")
    print(f"PATH: {os.environ.get('PATH', 'Not set')[:100]}...")
    print(f"USER: {os.environ.get('USER', 'Not set')}")
    print(f"SHELL: {os.environ.get('SHELL', 'Not set')}")

    # Check for display-related environment that might affect script
    display_vars = ['DISPLAY', 'WAYLAND_DISPLAY', 'XDG_SESSION_TYPE']
    for var in display_vars:
        print(f"{var}: {os.environ.get(var, 'Not set')}")

    print()

    # 3. Test script execution methods
    print("Script Execution Tests:")
    print("-" * 25)

    if not expanded_path.exists():
        print("❌ Script does not exist - cannot test execution")
        return

    # Test 1: Direct execution
    try:
        print("Test 1: Direct execution with full path")
        start_time = time.time()
        result = subprocess.run(
            [str(expanded_path)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.expanduser("~")
        )
        execution_time = time.time() - start_time

        print(f"  Return code: {result.returncode}")
        print(f"  Execution time: {execution_time:.2f}s")
        print(f"  stdout: '{result.stdout.strip()}'")
        if result.stderr.strip():
            print(f"  stderr: '{result.stderr.strip()}'")

    except subprocess.TimeoutExpired:
        print("  ❌ Script timed out (>10s)")
    except Exception as e:
        print(f"  ❌ Execution failed: {e}")

    print()

    # Test 2: Shell execution
    try:
        print("Test 2: Shell execution")
        start_time = time.time()
        result = subprocess.run(
            f"cd ~ && {script_path}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        execution_time = time.time() - start_time

        print(f"  Return code: {result.returncode}")
        print(f"  Execution time: {execution_time:.2f}s")
        print(f"  stdout: '{result.stdout.strip()}'")
        if result.stderr.strip():
            print(f"  stderr: '{result.stderr.strip()}'")

    except subprocess.TimeoutExpired:
        print("  ❌ Script timed out (>10s)")
    except Exception as e:
        print(f"  ❌ Execution failed: {e}")

    print()

    # Test 3: Check temperature sources directly
    print("Temperature Source Analysis:")
    print("-" * 30)

    # Common temperature file locations
    temp_paths = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/thermal/thermal_zone1/temp",
        "/sys/class/hwmon/hwmon0/temp1_input",
        "/sys/class/hwmon/hwmon1/temp1_input",
        "/sys/class/hwmon/hwmon2/temp1_input",
    ]

    print("Checking common temperature sensor paths:")
    for temp_path in temp_paths:
        path_obj = Path(temp_path)
        if path_obj.exists():
            try:
                with open(temp_path) as f:
                    temp_raw = f.read().strip()
                temp_celsius = int(temp_raw) / 1000
                print(f"  ✅ {temp_path}: {temp_celsius:.1f}°C")
            except Exception as e:
                print(f"  ❌ {temp_path}: exists but error reading - {e}")
        else:
            print(f"  ⚫ {temp_path}: not found")

    # Check if sensors command is available
    print()
    print("Checking 'sensors' command availability:")
    try:
        result = subprocess.run(["which", "sensors"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ sensors found at: {result.stdout.strip()}")

            # Try running sensors
            result = subprocess.run(["sensors"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print(f"  ✅ sensors output ({len(lines)} lines):")
                # Show first few lines
                for line in lines[:5]:
                    if line.strip():
                        print(f"    {line}")
                if len(lines) > 5:
                    print(f"    ... and {len(lines) - 5} more lines")
            else:
                print(f"  ❌ sensors command failed: {result.stderr.strip()}")
        else:
            print("  ⚫ sensors command not found")
    except Exception as e:
        print(f"  ❌ Error checking sensors: {e}")

    print()

    # 4. Qtile environment simulation
    print("Qtile Environment Simulation:")
    print("-" * 32)

    try:
        print("Simulating qtile script execution environment...")

        # This mimics how qtile's GenPollText calls the script
        def qtile_style_call():
            script_path_obj = Path(script_path).expanduser()
            result = subprocess.run(
                [str(script_path_obj)],
                capture_output=True,
                text=True,
                timeout=10,
                # Simulate qtile's environment - minimal environment
                env={
                    'HOME': os.environ.get('HOME', ''),
                    'PATH': os.environ.get('PATH', ''),
                    'USER': os.environ.get('USER', ''),
                }
            )
            return result

        start_time = time.time()
        result = qtile_style_call()
        execution_time = time.time() - start_time

        print(f"  Return code: {result.returncode}")
        print(f"  Execution time: {execution_time:.2f}s")
        print(f"  stdout: '{result.stdout.strip()}'")
        if result.stderr.strip():
            print(f"  stderr: '{result.stderr.strip()}'")

        if result.stdout.strip() == "N/A" or not result.stdout.strip():
            print("  ⚠️  Script returns N/A or empty - this matches the problem!")
        elif result.returncode != 0:
            print("  ⚠️  Script failed - this could be the issue")
        else:
            print("  ✅ Script works in qtile-style environment")

    except Exception as e:
        print(f"  ❌ Qtile-style execution failed: {e}")

    print()

    # 5. Recommendations
    print("Debugging Recommendations:")
    print("-" * 27)

    if not expanded_path.exists():
        print("❌ CRITICAL: Script file does not exist")
        print("   → Check if ~/bin/cputemp exists")
        print("   → Verify the path in qtile_config.py")
    elif not os.access(expanded_path, os.X_OK):
        print("❌ CRITICAL: Script is not executable")
        print("   → Run: chmod +x ~/bin/cputemp")
    else:
        print("✅ Script exists and is executable")
        print("📝 To debug further:")
        print("   → Check script logs: add logging to your cputemp script")
        print("   → Test after qtile restart: run this debug script again")
        print("   → Monitor qtile logs: python3 scripts/qtile_log_monitor.py --level debug")
        print("   → Check if script depends on display environment variables")
        print("   → Verify script works with minimal environment")

    print()
    print("💡 Next steps:")
    print("   1. Run this script before and after qtile restart to compare")
    print("   2. Check qtile logs for any script-related errors")
    print("   3. Add debug output to your cputemp script")
    print("   4. Consider using absolute paths in your script")


if __name__ == "__main__":
    test_script_execution()
