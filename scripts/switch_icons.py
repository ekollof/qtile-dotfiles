#!/usr/bin/env python3
"""
Icon Configuration Switcher for Qtile
Easily switch between emoticons and bitmap icons in your qtile configuration

Usage:
    python3 switch_icons.py [method]
    
Methods:
    emoticons  - Use original emoticons (🐍, 🔼, etc.)
    svg        - Use vector SVG images (best quality)
    image      - Use bitmap PNG images
    nerd_font  - Use Nerd Font icons
    text       - Use simple text symbols
    
Example:
    python3 switch_icons.py svg
"""

import os
import sys
import shutil
from pathlib import Path

class IconSwitcher:
    """Switches between different icon methods in qtile configuration"""
    
    def __init__(self, qtile_dir):
        self.qtile_dir = Path(qtile_dir)
        self.bars_original = self.qtile_dir / "modules" / "bars.py"
        self.bars_with_icons = self.qtile_dir / "modules" / "bars_with_icons.py"
        self.bars_backup = self.qtile_dir / "modules" / "bars_original.py"
        
    def backup_original(self):
        """Create a backup of the original bars.py if it doesn't exist"""
        if not self.bars_backup.exists() and self.bars_original.exists():
            shutil.copy2(self.bars_original, self.bars_backup)
            print(f"✓ Created backup: {self.bars_backup}")
    
    def switch_to_emoticons(self):
        """Switch back to original emoticons"""
        if self.bars_backup.exists():
            shutil.copy2(self.bars_backup, self.bars_original)
            print("✓ Switched to emoticons")
            print("  Restart qtile to see changes: Super+Ctrl+R")
        else:
            print("✗ No backup found. Cannot restore emoticons.")
    
    def switch_to_icons(self, method="image"):
        """Switch to bitmap icons with specified method"""
        if not self.bars_with_icons.exists():
            print(f"✗ Icon bars file not found: {self.bars_with_icons}")
            return False
            
        # Create backup of original
        self.backup_original()
        
        # Read the bars_with_icons.py file
        content = self.bars_with_icons.read_text()
        
        # Update the icon method in the content
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'self.icon_method = ' in line and line.strip().startswith('self.icon_method'):
                lines[i] = f'        self.icon_method = "{method}"  # Options: "svg", "image", "nerd_font", "text"'
                break
        
        # Write the modified content to bars.py
        modified_content = '\n'.join(lines)
        self.bars_original.write_text(modified_content)
        
        print(f"✓ Switched to {method} icons")
        print("  Restart qtile to see changes: Super+Ctrl+R")
        return True
    
    def show_status(self):
        """Show current icon configuration status"""
        print("Qtile Icon Configuration Status")
        print("=" * 40)
        
        if self.bars_backup.exists():
            print("✓ Original bars.py backed up")
        else:
            print("- No backup found")
            
        if self.bars_with_icons.exists():
            print("✓ Icon-enabled bars.py available")
        else:
            print("✗ Icon-enabled bars.py not found")
            
        # Try to detect current method
        if self.bars_original.exists():
            content = self.bars_original.read_text()
            if 'self.icon_method' in content:
                for line in content.split('\n'):
                    if 'self.icon_method = ' in line and line.strip().startswith('self.icon_method'):
                        method = line.split('"')[1] if '"' in line else "unknown"
                        print(f"Current method: {method}")
                        break
            else:
                print("Current method: emoticons (original)")
        
        # Check icon availability
        icon_dir = self.qtile_dir / "icons"
        if icon_dir.exists():
            svg_count = len(list(icon_dir.glob("*.svg")))
            png_count = len(list(icon_dir.glob("*.png")))
            print(f"✓ {svg_count} SVG icons available")
            print(f"✓ {png_count} PNG icons available")
        else:
            print("✗ Icon directory not found")

def main():
    """Main function"""
    # Get qtile directory
    home = os.path.expanduser("~")
    qtile_dir = os.path.join(home, ".config", "qtile")
    
    switcher = IconSwitcher(qtile_dir)
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCurrent Status:")
        switcher.show_status()
        return
    
    method = sys.argv[1].lower()
    
    if method == "emoticons":
        switcher.switch_to_emoticons()
    elif method in ["svg", "image", "nerd_font", "text"]:
        switcher.switch_to_icons(method)
    elif method == "status":
        switcher.show_status()
    else:
        print(f"Unknown method: {method}")
        print("Valid methods: emoticons, svg, image, nerd_font, text, status")

if __name__ == "__main__":
    main()
