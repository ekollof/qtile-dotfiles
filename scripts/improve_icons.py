#!/usr/bin/env python3
"""
Icon Quality Improver
Regenerates all SVG icons with better quality, transparency, and sharpness

This script will:
1. Re-process all existing SVG files with improved settings
2. Create crisp, transparent PNG icons
3. Optimize for qtile status bar display
"""

import os
import subprocess
from pathlib import Path

class IconQualityImprover:
    """Improves icon quality and transparency"""
    
    def __init__(self, icon_dir):
        self.icon_dir = Path(icon_dir)
        self.icon_size = 20  # Slightly larger for better quality
        
    def improve_icon_quality(self, svg_file, png_file):
        """Convert SVG to high-quality transparent PNG"""
        try:
            # First try with modern magick command
            cmd = [
                'magick',
                str(svg_file),
                '-background', 'transparent',
                '-density', '300',  # High DPI for crisp rendering
                '-colorspace', 'sRGB',  # Ensure proper color space
                '-resize', f'{self.icon_size}x{self.icon_size}',
                '-unsharp', '0x0.5+0.5+0.05',  # Slight sharpening
                '-strip',  # Remove metadata
                '-alpha', 'remove',  # Clean alpha channel
                '-alpha', 'on',     # Re-enable clean alpha
                '-quality', '100',  # Maximum quality
                '-define', 'png:compression-filter=5',  # Best PNG compression
                '-define', 'png:compression-level=9',
                '-define', 'png:compression-strategy=1',
                str(png_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Improved {svg_file.name} → {png_file.name}")
                return True
            
            # Fallback to older convert command
            cmd_fallback = [
                'convert',
                str(svg_file),
                '-background', 'transparent',
                '-density', '300',
                '-colorspace', 'sRGB',
                '-resize', f'{self.icon_size}x{self.icon_size}',
                '-unsharp', '0x0.5+0.5+0.05',
                '-strip',
                '-alpha', 'remove',
                '-alpha', 'on',
                '-quality', '100',
                str(png_file)
            ]
            
            result_fallback = subprocess.run(cmd_fallback, capture_output=True, text=True)
            if result_fallback.returncode == 0:
                print(f"✓ Improved {svg_file.name} → {png_file.name} (fallback)")
                return True
            else:
                print(f"✗ Failed to improve {svg_file.name}: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("✗ ImageMagick not found. Please install ImageMagick")
            return False
    
    def optimize_existing_png(self, png_file):
        """Optimize existing PNG for better transparency and quality"""
        try:
            # Create optimized version
            temp_file = png_file.with_suffix('.temp.png')
            
            cmd = [
                'magick',
                str(png_file),
                '-alpha', 'remove',  # Remove alpha channel
                '-alpha', 'on',      # Add clean alpha channel
                '-background', 'transparent',
                '-strip',            # Remove metadata
                str(temp_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Replace original with optimized version
                temp_file.replace(png_file)
                print(f"✓ Optimized {png_file.name}")
                return True
            else:
                print(f"✗ Failed to optimize {png_file.name}: {result.stderr}")
                if temp_file.exists():
                    temp_file.unlink()
                return False
                
        except FileNotFoundError:
            print("✗ ImageMagick not found")
            return False
    
    def process_all_icons(self):
        """Process all SVG files to create high-quality PNGs"""
        print("🎨 Improving icon quality and transparency...")
        print("=" * 50)
        
        svg_files = list(self.icon_dir.glob("*.svg"))
        if not svg_files:
            print("No SVG files found to process")
            return
        
        success_count = 0
        for svg_file in svg_files:
            png_file = svg_file.with_suffix('.png')
            if self.improve_icon_quality(svg_file, png_file):
                success_count += 1
        
        print(f"\n✓ Successfully processed {success_count}/{len(svg_files)} icons")
        
        # Also optimize any existing PNGs that weren't regenerated
        existing_pngs = [p for p in self.icon_dir.glob("*.png") 
                        if not (self.icon_dir / (p.stem + '.svg')).exists()]
        
        if existing_pngs:
            print(f"\n🔧 Optimizing {len(existing_pngs)} existing PNG files...")
            for png_file in existing_pngs:
                self.optimize_existing_png(png_file)
    
    def create_test_samples(self):
        """Create test samples showing different quality levels"""
        test_dir = self.icon_dir / "quality_test"
        test_dir.mkdir(exist_ok=True)
        
        # Find a good test icon
        test_svg = self.icon_dir / "python.svg"
        if not test_svg.exists():
            test_svg = next(self.icon_dir.glob("*.svg"), None)
        
        if not test_svg:
            print("No SVG files found for quality test")
            return
        
        print(f"\n🧪 Creating quality test samples using {test_svg.name}...")
        
        # Different quality settings
        quality_settings = [
            ("low_quality", ['-density', '72', '-resize', '16x16']),
            ("medium_quality", ['-density', '150', '-resize', '18x18', '-unsharp', '0x0.5']),
            ("high_quality", ['-density', '300', '-resize', '20x20', '-unsharp', '0x0.5+0.5+0.05']),
        ]
        
        for name, settings in quality_settings:
            output_file = test_dir / f"{test_svg.stem}_{name}.png"
            cmd = [
                'magick', str(test_svg),
                '-background', 'transparent',
                '-colorspace', 'sRGB',
                *settings,
                '-strip', '-alpha', 'remove', '-alpha', 'on',
                '-quality', '100',
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✓ Created {name} sample")
        
        print(f"Quality test samples saved in: {test_dir}")

def main():
    """Main function"""
    import sys
    
    # Get icon directory
    if len(sys.argv) > 1:
        icon_dir = sys.argv[1]
    else:
        home = os.path.expanduser("~")
        icon_dir = os.path.join(home, ".config", "qtile", "icons")
    
    improver = IconQualityImprover(icon_dir)
    
    # Check if we should create test samples
    if len(sys.argv) > 2 and sys.argv[2] == "test":
        improver.create_test_samples()
    else:
        improver.process_all_icons()
    
    print("\n💡 Tips for best results:")
    print("  • Restart qtile after icon changes: Super+Ctrl+R")
    print("  • Icons are sized at 20px for crisp display")
    print("  • All icons have transparent backgrounds")
    print("  • Use 'python3 improve_icons.py test' to create quality samples")

if __name__ == "__main__":
    main()
