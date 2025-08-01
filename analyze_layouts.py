#!/usr/bin/env python3
"""
Layout analysis module for qtile
Analyzes layouts and their supported commands for consistent key bindings
"""

from libqtile import layout
from libqtile.log_utils import logger


class LayoutAnalyzer:
    """Analyzes layout capabilities and generates consistent key bindings"""
    
    def __init__(self):
        self.layout_capabilities = self._analyze_layouts()
    
    def _analyze_layouts(self):
        """Analyze what commands each layout supports"""
        
        # Create instances of each layout to test their capabilities
        test_layouts = {
            'tile': layout.Tile(),
            'monadtall': layout.MonadTall(),
            'matrix': layout.Matrix(),
            'bsp': layout.Bsp(),
            'max': layout.Max(),
            'floating': layout.Floating()
        }
        
        # Define common layout commands we want to test
        commands_to_test = [
            'up', 'down', 'left', 'right',
            'shuffle_up', 'shuffle_down', 'shuffle_left', 'shuffle_right',
            'grow', 'shrink', 'grow_main', 'shrink_main',
            'increase_ratio', 'decrease_ratio',
            'normalize', 'maximize', 'minimize',
            'next', 'previous',
            'rotate', 'flip',
            'toggle_split', 'split',
            'add', 'remove',
            'increase_nmaster', 'decrease_nmaster'
        ]
        
        capabilities = {}
        
        for layout_name, layout_instance in test_layouts.items():
            layout_caps = []
            
            for command in commands_to_test:
                if hasattr(layout_instance, command):
                    # Check if it's a callable method
                    attr = getattr(layout_instance, command)
                    if callable(attr):
                        layout_caps.append(command)
            
            capabilities[layout_name] = layout_caps
            
        return capabilities
    
    def get_common_commands(self):
        """Get commands supported by all layouts"""
        if not self.layout_capabilities:
            return []
            
        all_layouts = list(self.layout_capabilities.keys())
        common = set(self.layout_capabilities[all_layouts[0]])
        
        for layout_name in all_layouts[1:]:
            common = common.intersection(set(self.layout_capabilities[layout_name]))
            
        return sorted(list(common))
    
    def get_layout_specific_commands(self, layout_name):
        """Get commands specific to a particular layout"""
        if layout_name not in self.layout_capabilities:
            return []
        return self.layout_capabilities[layout_name]
    
    def get_incompatible_commands(self, layout_name):
        """Get commands that don't work with a specific layout"""
        if layout_name not in self.layout_capabilities:
            return []
            
        all_commands = set()
        for caps in self.layout_capabilities.values():
            all_commands.update(caps)
            
        layout_commands = set(self.layout_capabilities[layout_name])
        return sorted(list(all_commands - layout_commands))
    
    def analyze_key_binding_consistency(self, current_bindings):
        """Analyze current key bindings for layout consistency issues"""
        issues = []
        recommendations = []
        
        # Extract layout commands from current bindings
        layout_commands_in_bindings = []
        for binding in current_bindings:
            if hasattr(binding, 'commands'):
                for cmd in binding.commands:
                    if hasattr(cmd, 'selectors') and 'layout' in str(cmd.selectors):
                        layout_commands_in_bindings.append(cmd)
        
        # Check for problematic bindings
        problematic_layouts = ['max']  # Layouts that don't support many commands
        
        for layout_name in problematic_layouts:
            incompatible = self.get_incompatible_commands(layout_name)
            if incompatible:
                issues.append(f"Layout '{layout_name}' doesn't support: {', '.join(incompatible)}")
        
        # Generate recommendations
        common_commands = self.get_common_commands()
        recommendations.append(f"Safe commands for all layouts: {', '.join(common_commands)}")
        
        return {
            'issues': issues,
            'recommendations': recommendations,
            'layout_capabilities': self.layout_capabilities,
            'common_commands': common_commands
        }
    
    def generate_layout_aware_bindings(self):
        """Generate layout-aware key binding suggestions"""
        suggestions = {
            'universal': [],  # Work with all layouts
            'conditional': {},  # Layout-specific bindings
            'problematic': []  # Bindings that might cause issues
        }
        
        # Universal bindings (work with all layouts)
        universal_mappings = [
            ('j', 'up', 'Move focus up'),
            ('k', 'down', 'Move focus down'),
            ('shift+j', 'shuffle_up', 'Move window up'),
            ('shift+k', 'shuffle_down', 'Move window down'),
        ]
        
        for key, command, description in universal_mappings:
            if all(command in caps for caps in self.layout_capabilities.values()):
                suggestions['universal'].append({
                    'key': key,
                    'command': f'lazy.layout.{command}()',
                    'description': description
                })
        
        # Layout-specific bindings
        specific_mappings = [
            ('shift+l', 'grow', 'Grow window', ['tile', 'monadtall', 'bsp']),
            ('shift+h', 'shrink', 'Shrink window', ['tile', 'monadtall', 'bsp']),
            ('control+l', 'increase_ratio', 'Increase ratio', ['monadtall']),
            ('control+h', 'decrease_ratio', 'Decrease ratio', ['monadtall']),
            ('shift+space', 'rotate', 'Rotate windows', ['tile', 'bsp']),
            ('shift+return', 'toggle_split', 'Toggle split', ['tile']),
        ]
        
        for key, command, description, compatible_layouts in specific_mappings:
            for layout_name in compatible_layouts:
                if layout_name not in suggestions['conditional']:
                    suggestions['conditional'][layout_name] = []
                
                if command in self.layout_capabilities.get(layout_name, []):
                    suggestions['conditional'][layout_name].append({
                        'key': key,
                        'command': f'lazy.layout.{command}()',
                        'description': description
                    })
        
        return suggestions


def analyze_current_configuration():
    """Analyze the current qtile configuration for layout consistency"""
    analyzer = LayoutAnalyzer()
    
    print("=== Layout Capability Analysis ===\n")
    
    # Show capabilities for each layout
    for layout_name, capabilities in analyzer.layout_capabilities.items():
        print(f"{layout_name.upper()} Layout:")
        print(f"  Supported commands ({len(capabilities)}): {', '.join(capabilities[:10])}")
        if len(capabilities) > 10:
            print(f"  ... and {len(capabilities) - 10} more")
        print()
    
    # Show common commands
    common = analyzer.get_common_commands()
    print(f"Commands supported by ALL layouts ({len(common)}):")
    print(f"  {', '.join(common)}")
    print()
    
    # Show problematic layouts
    print("Layout-specific limitations:")
    for layout_name in analyzer.layout_capabilities:
        incompatible = analyzer.get_incompatible_commands(layout_name)
        if incompatible:
            print(f"  {layout_name}: doesn't support {', '.join(incompatible[:5])}")
            if len(incompatible) > 5:
                print(f"    ... and {len(incompatible) - 5} more")
    print()
    
    # Generate suggestions
    suggestions = analyzer.generate_layout_aware_bindings()
    
    print("=== Key Binding Recommendations ===\n")
    
    print("UNIVERSAL bindings (work with all layouts):")
    for binding in suggestions['universal']:
        print(f"  {binding['key']:<15} {binding['command']:<30} # {binding['description']}")
    print()
    
    print("CONDITIONAL bindings (layout-specific):")
    for layout_name, bindings in suggestions['conditional'].items():
        if bindings:
            print(f"  {layout_name.upper()} layout:")
            for binding in bindings:
                print(f"    {binding['key']:<13} {binding['command']:<28} # {binding['description']}")
    print()


if __name__ == "__main__":
    analyze_current_configuration()
