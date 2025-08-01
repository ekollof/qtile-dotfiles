#!/usr/bin/env python3
"""
Window Rules Consistency Analysis for qtile configuration
Analyzes all window rules across the configuration for consistency and completeness
"""

import sys
sys.path.insert(0, '/home/ekollof/.config/qtile')

def analyze_window_rules():
    """Analyze window rules for consistency"""
    
    print("=== Window Rules Consistency Analysis ===\n")
    
    # Floating rules from groups.py
    floating_rules = [
        # Default qtile rules (included via *layout.Floating.default_float_rules)
        "Default qtile floating rules (included automatically)",
        
        # Custom floating rules
        ("wm_class", "confirm", "Confirmation dialogs"),
        ("wm_class", "dialog", "Generic dialog windows"),
        ("wm_class", "download", "Download windows"),
        ("wm_class", "error", "Error dialogs"),
        ("wm_class", "file_progress", "File progress dialogs"),
        ("wm_class", "notification", "Notification windows"),
        ("wm_class", "splash", "Splash screens"),
        ("wm_class", "toolbar", "Toolbar windows"),
        ("wm_class", "pinentry-gtk-2", "GTK2 PIN entry"),
        ("wm_class", "confirmreset", "gitk confirmation"),
        ("wm_class", "makebranch", "gitk branch creation"),
        ("wm_class", "maketag", "gitk tag creation"),
        ("title", "branchdialog", "gitk branch dialog"),
        ("title", "pinentry", "PIN entry by title"),
        ("wm_class", "pinentry", "PIN entry by class"),
        ("wm_class", "ssh-askpass", "SSH password prompt"),
        ("wm_class", "krunner", "KDE application launcher"),
        ("title", "Desktop — Plasma", "KDE desktop")
    ]
    
    # Hook-based floating rules from hooks.py
    hook_floating_classes = [
        ("wm_class", "nm-connection-editor", "NetworkManager connection editor"),
        ("wm_class", "pavucontrol", "PulseAudio volume control"),
        ("wm_class", "origin.exe", "Origin game launcher")
    ]
    
    # Transient window rules
    transient_rules = [
        "Windows with WM_TRANSIENT_FOR hint",
        "Windows with max_width hint"
    ]
    
    print("1. FLOATING RULES (from groups.py):")
    print(f"   Default qtile rules: Included automatically")
    print(f"   Custom rules: {len(floating_rules)-1}")
    
    for i, rule in enumerate(floating_rules[1:], 1):
        match_type, match_value, description = rule
        print(f"   {i:2d}. {match_type}='{match_value}' - {description}")
    
    print(f"\n2. HOOK-BASED FLOATING RULES (from hooks.py):")
    print(f"   Dynamic rules: {len(hook_floating_classes)}")
    
    for i, rule in enumerate(hook_floating_classes, 1):
        match_type, match_value, description = rule
        print(f"   {i:2d}. {match_type}='{match_value}' - {description}")
    
    print(f"\n3. TRANSIENT WINDOW RULES:")
    for i, rule in enumerate(transient_rules, 1):
        print(f"   {i:2d}. {rule}")
    
    print(f"\n4. CONSISTENCY ANALYSIS:")
    
    # Check for consistency issues
    issues = []
    recommendations = []
    
    # Check for duplicate rules
    all_wm_classes = []
    all_titles = []
    
    for rule in floating_rules[1:]:
        if rule[0] == "wm_class":
            all_wm_classes.append(rule[1])
        elif rule[0] == "title":
            all_titles.append(rule[1])
    
    for rule in hook_floating_classes:
        if rule[0] == "wm_class":
            all_wm_classes.append(rule[1])
        elif rule[0] == "title":
            all_titles.append(rule[1])
    
    # Check for duplicates
    duplicate_classes = set([x for x in all_wm_classes if all_wm_classes.count(x) > 1])
    duplicate_titles = set([x for x in all_titles if all_titles.count(x) > 1])
    
    if duplicate_classes:
        issues.append(f"Duplicate wm_class rules: {', '.join(duplicate_classes)}")
    
    if duplicate_titles:
        issues.append(f"Duplicate title rules: {', '.join(duplicate_titles)}")
    
    # Check for PIN entry inconsistency
    pinentry_rules = [rule for rule in floating_rules[1:] if 'pinentry' in rule[1].lower()]
    if len(pinentry_rules) > 1:
        issues.append("Multiple PIN entry rules found - may cause conflicts")
    
    # Common missing rules
    common_floating_apps = [
        "Calculator applications",
        "Color pickers", 
        "System monitors (htop, etc.)",
        "Password managers",
        "Screenshot tools",
        "File pickers/choosers",
        "System settings panels"
    ]
    
    recommendations.extend([
        "Consider adding rules for calculator apps (gnome-calculator, kcalc)",
        "Add rules for screenshot tools (flameshot, spectacle)",
        "Consider system monitor floating rules (htop in terminal)",
        "Add file picker rules if using specific applications"
    ])
    
    if issues:
        print("   🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"      ❌ {issue}")
    else:
        print("   ✅ No consistency issues found")
    
    print(f"\n5. RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    print(f"\n6. RULE COVERAGE:")
    
    coverage_categories = {
        "Dialog windows": ["confirm", "dialog", "error"],
        "Development tools": ["confirmreset", "makebranch", "maketag", "branchdialog"],
        "Security/Auth": ["pinentry-gtk-2", "pinentry", "ssh-askpass"],
        "System utilities": ["nm-connection-editor", "pavucontrol"],
        "DE integration": ["krunner", "Desktop — Plasma"],
        "Gaming": ["origin.exe"],
        "File operations": ["download", "file_progress"],
        "UI elements": ["splash", "toolbar", "notification"]
    }
    
    for category, rules in coverage_categories.items():
        covered = []
        for rule in rules:
            if any(rule in str(fr) for fr in floating_rules + hook_floating_classes):
                covered.append(rule)
        coverage = len(covered) / len(rules) * 100
        print(f"   {category:<20} {coverage:6.1f}% ({len(covered)}/{len(rules)})")
    
    print(f"\n7. SUMMARY:")
    total_rules = len(floating_rules) - 1 + len(hook_floating_classes) + len(transient_rules)
    print(f"   📊 Total floating rules: {total_rules}")
    print(f"   🎯 Static rules: {len(floating_rules)-1}")
    print(f"   ⚡ Dynamic rules: {len(hook_floating_classes)}")
    print(f"   🔄 Automatic rules: {len(transient_rules)}")
    
    if not issues:
        print(f"   ✅ Configuration is consistent and well-organized")
    else:
        print(f"   ⚠️  Minor issues found - see recommendations above")


if __name__ == "__main__":
    analyze_window_rules()
