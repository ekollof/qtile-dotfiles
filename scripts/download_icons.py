#!/usr/bin/env python3
from pathlib import Path
"""
Icon Downloader for Qtile Status Bar
Downloads appropriate icons to replace emoticons in qtile configuration

This script downloads high-quality SVG icons from various sources and converts them
to bitmap formats suitable for use in qtile status bars.
"""

import subprocess
import json
import requests

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
        """
        @brief Download a file from URL with error handling
        @param url The URL to download from
        @param filename The local filename to save to
        @return True if download successful, False otherwise
        @throws requests.exceptions.RequestException if download fails
        """
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
        """
        @brief Convert SVG to PNG using ImageMagick with high quality settings
        @param svg_file Path to source SVG file
        @param png_file Path to target PNG file
        @return True if conversion successful, False otherwise
        @throws FileNotFoundError if ImageMagick is not installed
        """
        try:
            # Try modern ImageMagick command first
            if self._try_magick_convert(svg_file, png_file):
                return True
            # Fallback to older convert command
            return self._try_legacy_convert(svg_file, png_file)
        except FileNotFoundError:
            print("✗ ImageMagick not found. Please install ImageMagick to convert SVG to PNG")
            return False

    def _try_magick_convert(self, svg_file, png_file) -> bool:
        """
        @brief Try conversion with modern 'magick' command
        @param svg_file Path to source SVG file
        @param png_file Path to target PNG file
        @return True if successful, False otherwise
        """
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
        return False

    def _try_legacy_convert(self, svg_file, png_file) -> bool:
        """
        @brief Try conversion with legacy 'convert' command as fallback
        @param svg_file Path to source SVG file
        @param png_file Path to target PNG file
        @return True if successful, False otherwise
        """
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
            print(f"✗ Failed to convert {svg_file.name}: {result_fallback.stderr}")
            return False

    def download_all_icons(self):
        """
        @brief Download all mapped icons from remote sources
        """
        self._download_emoticon_replacements()
        self._download_additional_icons()

    def _download_emoticon_replacements(self):
        """
        @brief Download icon replacements for emoticons
        """
        print("Downloading icon replacements for emoticons...")
        for emoticon, icon_info in self.icon_mapping.items():
            print(f"Downloading {icon_info['name']} to replace {emoticon}")
            self.download_file(icon_info['url'], icon_info['filename'])

    def _download_additional_icons(self):
        """
        @brief Download additional useful icons for status bar
        """
        print("\nDownloading additional useful icons...")
        for icon_name, icon_info in self.additional_icons.items():
            print(f"Downloading {icon_name}")
            self.download_file(icon_info['url'], icon_info['filename'])

    def convert_all_to_png(self):
        """
        @brief Convert all SVG files to PNG format
        """
        print("\nConverting SVG files to PNG...")

        svg_files = list(self.icon_dir.glob("*.svg"))
        if not svg_files:
            print("No SVG files found to convert")
            return

        for svg_file in svg_files:
            png_file = svg_file.with_suffix('.png')
            self.convert_svg_to_png(svg_file, png_file)

    def create_icon_reference(self):
        """
        @brief Create a reference file showing the mapping between emoticons and icons
        """
        reference = self._build_reference_dict()
        reference_file = self.icon_dir / 'icon_reference.json'
        
        with open(reference_file, 'w') as f:
            json.dump(reference, f, indent=2, ensure_ascii=False)

        print(f"✓ Created icon reference at {reference_file}")

    def _build_reference_dict(self) -> dict:
        """
        @brief Build the reference dictionary structure
        @return Dictionary containing emoticon mappings and usage examples
        """
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

        return reference

    def run(self):
        """
        @brief Run the complete download and conversion process
        """
        print(f"Icon directory: {self.icon_dir}")
        self._setup_process()
        self._report_completion()

    def _setup_process(self):
        """
        @brief Execute the main setup steps
        """
        self.download_all_icons()
        self.convert_all_to_png()
        self.create_icon_reference()

    def _report_completion(self):
        """
        @brief Report successful completion of the icon setup
        """
        print(f"\n✓ Icon setup complete! Check {self.icon_dir} for your new icons.")


def main():
    """
    @brief Main function to execute icon downloader
    """
    # IconDownloader uses its own path detection
    downloader = IconDownloader()
    downloader.run()


if __name__ == "__main__":
    main()
