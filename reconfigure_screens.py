#!/usr/bin/env python3
"""
External script to trigger Qtile screen reconfiguration
Usage: python3 /home/ekollof/.config/qtile/reconfigure_screens.py
"""

import subprocess
import sys


def reconfigure_screens():
    """Trigger Qtile screen reconfiguration"""
    try:
        # Use qtile's built-in reconfigure_screens command
        cmd = [
            "qtile", "cmd-obj", "-o", "cmd", "-f", "reconfigure_screens"
        ]

        print("Triggering Qtile screen reconfiguration...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("Screen reconfiguration completed successfully")

            # Also trigger a refresh of our screen detection
            try:
                import sys
                sys.path.insert(0, '/home/ekollof/.config/qtile')
                from modules.screens import refresh_screens, get_screen_count

                changed = refresh_screens()
                new_count = get_screen_count()
                print(f"Updated screen count: {new_count}")
                if changed:
                    print("Screen configuration changed - qtile should restart automatically")
                else:
                    print("No screen count change detected")

            except Exception as e:
                print(f"Warning: Could not update local screen detection: {e}")

        else:
            print(f"Error triggering reconfiguration: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("Timeout waiting for Qtile response")
        return False
    except FileNotFoundError:
        print("qtile command not found. Make sure Qtile is installed and in PATH")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

    return True


if __name__ == "__main__":
    if reconfigure_screens():
        sys.exit(0)
    else:
        sys.exit(1)
