#!/usr/bin/env python3
"""
Automated legacy type annotation fixer for qtile project

Converts legacy typing imports and annotations to modern Python 3.10+ syntax:
- dict[K, V] → dict[K, V]
- list[T] → list[T]
- tuple[T, ...] → tuple[T, ...]
- set[T] → set[T]
- A | B → A | B
- T | None → T | None

@brief Automated modernization tool for Python type annotations
@author qtile configuration system
"""

import re
import sys
from pathlib import Path
from typing import Any


class LegacyTypeFixer:
    """
    @brief Automated fixer for legacy Python type annotations

    Modernizes type annotations to use Python 3.10+ syntax while preserving
    functionality and maintaining proper import statements.
    """

    def __init__(self, project_root: str | Path):
        """
        @brief Initialize the legacy type fixer
        @param project_root: Root directory of the project to fix
        """
        self.project_root = Path(project_root)
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "dict_fixes": 0,
            "list_fixes": 0,
            "tuple_fixes": 0,
            "set_fixes": 0,
            "union_fixes": 0,
            "optional_fixes": 0,
            "import_cleanups": 0
        }

    def fix_project(self) -> dict[str, Any]:
        """
        @brief Fix all Python files in the project
        @return Dictionary containing fix statistics
        """
        print("🔧 Fixing Legacy Type Annotations")
        print("=" * 35)

        # Find all Python files
        python_files = list(self.project_root.glob("**/*.py"))

        for file_path in python_files:
            # Skip __pycache__ and other generated files
            if "__pycache__" in str(file_path) or ".pyc" in str(file_path):
                continue

            self._fix_file(file_path)
            self.stats["files_processed"] += 1

        return self._generate_summary()

    def _fix_file(self, file_path: Path) -> None:
        """
        @brief Fix legacy type annotations in a single file
        @param file_path: Path to the Python file to fix
        """
        try:
            original_content = file_path.read_text(encoding='utf-8')
            modified_content = original_content
            file_changed = False

            # Track what legacy types are used to clean imports later
            legacy_types_used = set()

            # Fix type annotations
            modified_content, changes = self._fix_type_annotations(modified_content)
            if changes:
                file_changed = True
                for change_type, count in changes.items():
                    self.stats[f"{change_type}_fixes"] += count
                    legacy_types_used.add(change_type.capitalize())

            # Clean up imports
            if legacy_types_used:
                modified_content, import_cleaned = self._clean_imports(modified_content, legacy_types_used)
                if import_cleaned:
                    file_changed = True
                    self.stats["import_cleanups"] += 1

            # Write back if changed
            if file_changed:
                file_path.write_text(modified_content, encoding='utf-8')
                self.stats["files_modified"] += 1
                relative_path = file_path.relative_to(self.project_root)
                print(f"✅ Fixed {relative_path}")

        except Exception as e:
            relative_path = file_path.relative_to(self.project_root)
            print(f"❌ Error fixing {relative_path}: {e}")

    def _fix_type_annotations(self, content: str) -> tuple[str, dict[str, int]]:
        """
        @brief Fix type annotations in file content
        @param content: File content to fix
        @return Tuple of (fixed_content, changes_dict)
        """
        changes = {
            "dict": 0,
            "list": 0,
            "tuple": 0,
            "set": 0,
            "union": 0,
            "optional": 0
        }

        # Fix dict[K, V] → dict[K, V]
        dict_pattern = r'\bDict\[([^\]]+)\]'
        new_content, dict_count = re.subn(dict_pattern, r'dict[\1]', content)
        changes["dict"] = dict_count
        content = new_content

        # Fix list[T] → list[T]
        list_pattern = r'\bList\[([^\]]+)\]'
        new_content, list_count = re.subn(list_pattern, r'list[\1]', content)
        changes["list"] = list_count
        content = new_content

        # Fix tuple[T, ...] → tuple[T, ...]
        tuple_pattern = r'\bTuple\[([^\]]+)\]'
        new_content, tuple_count = re.subn(tuple_pattern, r'tuple[\1]', content)
        changes["tuple"] = tuple_count
        content = new_content

        # Fix set[T] → set[T]
        set_pattern = r'\bSet\[([^\]]+)\]'
        new_content, set_count = re.subn(set_pattern, r'set[\1]', content)
        changes["set"] = set_count
        content = new_content

        # Fix T | None → T | None (more complex)
        optional_pattern = r'\bOptional\[([^\]]+)\]'
        new_content, optional_count = re.subn(optional_pattern, r'\1 | None', content)
        changes["optional"] = optional_count
        content = new_content

        # Fix A | B → A | B (most complex)
        content, union_count = self._fix_union_types(content)
        changes["union"] = union_count

        return content, changes

    def _fix_union_types(self, content: str) -> tuple[str, int]:
        """
        @brief Fix A | B | ... → A | B | ... type annotations
        @param content: File content to fix
        @return Tuple of (fixed_content, number_of_fixes)
        """
        union_count = 0

        # Find all ... patterns
        union_pattern = r'\bUnion\[([^\]]+)\]'

        def replace_union(match):
            nonlocal union_count
            union_content = match.group(1)

            # Split by comma but handle nested brackets
            types = self._split_union_types(union_content)

            # Join with | operator
            union_replacement = ' | '.join(type_str.strip() for type_str in types)
            union_count += 1

            return union_replacement

        new_content = re.sub(union_pattern, replace_union, content)
        return new_content, union_count

    def _split_union_types(self, union_content: str) -> list[str]:
        """
        @brief Split union type content handling nested brackets
        @param union_content: Content inside ...
        @return List of individual type strings
        """
        types = []
        current_type = ""
        bracket_depth = 0

        for char in union_content:
            if char == '[':
                bracket_depth += 1
                current_type += char
            elif char == ']':
                bracket_depth -= 1
                current_type += char
            elif char == ',' and bracket_depth == 0:
                types.append(current_type.strip())
                current_type = ""
            else:
                current_type += char

        if current_type.strip():
            types.append(current_type.strip())

        return types

    def _clean_imports(self, content: str, legacy_types_used: set[str]) -> tuple[str, bool]:
        """
        @brief Clean up typing imports that are no longer needed
        @param content: File content to clean
        @param legacy_types_used: Set of legacy types that were replaced
        @return Tuple of (cleaned_content, was_modified)
        """
        lines = content.split('\n')
        modified = False

        for i, line in enumerate(lines):
            # Check for typing imports
            if line.strip().startswith('from typing import'):
                # Extract the imported items
                import_match = re.match(r'from typing import\s+(.+)', line.strip())
                if import_match:
                    imports_str = import_match.group(1)

                    # Split imports handling multi-line
                    if '(' in imports_str:
                        # Multi-line import - need to handle differently
                        continue

                    # Single line import
                    imports = [imp.strip() for imp in imports_str.split(',')]

                    # Remove legacy types that we fixed
                    remaining_imports = []
                    for imp in imports:
                        if imp not in legacy_types_used:
                            remaining_imports.append(imp)

                    # Rebuild import line
                    if not remaining_imports:
                        # Remove entire import line
                        lines[i] = ""
                        modified = True
                    elif len(remaining_imports) != len(imports):
                        # Some imports removed
                        new_import_line = f"from typing import {', '.join(remaining_imports)}"
                        lines[i] = new_import_line
                        modified = True

            # Handle individual imports like "from typing import Dict"
            elif re.match(r'from typing import\s+\w+$', line.strip()):
                import_match = re.match(r'from typing import\s+(\w+)', line.strip())
                if import_match and import_match.group(1) in legacy_types_used:
                    lines[i] = ""
                    modified = True

        if modified:
            # Clean up empty lines that might have been created
            cleaned_lines = []
            for line in lines:
                if line.strip() or (cleaned_lines and cleaned_lines[-1].strip()):
                    cleaned_lines.append(line)

            # Remove trailing empty lines
            while cleaned_lines and not cleaned_lines[-1].strip():
                cleaned_lines.pop()

            return '\n'.join(cleaned_lines), True

        return content, False

    def _generate_summary(self) -> dict[str, Any]:
        """
        @brief Generate summary of fixes applied
        @return Dictionary containing fix statistics and summary
        """
        print(f"\n📊 Fix Summary")
        print("=" * 14)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files modified:  {self.stats['files_modified']}")
        print()

        fix_types = [
            ("Dict → dict", "dict_fixes"),
            ("List → list", "list_fixes"),
            ("Tuple → tuple", "tuple_fixes"),
            ("Set → set", "set_fixes"),
            ("Union → |", "union_fixes"),
            ("Optional → | None", "optional_fixes"),
        ]

        total_fixes = 0
        for name, key in fix_types:
            count = self.stats[key]
            total_fixes += count
            if count > 0:
                print(f"{name:20} {count:3} fixes")

        if self.stats["import_cleanups"] > 0:
            print(f"{'Import cleanups':20} {self.stats['import_cleanups']:3} fixes")

        print(f"\n✅ Total fixes applied: {total_fixes}")

        if total_fixes > 0:
            print("🎉 Successfully modernized type annotations!")
            print("   Your code now uses Python 3.10+ type syntax.")
        else:
            print("ℹ️  No legacy type annotations found.")

        return {
            "stats": self.stats,
            "total_fixes": total_fixes,
            "success": True
        }


def main():
    """
    @brief Main entry point for legacy type fixer
    """
    import argparse

    parser = argparse.ArgumentParser(description="Fix legacy type annotations")
    parser.add_argument("--project-root", "-r", default=".",
                       help="Root directory of the project to fix")
    parser.add_argument("--dry-run", "-n", action="store_true",
                       help="Show what would be fixed without making changes")

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print("=" * 45)

    try:
        fixer = LegacyTypeFixer(args.project_root)

        if args.dry_run:
            # TODO: Implement dry run mode
            print("Dry run mode not yet implemented")
            return

        results = fixer.fix_project()

        if results["total_fixes"] > 0:
            print("\n💡 Recommendations:")
            print("• Test your code to ensure type changes don't break anything")
            print("• Run your linter/type checker to verify the changes")
            print("• Consider adding 'from __future__ import annotations' for forward compatibility")

    except KeyboardInterrupt:
        print("\n⚠️  Fix interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fix failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
