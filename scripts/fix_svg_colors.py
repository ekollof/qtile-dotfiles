#!/usr/bin/env python3
"""
SVG Color Replacer for Qtile
Directly replaces currentColor with actual hex colors from your qtile theme

This script reads your qtile color configuration and replaces all instances
of 'currentColor' in SVG files with the actual foreground color.
"""


import sys
from pathlib import Path

class SVGColorReplacer:
    """Replaces currentColor with actual theme colors in SVG files"""

    def __init__(self, icon_dir, qtile_dir):
        self.icon_dir = Path(icon_dir)
        self.qtile_dir = Path(qtile_dir)
        self.foreground_color = None

    def get_qtile_foreground_color(self):
        """Extract the foreground color from qtile configuration"""
        try:
            # Try to import and get colors from the color manager
            sys.path.insert(0, str(self.qtile_dir))

            # Import the color manager
            from modules.colors import color_manager
            colors = color_manager.get_colors()

            # Get the foreground color
            self.foreground_color = colors["special"]["foreground"]
            print(f"✓ Found qtile foreground color: {self.foreground_color}")
            return True

        except Exception as e:
            print(f"✗ Could not get qtile colors: {e}")

            # Fallback: try to read from cache files
            cache_files = [
                self.qtile_dir.parent / ".cache" / "wal" / "colors.json",
                Path.home() / ".cache" / "wal" / "colors.json"
            ]

            for cache_file in cache_files:
                if cache_file.exists():
                    try:
                        import json
                        with open(cache_file) as f:
                            data = json.load(f)
                            if "special" in data and "foreground" in data["special"]:
                                self.foreground_color = data["special"]["foreground"]
                                print(f"✓ Found color from cache: {self.foreground_color}")
                                return True
                    except Exception as e:
                        print(f"Could not read {cache_file}: {e}")

            # Last resort: use a light color that works on dark backgrounds
            self.foreground_color = "#E0E0E0"
            print(f"⚠ Using fallback color: {self.foreground_color}")
            return True

    def replace_current_color_in_svg(self, svg_file):
        """Replace currentColor with actual hex color in an SVG file"""
        try:
            content = svg_file.read_text()

            # Count occurrences before replacement
            current_color_count = content.count('currentColor')
            if current_color_count == 0:
                print(f"- {svg_file.name}: no currentColor found")
                return False

            # Create backup if it doesn't exist
            backup_file = svg_file.with_suffix('.svg.colorbackup')
            if not backup_file.exists():
                backup_file.write_text(content)

            # Replace currentColor with actual color
            new_content = content.replace('currentColor', self.foreground_color)

            # Also replace any stroke="none" with the color for visibility
            if 'stroke="none"' in new_content and 'fill="none"' in new_content:
                new_content = new_content.replace('fill="none"', f'fill="{self.foreground_color}"')
                print(f"✓ {svg_file.name}: replaced currentColor ({current_color_count}x) and added fill")
            else:
                print(f"✓ {svg_file.name}: replaced currentColor ({current_color_count}x)")

            # Write the updated content
            svg_file.write_text(new_content)
            return True

        except Exception as e:
            print(f"✗ Error processing {svg_file.name}: {e}")
            return False

    def create_colored_test_icon(self):
        """Create a test icon with the current color"""
        test_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{self.foreground_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <path d="m 14.31 8 L 20 12 L 14.31 16 L 16 12"/>
  <path d="m 9.69 16 L 4 12 L 9.69 8 L 8 12"/>
  <text x="12" y="16" text-anchor="middle" fill="{self.foreground_color}" font-size="8" font-family="monospace">TEST</text>
</svg>'''

        test_file = self.icon_dir / "color-test.svg"
        test_file.write_text(test_content)
        print(f"✓ Created color test icon: {test_file.name}")

    def process_all_svgs(self):
        """Process all SVG files in the directory"""
        print("🎨 Replacing currentColor with theme colors...")
        print("=" * 50)

        # Get the foreground color
        if not self.get_qtile_foreground_color():
            print("Could not determine foreground color")
            return

        # Find all SVG files
        svg_files = list(self.icon_dir.glob("*.svg"))
        if not svg_files:
            print("No SVG files found")
            return

        # Process each file
        processed_count = 0
        for svg_file in svg_files:
            if svg_file.name.endswith(('-simple.svg', '-test.svg')):
                continue  # Skip generated files

            if self.replace_current_color_in_svg(svg_file):
                processed_count += 1

        print(f"\n✓ Processed {processed_count}/{len(svg_files)} SVG files")
        print(f"✓ All icons now use color: {self.foreground_color}")

        # Create test icon
        self.create_colored_test_icon()

        print("\n💡 Next steps:")
        print("  • Restart qtile: Super+Ctrl+R")
        print(f"  • Icons should now be visible in {self.foreground_color}")
        print("  • If too bright/dark, edit the color in each SVG file")
        print("  • Backups saved with .colorbackup extension")

    def restore_from_backup(self):
        """Restore SVG files from backup"""
        print("🔄 Restoring SVG files from backup...")

        backup_files = list(self.icon_dir.glob("*.colorbackup"))
        if not backup_files:
            print("No backup files found")
            return

        restored_count = 0
        for backup_file in backup_files:
            original_file = backup_file.with_suffix('')  # Remove .colorbackup
            if original_file.exists():
                content = backup_file.read_text()
                original_file.write_text(content)
                print(f"✓ Restored {original_file.name}")
                restored_count += 1

        print(f"\n✓ Restored {restored_count} files from backup")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        # Restore mode
        home = Path.home()
        icon_dir = home / ".config" / "qtile" / "icons"
        qtile_dir = home / ".config" / "qtile"

        replacer = SVGColorReplacer(str(icon_dir), str(qtile_dir))
        replacer.restore_from_backup()
        return

    # Normal mode
    home = Path.home()
    icon_dir = home / ".config" / "qtile" / "icons"
    qtile_dir = home / ".config" / "qtile"

    replacer = SVGColorReplacer(str(icon_dir), str(qtile_dir))
    replacer.process_all_svgs()

if __name__ == "__main__":
    main()
