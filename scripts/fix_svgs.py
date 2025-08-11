#!/usr/bin/env python3
"""
SVG Fixer for Qtile
Fixes SVG namespace issues and ensures proper qtile compatibility

This script fixes common SVG issues that prevent qtile from loading icons:
1. Removes namespace prefixes that confuse qtile's SVG parser
2. Ensures proper SVG structure
3. Maintains color theming capabilities
"""


import re
from pathlib import Path

class SVGFixer:
    """Fixes SVG files for qtile compatibility"""

    def __init__(self, icon_dir):
        self.icon_dir = Path(icon_dir)

    def fix_svg_namespaces(self, svg_file):
        """Remove namespace prefixes from SVG elements"""
        try:
            content = svg_file.read_text()

            # Store original for backup
            backup_file = svg_file.with_suffix('.svg.bak')
            if not backup_file.exists():
                backup_file.write_text(content)

            # Fix namespace issues
            fixes_applied = []

            # Remove ns0: prefixes
            if 'ns0:' in content:
                content = re.sub(r'ns0:', '', content)
                fixes_applied.append("removed ns0 namespaces")

            # Fix xmlns declarations
            if 'xmlns:ns0=' in content:
                content = re.sub(r'xmlns:ns0="[^"]*"', 'xmlns="http://www.w3.org/2000/svg"', content)
                fixes_applied.append("fixed xmlns declaration")

            # Ensure proper SVG opening tag
            if '<svg' not in content and content.strip().startswith('<?xml'):
                # Find the svg tag and fix it
                content = re.sub(r'<svg([^>]*)>', r'<svg\1>', content)
                fixes_applied.append("normalized svg tag")

            # Write fixed content
            svg_file.write_text(content)

            if fixes_applied:
                print(f"✓ Fixed {svg_file.name}: {', '.join(fixes_applied)}")
                return True
            else:
                print(f"- {svg_file.name}: no fixes needed")
                return False

        except Exception as e:
            print(f"✗ Error fixing {svg_file.name}: {e}")
            return False

    def create_simple_icons(self):
        """Create simple fallback icons that definitely work"""
        simple_icons = {
            'python-simple.svg': '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <text x="12" y="16" text-anchor="middle" fill="currentColor" font-size="10" font-family="monospace">Py</text>
</svg>''',
            'arrow-up-simple.svg': '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="12" y1="19" x2="12" y2="5"/>
  <polyline points="5,12 12,5 19,12"/>
</svg>''',
            'refresh-simple.svg': '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23,4 23,10 17,10"/>
  <path d="m 20.49 15 A 9 9 0 1 1 23 10"/>
</svg>''',
        }

        for filename, content in simple_icons.items():
            file_path = self.icon_dir / filename
            file_path.write_text(content)
            print(f"✓ Created simple fallback: {filename}")

    def test_svg_validity(self, svg_file):
        """Test if an SVG file is valid"""
        try:
            content = svg_file.read_text()

            # Basic validity checks
            if not content.strip():
                return False, "empty file"

            if not content.startswith('<?xml'):
                return False, "missing xml declaration"

            if '<svg' not in content:
                return False, "missing svg tag"

            if content.count('<svg') != content.count('</svg>'):
                return False, "unmatched svg tags"

            # Check for problematic elements
            if 'linearGradient' in content or 'radialGradient' in content:
                return True, "has gradients (may cause issues)"

            return True, "valid"

        except Exception as e:
            return False, f"error reading: {e}"

    def fix_all_svgs(self):
        """Fix all SVG files in the directory"""
        print("🔧 Fixing SVG files for qtile compatibility...")
        print("=" * 50)

        svg_files = list(self.icon_dir.glob("*.svg"))
        if not svg_files:
            print("No SVG files found")
            return

        fixed_count = 0
        problem_files = []

        for svg_file in svg_files:
            # Test validity first
            valid, reason = self.test_svg_validity(svg_file)

            if not valid:
                print(f"⚠ {svg_file.name}: {reason}")
                problem_files.append(svg_file.name)

            # Try to fix namespace issues
            if self.fix_svg_namespaces(svg_file):
                fixed_count += 1

        print(f"\n✓ Fixed {fixed_count}/{len(svg_files)} SVG files")

        if problem_files:
            print(f"\n⚠ Files that may still have issues: {', '.join(problem_files)}")
            print("Consider using PNG fallbacks for these files")

        # Create simple fallback icons
        print("\n🎯 Creating simple fallback icons...")
        self.create_simple_icons()

        print("\n💡 Recommendations:")
        print("  • Test qtile restart: Super+Ctrl+R")
        print("  • If issues persist, use PNG icons: python3 scripts/switch_icons.py image")
        print("  • Backups are saved with .bak extension")

def main():
    """Main function"""
    import sys

    # Get icon directory
    if len(sys.argv) > 1:
        icon_dir = sys.argv[1]
    else:
        home = Path.home()
        icon_dir = home / ".config" / "qtile" / "icons"

    fixer = SVGFixer(icon_dir)
    fixer.fix_all_svgs()

if __name__ == "__main__":
    main()
