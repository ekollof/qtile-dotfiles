#!/usr/bin/env python3
"""
@brief Test different font sizes in qtile configuration
@author qtile-config
@version 1.0.0

Simple script to test what different font sizes look like
before permanently changing qtile_config.py.
"""

import sys
import os

# Add parent directory to path to import qtile modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from qtile_config import get_config
    from modules.dpi_utils import get_dpi_manager, scale_font
except ImportError as e:
    print(f"❌ Error importing qtile modules: {e}")
    print("Make sure you're running this from the qtile config directory.")
    sys.exit(1)


def test_font_sizes():
    """Test different font size and bar height combinations"""
    print("🔤 Font Size & Bar Height Tester for Qtile Configuration")
    print("=" * 60)
    
    # Get current DPI info
    dpi_manager = get_dpi_manager()
    print(f"📊 Current DPI: {dpi_manager.dpi}")
    print(f"📊 DPI Scale Factor: {dpi_manager.scale_factor:.2f}")
    print()
    
    # Test different font sizes
    test_sizes = [
        (10, 14, "Small"),
        (12, 16, "Default"),  
        (14, 18, "Medium"),
        (16, 20, "Large"),
        (18, 22, "Extra Large"),
    ]
    
    print("🧪 Testing Font Size Combinations:")
    print("-" * 60)
    print("| Style       | Text Size | Icon Size | Scaled Text | Scaled Icon |")
    print("|-------------|-----------|-----------|-------------|-------------|")
    
    for text_size, icon_size, label in test_sizes:
        scaled_text = scale_font(text_size)
        scaled_icon = scale_font(icon_size)
        
        print(f"| {label:<11} | {text_size:>9} | {icon_size:>9} | {scaled_text:>11} | {scaled_icon:>11} |")
    
    print()
    
    # Test different bar heights
    bar_heights = [20, 24, 28, 32, 36, 40]
    
    print("📏 Testing Bar Height Options:")
    print("-" * 40)
    print("| Height | Scaled | Description     |")
    print("|--------|--------|-----------------|")
    
    for height in bar_heights:
        scaled_height = scale_font(height)  # Use scale_font for consistency
        if height <= 24:
            desc = "Compact"
        elif height <= 28:
            desc = "Default"
        elif height <= 32:
            desc = "Comfortable"
        else:
            desc = "Spacious"
        
        print(f"| {height:>6} | {scaled_height:>6} | {desc:<15} |")
    
    print()
    print("🎯 To Apply Changes:")
    print("1. Edit qtile_config.py")
    print("2. Change the return values in:")
    print("   - preferred_fontsize() → for text size")
    print("   - preferred_icon_fontsize() → for icon size")
    print("   - preferred_bar_height() → for bar height")
    print("3. Restart qtile with Super+Ctrl+R")
    print()
    
    # Show current settings
    config = get_config()
    current_text = config.preferred_fontsize
    current_icon = config.preferred_icon_fontsize
    current_bar_height = config.preferred_bar_height
    
    print("📄 Current Settings:")
    print(f"   Text size: {current_text} → scaled: {scale_font(current_text)}")
    print(f"   Icon size: {current_icon} → scaled: {scale_font(current_icon)}")
    print(f"   Bar height: {current_bar_height} → scaled: {config.bar_settings['height']}")
    print()
    
    # Interactive size recommendations
    print("💡 Recommendations:")
    if dpi_manager.dpi <= 96:
        print("   📺 Standard DPI: Font sizes 10-14, Bar height 24-28")
    elif dpi_manager.dpi <= 144:  
        print("   🖥️  Medium DPI: Font sizes 12-16, Bar height 28-32")
    else:
        print("   📱 High DPI: Font sizes 14-18+, Bar height 32-36+")
    
    print()
    print("✅ Choose the combination that looks best for your display!")


def main():
    """Main function"""
    try:
        test_font_sizes()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
