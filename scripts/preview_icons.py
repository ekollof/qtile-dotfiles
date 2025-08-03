#!/usr/bin/env python3
"""
Icon Preview Script
Shows how different icon methods will look in your qtile status bar
"""

import os
from pathlib import Path

def show_icon_preview():
    """Display a preview of different icon methods"""
    
    qtile_dir = Path.home() / ".config" / "qtile"
    icon_dir = qtile_dir / "icons"
    
    print("🎨 Qtile Icon Preview")
    print("=" * 50)
    print()
    
    # Icon mappings
    icons = {
        "Python launcher": {
            "original": "🐍",
            "nerd_font": "\ue73c",
            "text": "Py",
            "image": "python.png",
            "svg": "python.svg"
        },
        "Package updates": {
            "original": "🔼",
            "nerd_font": "\uf0aa", 
            "text": "↑",
            "image": "arrow-up.png",
            "svg": "arrow-up.svg"
        },
        "AUR updates": {
            "original": "🔄",
            "nerd_font": "\uf2f1",
            "text": "⟲", 
            "image": "refresh.png",
            "svg": "refresh.svg"
        },
        "Email": {
            "original": "📭",
            "nerd_font": "\uf0e0",
            "text": "✉",
            "image": "mail.png",
            "svg": "mail.svg"
        },
        "Tickets": {
            "original": "🎫",
            "nerd_font": "\uf3ff",
            "text": "🎟",
            "image": "ticket.png",
            "svg": "ticket.svg"
        },
        "Temperature": {
            "original": "🌡",
            "nerd_font": "\uf2c9",
            "text": "T°",
            "image": "thermometer.png",
            "svg": "thermometer.svg"
        },
        "Battery": {
            "original": "🔋",
            "nerd_font": "\uf240",
            "text": "⚡",
            "image": "battery.png",
            "svg": "battery.svg"
        }
    }
    
    # Display table
    print(f"{'Widget':<15} {'Original':<8} {'Nerd Font':<10} {'Text':<6} {'PNG File':<15} {'SVG File':<15}")
    print("-" * 80)
    
    for name, icon_set in icons.items():
        png_status = "✓" if (icon_dir / icon_set['image']).exists() else "✗"
        svg_status = "✓" if (icon_dir / icon_set['svg']).exists() else "✗"
        print(f"{name:<15} {icon_set['original']:<8} {icon_set['nerd_font']:<10} {icon_set['text']:<6} {icon_set['image']:<15} {icon_set['svg']:<15} {png_status}/{svg_status}")
    
    print()
    print("Icon Method Details:")
    print("─" * 30)
    print("• Original:   Uses Unicode emoticons (current setup)")
    print("• Nerd Font:  Uses Nerd Font icon characters")
    print("• Text:       Uses simple text symbols") 
    print("• SVG:        Uses vector SVG files (best quality)")
    print("• PNG:        Uses bitmap PNG files")
    print()
    
    # Show current status
    current_method = "unknown"
    bars_file = qtile_dir / "modules" / "bars.py"
    if bars_file.exists():
        content = bars_file.read_text()
        if 'self.icon_method' in content:
            for line in content.split('\n'):
                if 'self.icon_method = ' in line and line.strip().startswith('self.icon_method'):
                    if '"' in line:
                        current_method = line.split('"')[1]
                    break
        else:
            current_method = "emoticons"
    
    print(f"Current method: {current_method}")
    svg_count = len(list(icon_dir.glob('*.svg')))
    png_count = len(list(icon_dir.glob('*.png')))
    print(f"Available SVG icons: {svg_count}")
    print(f"Available PNG icons: {png_count}")
    print()
    print("To switch methods:")
    print("  python3 scripts/switch_icons.py svg        # Use SVG vectors (recommended)")
    print("  python3 scripts/switch_icons.py image      # Use PNG images")
    print("  python3 scripts/switch_icons.py nerd_font  # Use Nerd Font icons")
    print("  python3 scripts/switch_icons.py text       # Use text symbols")
    print("  python3 scripts/switch_icons.py emoticons  # Back to emoticons")

if __name__ == "__main__":
    show_icon_preview()
