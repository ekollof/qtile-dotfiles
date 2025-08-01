#!/usr/bin/env python3
"""
Key binding consistency analyzer and migration tool
Compares current bindings with layout-aware alternatives
"""

import sys
sys.path.insert(0, '/home/ekollof/.config/qtile')

from modules.keys import create_key_manager
from modules.keys_layout_aware import create_layout_aware_key_manager
from modules.colors import color_manager


def analyze_key_binding_issues():
    """Analyze current key bindings for layout consistency issues"""
    
    print("=== Key Binding Layout Consistency Analysis ===\n")
    
    # Get current bindings
    current_km = create_key_manager(color_manager)
    current_keys = current_km.get_keys()
    
    # Get layout-aware bindings
    aware_km = create_layout_aware_key_manager(color_manager)
    aware_keys = aware_km.get_keys()
    
    print(f"Current bindings: {len(current_keys)} keys")
    print(f"Layout-aware bindings: {len(aware_keys)} keys")
    print()
    
    # Analyze problematic bindings in current setup
    problematic_bindings = []
    
    for key in current_keys:
        modifiers_str = "+".join(str(mod) for mod in key.modifiers) if key.modifiers else ""
        key_combo = f"{modifiers_str}+{key.key}" if modifiers_str else str(key.key)
        
        # Check for layout commands that might not work everywhere
        if hasattr(key, 'commands'):
            for cmd in key.commands:
                cmd_str = str(cmd)
                
                # Commands that don't work with Max layout
                if any(problem in cmd_str.lower() for problem in ['grow', 'shrink', 'increase_ratio', 'decrease_ratio']):
                    problematic_bindings.append({
                        'key': key_combo,
                        'command': cmd_str,
                        'issue': 'May not work with Max/Floating layouts',
                        'description': getattr(key, 'desc', 'No description')
                    })
                
                # Commands that might cause errors
                if 'toggle_split' in cmd_str.lower():
                    problematic_bindings.append({
                        'key': key_combo,
                        'command': cmd_str,
                        'issue': 'Only works with Tile layout',
                        'description': getattr(key, 'desc', 'No description')
                    })
    
    if problematic_bindings:
        print("🚨 PROBLEMATIC BINDINGS FOUND:")
        for binding in problematic_bindings:
            print(f"  {binding['key']:<20} {binding['description']}")
            print(f"    Issue: {binding['issue']}")
            print(f"    Command: {binding['command'][:60]}...")
            print()
    else:
        print("✅ No obvious layout consistency issues found")
    
    # Show improvements in layout-aware version
    print("=== IMPROVEMENTS IN LAYOUT-AWARE VERSION ===\n")
    
    improvements = [
        {
            'category': 'Smart Resizing',
            'description': 'Resize commands adapt to current layout',
            'examples': [
                'Ctrl+L/H: MonadTall=grow/shrink, Tile=ratio, BSP=directional, Max=no-op',
                'No more errors when resizing in Max layout'
            ]
        },
        {
            'category': 'Consistent Navigation', 
            'description': 'All navigation works across layouts',
            'examples': [
                'J/K/H/L: Universal focus movement',
                'Shift+J/K/H/L: Universal window movement'
            ]
        },
        {
            'category': 'Layout-Specific Features',
            'description': 'Advanced features only when supported',
            'examples': [
                'Shift+Space: Rotate (Tile/BSP only)',
                'Shift+Return: Toggle split (Tile only)',
                'X: Maximize (when supported)'
            ]
        },
        {
            'category': 'More Layout Options',
            'description': 'Quick access to all layouts',
            'examples': [
                'T: Tile, M: Max, B: BSP',
                'Shift+T: MonadTall, Shift+X: Matrix'
            ]
        }
    ]
    
    for improvement in improvements:
        print(f"📈 {improvement['category']}:")
        print(f"   {improvement['description']}")
        for example in improvement['examples']:
            print(f"   • {example}")
        print()
    
    # Show migration path
    print("=== MIGRATION RECOMMENDATIONS ===\n")
    
    print("1. BACKUP your current configuration:")
    print("   cp modules/keys.py modules/keys.py.backup")
    print()
    
    print("2. UPDATE config.py to use layout-aware keys:")
    print("   # Replace this line:")
    print("   from modules.keys import create_key_manager")
    print("   # With:")
    print("   from modules.keys_layout_aware import create_layout_aware_key_manager as create_key_manager")
    print()
    
    print("3. TEST the new bindings:")
    print("   • Restart qtile")
    print("   • Try resizing in different layouts")
    print("   • Verify all your workflows still work")
    print()
    
    print("4. KEY CHANGES to be aware of:")
    changes = [
        ("Navigation", "J/K now move up/down (was K/J for down/up)"),
        ("Resizing", "Ctrl+H/L for smart shrink/grow (was Shift+H/L)"),
        ("Layout switching", "Added B for BSP, Shift+T for MonadTall"),
        ("New features", "Shift+F for fullscreen, smart normalize")
    ]
    
    for category, change in changes:
        print(f"   • {category}: {change}")
    
    print()
    print("5. BENEFITS after migration:")
    benefits = [
        "No more error messages when using unsupported layout commands",
        "Consistent behavior across all layouts",
        "Smart commands that adapt to current layout",
        "More intuitive navigation (J=up, K=down like vim)",
        "Quick access to all available layouts"
    ]
    
    for benefit in benefits:
        print(f"   ✅ {benefit}")


if __name__ == "__main__":
    analyze_key_binding_issues()
