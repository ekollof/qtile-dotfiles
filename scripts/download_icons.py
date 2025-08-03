#!/usr/bin/env python3
"""
Icon Downloader for Qtile Status Bar
Downloads appropriate icons to replace emoticons in qtile configuration

This script downloads high-quality SVG icons from various sources and converts them
to bitmap formats suitable for use in qtile status bars.
"""

import os
import sys
import subprocess
import requests
from pathlib import Path
import json

class IconDownloader:
    """Downloads and processes icons for qtile status bar"""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.qtile_dir = self.home_dir / ".config" / "qtile"
        self.icon_dir = self.qtile_dir / "icons"
        
        # Make icon size DPI-aware
        try:
            import sys
            sys.path.insert(0, str(self.qtile_dir))
            from modules.dpi_utils import scale_size
            self.icon_size = scale_size(20)  # DPI-scaled icon size
        except ImportError:
            self.icon_size = 20  # Fallback for systems without DPI utils
            
        # Ensure icon directory exists
        self.icon_dir.mkdir(exist_ok=True)
        
        # Map of current emoticons to appropriate icon replacements
        self.icon_mapping = {
            '🐍': {
                'name': 'python',
                'url': 'https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg',
                'filename': 'python.svg'
            },
            '🔼': {
                'name': 'arrow-up',
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/arrow-up.svg',
                'filename': 'arrow-up.svg'
            },
            '🔄': {
                'name': 'refresh',
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/refresh-cw.svg',
                'filename': 'refresh.svg'
            },
            '📭': {
                'name': 'mail',
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/mail.svg',
                'filename': 'mail.svg'
            },
            '🎫': {
                'name': 'ticket',
                'url': 'https://raw.githubusercontent.com/tabler/tabler-icons/master/icons/ticket.svg',
                'filename': 'ticket.svg'
            },
            '🌡': {
                'name': 'thermometer',
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/thermometer.svg',
                'filename': 'thermometer.svg'
            },
            '🔋': {
                'name': 'battery',
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/battery.svg',
                'filename': 'battery.svg'
            },
            '⚡': {
                'name': 'zap',
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/zap.svg',
                'filename': 'zap.svg'
            },
            '🪫': {
                'name': 'battery-low',
                'url': 'https://raw.githubusercontent.com/tabler/tabler-icons/master/icons/battery-low.svg',
                'filename': 'battery-low.svg'
            }
        }
        
        # Additional useful icons for status bar
        self.additional_icons = {
            'clock': {
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/clock.svg',
                'filename': 'clock.svg'
            },
            'monitor': {
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/monitor.svg',
                'filename': 'monitor.svg'
            },
            'cpu': {
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/cpu.svg',
                'filename': 'cpu.svg'
            },
            'activity': {
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/activity.svg',
                'filename': 'activity.svg'
            },
            'wifi': {
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/wifi.svg',
                'filename': 'wifi.svg'
            },
            'volume': {
                'url': 'https://raw.githubusercontent.com/feathericons/feather/master/icons/volume-2.svg',
                'filename': 'volume.svg'
            }
        }

    def download_file(self, url, filename):
        """Download a file from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            filepath = self.icon_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Downloaded {filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to download {filename}: {e}")
            return False

    def convert_svg_to_png(self, svg_file, png_file):
        """Convert SVG to PNG using ImageMagick with high quality settings"""
        try:
            # Use ImageMagick with improved settings for crisp, transparent icons
            cmd = [
                'magick',  # Use modern ImageMagick command
                str(svg_file),
                '-background', 'transparent',
                '-density', '300',  # High DPI for crisp rendering
                '-resize', f'{self.icon_size}x{self.icon_size}',
                '-strip',  # Remove metadata
                '-alpha', 'remove',  # Clean alpha channel
                '-alpha', 'on',     # Re-enable clean alpha
                '-quality', '100',  # Maximum quality
                str(png_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Converted {svg_file.name} to PNG (high quality)")
                return True
            else:
                # Fallback to older convert command
                cmd_fallback = [
                    'convert',
                    str(svg_file),
                    '-background', 'transparent',
                    '-density', '300',
                    '-resize', f'{self.icon_size}x{self.icon_size}',
                    '-strip',
                    '-alpha', 'remove',
                    '-alpha', 'on',
                    '-quality', '100',
                    str(png_file)
                ]
                
                result_fallback = subprocess.run(cmd_fallback, capture_output=True, text=True)
                if result_fallback.returncode == 0:
                    print(f"✓ Converted {svg_file.name} to PNG (fallback)")
                    return True
                else:
                    print(f"✗ Failed to convert {svg_file.name}: {result.stderr}")
                    return False
                
        except FileNotFoundError:
            print("✗ ImageMagick not found. Please install ImageMagick to convert SVG to PNG")
            return False

    def download_all_icons(self):
        """Download all mapped icons"""
        print("Downloading icon replacements for emoticons...")
        
        # Download emoticon replacements
        for emoticon, icon_info in self.icon_mapping.items():
            print(f"Downloading {icon_info['name']} to replace {emoticon}")
            self.download_file(icon_info['url'], icon_info['filename'])
        
        # Download additional useful icons
        print("\nDownloading additional useful icons...")
        for icon_name, icon_info in self.additional_icons.items():
            print(f"Downloading {icon_name}")
            self.download_file(icon_info['url'], icon_info['filename'])

    def convert_all_to_png(self):
        """Convert all SVG files to PNG"""
        print("\nConverting SVG files to PNG...")
        
        svg_files = list(self.icon_dir.glob("*.svg"))
        if not svg_files:
            print("No SVG files found to convert")
            return
        
        for svg_file in svg_files:
            png_file = svg_file.with_suffix('.png')
            self.convert_svg_to_png(svg_file, png_file)

    def create_icon_reference(self):
        """Create a reference file showing the mapping"""
        reference = {
            'emoticon_replacements': {},
            'additional_icons': list(self.additional_icons.keys()),
            'usage_examples': {
                'qtile_widget': 'widget.TextBox(text="", font="monospace", fontsize=16)',
                'image_widget': 'widget.Image(filename="~/.config/qtile/icons/python.png")'
            }
        }
        
        for emoticon, icon_info in self.icon_mapping.items():
            reference['emoticon_replacements'][emoticon] = {
                'name': icon_info['name'],
                'svg_file': icon_info['filename'],
                'png_file': icon_info['filename'].replace('.svg', '.png')
            }
        
        reference_file = self.icon_dir / 'icon_reference.json'
        with open(reference_file, 'w') as f:
            json.dump(reference, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Created icon reference at {reference_file}")

    def run(self):
        """Run the complete download and conversion process"""
        print(f"Icon directory: {self.icon_dir}")
        self.download_all_icons()
        self.convert_all_to_png()
        self.create_icon_reference()
        print(f"\n✓ Icon setup complete! Check {self.icon_dir} for your new icons.")


def main():
    """Main function"""
    # Determine icon directory
    if len(sys.argv) > 1:
        icon_dir = sys.argv[1]
    else:
        # Default to qtile config directory
        home = os.path.expanduser("~")
        icon_dir = os.path.join(home, ".config", "qtile", "icons")
    
    downloader = IconDownloader(icon_dir)
    downloader.run()


if __name__ == "__main__":
    main()
