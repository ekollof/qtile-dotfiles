#!/usr/bin/env python3
"""
Compliance audit script for qtile configuration project

Checks code compliance against project rules defined in .github/copilot-instructions.md:
- Python 3.10+ features and modern syntax
- Doxygen-compatible documentation standards
- Cross-platform portability requirements
- Code quality standards (PEP 8, type hints, error handling)

@brief Automated compliance auditing tool for qtile project standards
@author qtile configuration system
"""

import ast
import re
import sys
from pathlib import Path
from typing import Any


class ComplianceAuditor:
    """
    @brief Automated compliance checker for qtile project standards

    Analyzes Python source files for compliance with project coding standards
    including modern Python syntax, documentation, portability, and quality.
    """

    def __init__(self, project_root: str | Path):
        """
        @brief Initialize compliance auditor
        @param project_root: Root directory of the qtile project
        """
        self.project_root = Path(project_root)
        self.issues: list[dict[str, Any]] = []
        self.stats = {
            "files_checked": 0,
            "total_issues": 0,
            "python_syntax": 0,
            "documentation": 0,
            "portability": 0,
            "code_quality": 0
        }

    def audit_project(self) -> dict[str, Any]:
        """
        @brief Run comprehensive compliance audit on the project
        @return Dictionary containing audit results and statistics
        """
        print("🔍 Starting Qtile Project Compliance Audit")
        print("=" * 45)

        # Find all Python files
        python_files = list(self.project_root.glob("**/*.py"))

        for file_path in python_files:
            # Skip __pycache__, generated files, and scripts directory
            if "__pycache__" in str(file_path) or ".pyc" in str(file_path) or "scripts/" in str(file_path):
                continue

            self._audit_file(file_path)
            self.stats["files_checked"] += 1

        # Generate summary
        return self._generate_summary()

    def _audit_file(self, file_path: Path) -> None:
        """
        @brief Audit a single Python file for compliance issues
        @param file_path: Path to the Python file to audit
        """
        try:
            content = file_path.read_text(encoding='utf-8')

            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self._add_issue("syntax_error", file_path, 0,
                              f"Syntax error: {e}")
                return

            # Run all compliance checks
            self._check_python_syntax(file_path, content, tree)
            self._check_documentation(file_path, content, tree)
            self._check_portability(file_path, content)
            self._check_code_quality(file_path, content, tree)

        except Exception as e:
            self._add_issue("file_error", file_path, 0,
                          f"Could not process file: {e}")

    def _check_python_syntax(self, file_path: Path, content: str, tree: ast.AST) -> None:
        """
        @brief Check for modern Python 3.10+ syntax compliance
        @param file_path: Path to the file being checked
        @param content: File content as string
        @param tree: Parsed AST tree
        """
        lines = content.split('\n')

        # Check for legacy type annotations
        legacy_types = [
            (r'from typing import.*\bDict\b', "Use 'dict' instead of 'Dict' (Python 3.9+)"),
            (r'from typing import.*\bList\b', "Use 'list' instead of 'List' (Python 3.9+)"),
            (r'from typing import.*\bTuple\b', "Use 'tuple' instead of 'Tuple' (Python 3.9+)"),
            (r'from typing import.*\bSet\b', "Use 'set' instead of 'Set' (Python 3.9+)"),
            (r'from typing import.*\bUnion\b', "Use '|' union syntax instead of 'Union' (Python 3.10+)"),
            (r'from typing import.*\bOptional\b', "Use '| None' instead of 'Optional' (Python 3.10+)"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, message in legacy_types:
                if re.search(pattern, line):
                    self._add_issue("python_syntax", file_path, i, message)

        # Check for legacy type usage in annotations
        type_patterns = [
            (r'\bDict\[[^\]]+\]', "Use 'dict[...]' instead of 'dict[...]'"),
            (r'\bList\[[^\]]+\]', "Use 'list[...]' instead of 'list[...]'"),
            (r'\bTuple\[[^\]]+\]', "Use 'tuple[...]' instead of 'tuple[...]'"),
            (r'\bUnion\[[^\]]+\]', "Use '|' union syntax instead of '...'"),
            (r'\bOptional\[[^\]]+\]', "Use '... | None' instead of '... | None'"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, message in type_patterns:
                if re.search(pattern, line):
                    self._add_issue("python_syntax", file_path, i, message)

        # Check for os.path usage
        if re.search(r'import os\.path|from os import path', content):
            self._add_issue("python_syntax", file_path, 0,
                          "Use 'pathlib.Path' instead of 'os.path' for better portability")

        # Look for match statements usage (good practice for Python 3.10+)
        has_match = any(isinstance(node, ast.Match) for node in ast.walk(tree))
        has_if_elif_chains = self._detect_long_if_elif_chains(tree)

        if has_if_elif_chains and not has_match:
            self._add_issue("python_syntax", file_path, 0,
                          "Consider using 'match' statements instead of long if/elif chains")

    def _check_documentation(self, file_path: Path, content: str, tree: ast.AST) -> None:
        """
        @brief Check documentation compliance (doxygen format)
        @param file_path: Path to the file being checked
        @param content: File content as string
        @param tree: Parsed AST tree
        """
        # Check module docstring
        if isinstance(tree, ast.Module):
            module_docstring = ast.get_docstring(tree)
            if not module_docstring:
                self._add_issue("documentation", file_path, 1,
                              "Module missing docstring")
            elif not self._is_doxygen_format(module_docstring):
                self._add_issue("documentation", file_path, 1,
                              "Module docstring not in doxygen format (@brief, etc.)")

        # Check functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._check_function_docs(file_path, node)
            elif isinstance(node, ast.AsyncFunctionDef):
                self._check_async_function_docs(file_path, node)
            elif isinstance(node, ast.ClassDef):
                self._check_class_docs(file_path, node)

    def _check_portability(self, file_path: Path, content: str) -> None:
        """
        @brief Check cross-platform portability compliance
        @param file_path: Path to the file being checked
        @param content: File content as string
        """
        # Check for platform-specific imports/calls
        platform_specific = [
            (r'import winreg|from winreg', "Windows-specific module"),
            (r'import pwd|from pwd', "Unix-specific module (consider alternatives)"),
            (r'import grp|from grp', "Unix-specific module (consider alternatives)"),
            (r'\.chown\(', "Unix-specific operation"),
            (r'\.chmod\(', "Unix-specific operation (ensure cross-platform)"),
            (r'/proc/', "Linux-specific filesystem path"),
            (r'/sys/', "Linux-specific filesystem path"),
            (r'C:\\|\\\\', "Windows-specific path format"),
        ]

        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, message in platform_specific:
                if re.search(pattern, line):
                    self._add_issue("portability", file_path, i, message)

        # Check for hardcoded paths
        hardcoded_paths = [
            (r'"/usr/[^"]*"', "Hardcoded Unix path - consider making configurable"),
            (r'"/etc/[^"]*"', "Hardcoded Unix path - consider making configurable"),
            (r'"/var/[^"]*"', "Hardcoded Unix path - consider making configurable"),
            (r'"/tmp/[^"]*"', "Use tempfile module instead of hardcoded /tmp"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, message in hardcoded_paths:
                if re.search(pattern, line):
                    self._add_issue("portability", file_path, i, message)

    def _check_code_quality(self, file_path: Path, content: str, tree: ast.AST) -> None:
        """
        @brief Check code quality standards (PEP 8, type hints, error handling)
        @param file_path: Path to the file being checked
        @param content: File content as string
        @param tree: Parsed AST tree
        """
        # Check for missing type hints
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.returns and node.name not in ['__init__', '__str__', '__repr__']:
                    self._add_issue("code_quality", file_path, node.lineno,
                                  f"Function '{node.name}' missing return type annotation")

                # Check function parameters for type hints
                for arg in node.args.args:
                    if not arg.annotation and arg.arg != 'self':
                        self._add_issue("code_quality", file_path, node.lineno,
                                      f"Parameter '{arg.arg}' in '{node.name}' missing type annotation")

        # Check for bare except clauses
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self._add_issue("code_quality", file_path, node.lineno,
                                  "Bare 'except:' clause - specify exception types")

        # Check function complexity (simplified cyclomatic complexity)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    self._add_issue("code_quality", file_path, node.lineno,
                                  f"Function '{node.name}' has high complexity ({complexity}) - consider refactoring")

        # Check line length (PEP 8)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 88:  # Slightly more lenient than strict PEP 8
                self._add_issue("code_quality", file_path, i,
                              f"Line too long ({len(line)} characters) - PEP 8 recommends ≤79")

    def _detect_long_if_elif_chains(self, tree: ast.AST) -> bool:
        """
        @brief Detect long if/elif chains that could be match statements
        @param tree: AST tree to analyze
        @return True if long if/elif chains found
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                elif_count = 0
                current = node
                while hasattr(current, 'orelse') and current.orelse:
                    if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                        elif_count += 1
                        current = current.orelse[0]
                    else:
                        break
                if elif_count >= 3:  # 3+ elif clauses
                    return True
        return False

    def _is_doxygen_format(self, docstring: str) -> bool:
        """
        @brief Check if docstring follows doxygen format
        @param docstring: Docstring to check
        @return True if doxygen format detected
        """
        doxygen_tags = ['@brief', '@param', '@return', '@throws']
        return any(tag in docstring for tag in doxygen_tags)

    def _check_function_docs(self, file_path: Path, node: ast.FunctionDef) -> None:
        """
        @brief Check function documentation compliance
        @param file_path: Path to the file
        @param node: Function AST node
        """
        docstring = ast.get_docstring(node)
        if not docstring:
            if not node.name.startswith('_'):  # Public functions need docs
                self._add_issue("documentation", file_path, node.lineno,
                              f"Public function '{node.name}' missing docstring")
        else:
            if not self._is_doxygen_format(docstring):
                self._add_issue("documentation", file_path, node.lineno,
                              f"Function '{node.name}' docstring not in doxygen format")

    def _check_async_function_docs(self, file_path: Path, node: ast.AsyncFunctionDef) -> None:
        """
        @brief Check async function documentation compliance
        @param file_path: Path to the file
        @param node: Async function AST node
        """
        docstring = ast.get_docstring(node)
        if not docstring:
            if not node.name.startswith('_'):  # Public functions need docs
                self._add_issue("documentation", file_path, node.lineno,
                              f"Public async function '{node.name}' missing docstring")
        else:
            if not self._is_doxygen_format(docstring):
                self._add_issue("documentation", file_path, node.lineno,
                              f"Async function '{node.name}' docstring not in doxygen format")

    def _check_class_docs(self, file_path: Path, node: ast.ClassDef) -> None:
        """
        @brief Check class documentation compliance
        @param file_path: Path to the file
        @param node: Class AST node
        """
        docstring = ast.get_docstring(node)
        if not docstring:
            self._add_issue("documentation", file_path, node.lineno,
                          f"Class '{node.name}' missing docstring")
        elif not self._is_doxygen_format(docstring):
            self._add_issue("documentation", file_path, node.lineno,
                          f"Class '{node.name}' docstring not in doxygen format")

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        @brief Calculate simplified cyclomatic complexity
        @param node: Function AST node
        @return Complexity score
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp)):
                complexity += 1

        return complexity

    def _add_issue(self, category: str, file_path: Path, line_number: int, message: str) -> None:
        """
        @brief Add a compliance issue to the results
        @param category: Issue category (python_syntax, documentation, etc.)
        @param file_path: Path to file with issue
        @param line_number: Line number (0 for file-level issues)
        @param message: Description of the issue
        """
        issue = {
            "category": category,
            "file": str(file_path.relative_to(self.project_root)),
            "line": line_number,
            "message": message
        }
        self.issues.append(issue)
        self.stats["total_issues"] += 1
        self.stats[category] += 1

    def _generate_summary(self) -> dict[str, Any]:
        """
        @brief Generate audit summary report
        @return Dictionary containing complete audit results
        """
        print("\n📊 Audit Summary")
        print("=" * 16)
        print(f"Files checked: {self.stats['files_checked']}")
        print(f"Total issues: {self.stats['total_issues']}")
        print()

        categories = [
            ("Python Syntax", "python_syntax"),
            ("Documentation", "documentation"),
            ("Portability", "portability"),
            ("Code Quality", "code_quality")
        ]

        for name, key in categories:
            count = self.stats[key]
            print(f"{name:15} {count:3} issues")

        # Group issues by category for detailed report
        issues_by_category = {}
        for issue in self.issues:
            category = issue["category"]
            if category not in issues_by_category:
                issues_by_category[category] = []
            issues_by_category[category].append(issue)

        # Print detailed issues
        for name, key in categories:
            if key in issues_by_category and issues_by_category[key]:
                print(f"\n🔍 {name} Issues")
                print("-" * (len(name) + 8))

                for issue in issues_by_category[key][:10]:  # Limit to first 10
                    line_info = f":{issue['line']}" if issue['line'] > 0 else ""
                    print(f"  {issue['file']}{line_info}")
                    print(f"    {issue['message']}")

                if len(issues_by_category[key]) > 10:
                    remaining = len(issues_by_category[key]) - 10
                    print(f"    ... and {remaining} more issues")

        # Calculate compliance score
        total_possible_issues = self.stats["files_checked"] * 10  # Rough estimate
        compliance_score = max(0, 100 - (self.stats["total_issues"] / max(1, total_possible_issues) * 100))

        print(f"\n📈 Compliance Score: {compliance_score:.1f}%")

        if compliance_score >= 90:
            print("🎉 Excellent compliance!")
        elif compliance_score >= 75:
            print("✅ Good compliance - minor issues to address")
        elif compliance_score >= 50:
            print("⚠️  Moderate compliance - several improvements needed")
        else:
            print("❌ Low compliance - significant improvements required")

        return {
            "stats": self.stats,
            "issues": self.issues,
            "issues_by_category": issues_by_category,
            "compliance_score": compliance_score
        }


def main():
    """
    @brief Main entry point for compliance auditor
    """
    import argparse

    parser = argparse.ArgumentParser(description="Audit qtile project compliance")
    parser.add_argument("--project-root", "-r", default=".",
                       help="Root directory of the qtile project")
    parser.add_argument("--category", "-c",
                       choices=["python_syntax", "documentation", "portability", "code_quality"],
                       help="Check only specific category")
    parser.add_argument("--summary-only", "-s", action="store_true",
                       help="Show only summary statistics")

    args = parser.parse_args()

    try:
        auditor = ComplianceAuditor(args.project_root)
        results = auditor.audit_project()

        # Exit with non-zero if significant issues found
        if results["compliance_score"] < 75:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠️  Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
