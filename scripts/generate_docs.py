#!/usr/bin/env python3
"""
@brief Doxygen documentation generator for qtile configuration
@file generate_docs.py

This script generates HTML documentation from the qtile configuration codebase
using doxygen. It creates a Doxyfile configuINPUT                  = . \\
                         ./modules \\
                         ./modules/hook_management \\
                         ./modules/hotkey_management \\
                         ./modules/key_management \\
                         ./scriptson, removes old docs, and 
generates fresh documentation.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional
import sys
import os


class DoxygenDocGenerator:
    """
    @brief Generates doxygen documentation for the qtile configuration project
    """

    def __init__(self):
        """
        @brief Initialize the documentation generator
        """
        self.project_root = Path(__file__).parent.parent.resolve()
        self.docs_dir = self.project_root / "docs"
        self.html_dir = self.docs_dir / "html"
        self.doxyfile_path = self.project_root / "Doxyfile"
        
        # Project information
        self.project_name = "Qtile Configuration"
        self.project_version = "1.0.0"
        self.project_brief = "Modular qtile configuration with DPI awareness and color management"

    def check_dependencies(self) -> bool:
        """
        @brief Check if doxygen and doxypypy are available on the system
        @return True if both tools are installed and accessible, False otherwise
        """
        # Check doxygen
        try:
            result = subprocess.run(['doxygen', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ Doxygen found: {result.stdout.strip()}")
            else:
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("✗ Doxygen is not installed or not accessible")
            print("  Please install doxygen: sudo apt install doxygen (Debian/Ubuntu)")
            print("  Or: sudo pkg install doxygen (FreeBSD/OpenBSD)")
            return False

        # Check doxypypy
        try:
            result = subprocess.run(['doxypypy', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ Doxypypy found: {result.stdout.strip()}")
                return True
            else:
                # Try alternative check
                result = subprocess.run(['doxypypy', '--help'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("✓ Doxypypy found (help available)")
                    return True
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("✗ Doxypypy is not installed or not accessible")
            print("  Please install doxypypy: pip install doxypypy")
            print("  Or: sudo apt install doxypypy (if available)")
            return False

    def create_python_filter(self) -> bool:
        """
        @brief Create a Python filter script for doxygen
        @return True if filter was created successfully, False otherwise
        """
        filter_script = '''#!/usr/bin/env python3
"""
Python filter for doxygen to convert Python docstrings to doxygen format
"""
import sys
import re
import ast

def convert_docstring_to_doxygen(docstring):
    """Convert Python docstring to doxygen format"""
    if not docstring:
        return ""
    
    lines = docstring.strip().split('\\n')
    result = []
    
    # Handle different docstring formats
    if lines[0].strip().startswith('@brief'):
        # Already in doxygen format
        return '\\n'.join(['//! ' + line for line in lines])
    
    # Convert to doxygen format
    result.append('//! @brief ' + lines[0])
    
    for line in lines[1:]:
        line = line.strip()
        if line.startswith('@'):
            result.append('//! ' + line)
        elif line:
            result.append('//! ' + line)
    
    return '\\n'.join(result)

def process_python_file(content):
    """Process Python file and convert docstrings"""
    try:
        tree = ast.parse(content)
    except:
        return content
    
    lines = content.split('\\n')
    result = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                docstring = node.body[0].value.value
                if isinstance(docstring, str):
                    # Convert docstring
                    doxy_comment = convert_docstring_to_doxygen(docstring)
                    # Find the line number and insert comment
                    for i, line in enumerate(lines):
                        if i >= node.lineno - 1 and 'def ' in line or 'class ' in line:
                            lines.insert(i, doxy_comment)
                            break
    
    return '\\n'.join(lines)

if __name__ == '__main__':
    content = sys.stdin.read()
    processed = process_python_file(content)
    print(processed)
'''
        
        filter_path = self.project_root / "python_filter.py"
        try:
            with open(filter_path, 'w') as f:
                f.write(filter_script)
            filter_path.chmod(0o755)
            print(f"✓ Created Python filter at {filter_path}")
            return True
        except IOError as e:
            print(f"✗ Failed to create Python filter: {e}")
            return False

    def create_doxyfile(self) -> bool:
        """
        @brief Create a Doxyfile configuration for the project optimized for Python
        @return True if Doxyfile was created successfully, False otherwise
        """
        try:
            doxyfile_content = f"""# Doxyfile for Qtile Configuration Documentation - Python Optimized
# Generated automatically by generate_docs.py

#---------------------------------------------------------------------------
# Project related configuration options
#---------------------------------------------------------------------------
DOXYFILE_ENCODING      = UTF-8
PROJECT_NAME           = "{self.project_name}"
PROJECT_NUMBER         = {self.project_version}
PROJECT_BRIEF          = "{self.project_brief}"
PROJECT_LOGO           = 
OUTPUT_DIRECTORY       = docs
CREATE_SUBDIRS         = NO
ALLOW_UNICODE_NAMES    = YES
OUTPUT_LANGUAGE        = English
BRIEF_MEMBER_DESC      = YES
REPEAT_BRIEF           = YES
ALWAYS_DETAILED_SEC    = YES
INLINE_INHERITED_MEMB  = YES
FULL_PATH_NAMES        = NO

#---------------------------------------------------------------------------
# Build related configuration options - Python Optimized
#---------------------------------------------------------------------------
EXTRACT_ALL            = YES
EXTRACT_PRIVATE        = YES
EXTRACT_PACKAGE        = YES
EXTRACT_STATIC         = YES
EXTRACT_LOCAL_CLASSES  = YES
EXTRACT_LOCAL_METHODS  = YES
EXTRACT_ANON_NSPACES   = YES
HIDE_UNDOC_MEMBERS     = NO
HIDE_UNDOC_CLASSES     = NO
HIDE_FRIEND_COMPOUNDS  = NO
HIDE_IN_BODY_DOCS      = NO
INTERNAL_DOCS          = YES
CASE_SENSE_NAMES       = YES
HIDE_SCOPE_NAMES       = NO
HIDE_COMPOUND_REFERENCE= NO
SHOW_INCLUDE_FILES     = YES
SHOW_GROUPED_MEMB_INC  = NO
FORCE_LOCAL_INCLUDES   = NO
INLINE_INFO            = YES
SORT_MEMBER_DOCS       = YES
SORT_BRIEF_DOCS        = YES
SORT_MEMBERS_CTORS_1ST = NO
SORT_GROUP_NAMES       = NO
SORT_BY_SCOPE_NAME     = NO
STRICT_PROTO_MATCHING  = NO
GENERATE_TODOLIST      = YES
GENERATE_TESTLIST      = YES
GENERATE_BUGLIST       = YES
GENERATE_DEPRECATEDLIST= YES
ENABLED_SECTIONS       = 
MAX_INITIALIZER_LINES  = 30
SHOW_USED_FILES        = YES
SHOW_FILES             = YES
SHOW_NAMESPACES        = YES

#---------------------------------------------------------------------------
# Configuration options related to warning and progress messages
#---------------------------------------------------------------------------
QUIET                  = NO
WARNINGS               = YES
WARN_IF_UNDOCUMENTED   = NO
WARN_IF_DOC_ERROR      = YES
WARN_NO_PARAMDOC       = NO
WARN_AS_ERROR          = NO
WARN_FORMAT            = "$file:$line: $text"
WARN_LOGFILE           = 

#---------------------------------------------------------------------------
# Configuration options related to the input files - Python Optimized
#---------------------------------------------------------------------------
INPUT                  = modules/simple_color_management.py \\
                         modules/font_utils.py \\
                         modules/dpi_utils.py \\
                         modules/colors.py \\
                         scripts/generate_docs.py \\
                         qtile_config.py \\
                         config.py
INPUT_ENCODING         = UTF-8
FILE_PATTERNS          = *.py \\
                         *.md
RECURSIVE              = YES
EXCLUDE                = __pycache__ \\
                         .git \\
                         build \\
                         dist \\
                         *.pyc \\
                         test_docs_output \\
                         debug_docs \\
                         Doxyfile
EXCLUDE_SYMLINKS       = NO
EXCLUDE_PATTERNS       = */build/* \\
                         */__pycache__/* \\
                         */.git/* \\
                         */.*
EXCLUDE_SYMBOLS        = 
EXAMPLE_PATH           = examples
EXAMPLE_PATTERNS       = *.py
EXAMPLE_RECURSIVE      = YES
IMAGE_PATH             = icons

# Python-specific filters
FILTER_PATTERNS        = "*.py=/bin/doxypypy -a -c"
INPUT_FILTER           = 
FILTER_SOURCE_FILES    = YES
FILTER_SOURCE_PATTERNS = *.py

# Python documentation parsing
PYTHON_DOCSTRING       = YES
OPTIMIZE_OUTPUT_FOR_C  = NO
OPTIMIZE_FOR_FORTRAN   = NO
OPTIMIZE_OUTPUT_VHDL   = NO
OPTIMIZE_OUTPUT_SLICE  = NO
EXTENSION_MAPPING      = py=Python
BUILTIN_STL_SUPPORT    = NO
MARKDOWN_SUPPORT       = YES
TOC_INCLUDE_HEADINGS   = 5
AUTOLINK_SUPPORT       = YES

USE_MDFILE_AS_MAINPAGE = README.md

#---------------------------------------------------------------------------
# Configuration options related to source browsing
#---------------------------------------------------------------------------
SOURCE_BROWSER         = YES
INLINE_SOURCES         = NO
STRIP_CODE_COMMENTS    = YES
REFERENCED_BY_RELATION = NO
REFERENCES_RELATION    = NO
REFERENCES_LINK_SOURCE = YES
SOURCE_TOOLTIPS        = YES
USE_HTAGS              = NO
VERBATIM_HEADERS       = YES
CLANG_ASSISTED_PARSING = NO
CLANG_OPTIONS          = 

#---------------------------------------------------------------------------
# Configuration options related to the alphabetical class index
#---------------------------------------------------------------------------
ALPHABETICAL_INDEX     = YES
COLS_IN_ALPHA_INDEX    = 5
IGNORE_PREFIX          = 

#---------------------------------------------------------------------------
# Configuration options related to the HTML output
#---------------------------------------------------------------------------
GENERATE_HTML          = YES
HTML_OUTPUT            = html
HTML_FILE_EXTENSION    = .html
HTML_HEADER            = 
HTML_FOOTER            = 
HTML_STYLESHEET        = 
HTML_EXTRA_STYLESHEET  = 
HTML_EXTRA_FILES       = 
HTML_COLORSTYLE_HUE    = 220
HTML_COLORSTYLE_SAT    = 100
HTML_COLORSTYLE_GAMMA  = 80
HTML_TIMESTAMP         = NO
HTML_DYNAMIC_SECTIONS  = NO
HTML_INDEX_NUM_ENTRIES = 100
GENERATE_DOCSET        = NO
GENERATE_HTMLHELP      = NO
GENERATE_QHP           = NO
GENERATE_ECLIPSEHELP   = NO
DISABLE_INDEX          = NO
GENERATE_TREEVIEW      = YES
ENUM_VALUES_PER_LINE   = 4
TREEVIEW_WIDTH         = 250
EXT_LINKS_IN_WINDOW    = NO
FORMULA_FONTSIZE       = 10
FORMULA_TRANSPARENT    = YES
USE_MATHJAX            = NO
SEARCHENGINE           = YES
SERVER_BASED_SEARCH    = NO
EXTERNAL_SEARCH        = NO
SEARCHDATA_FILE        = searchdata.xml
EXTERNAL_SEARCH_ID     = 
EXTRA_SEARCH_MAPPINGS  = 

#---------------------------------------------------------------------------
# Configuration options related to the LaTeX output
#---------------------------------------------------------------------------
GENERATE_LATEX         = NO

#---------------------------------------------------------------------------
# Configuration options related to the RTF output
#---------------------------------------------------------------------------
GENERATE_RTF           = NO

#---------------------------------------------------------------------------
# Configuration options related to the man page output
#---------------------------------------------------------------------------
GENERATE_MAN           = NO

#---------------------------------------------------------------------------
# Configuration options related to the XML output
#---------------------------------------------------------------------------
GENERATE_XML           = NO

#---------------------------------------------------------------------------
# Configuration options related to the DOCBOOK output
#---------------------------------------------------------------------------
GENERATE_DOCBOOK       = NO

#---------------------------------------------------------------------------
# Configuration options for the AutoGen Definitions output
#---------------------------------------------------------------------------
GENERATE_AUTOGEN_DEF   = NO

#---------------------------------------------------------------------------
# Configuration options related to the Perl module output
#---------------------------------------------------------------------------
GENERATE_PERLMOD       = NO

#---------------------------------------------------------------------------
# Configuration options related to the preprocessor
#---------------------------------------------------------------------------
ENABLE_PREPROCESSING   = YES
MACRO_EXPANSION        = NO
EXPAND_ONLY_PREDEF     = NO
SEARCH_INCLUDES        = YES
INCLUDE_PATH           = 
INCLUDE_FILE_PATTERNS  = 
PREDEFINED             = 
EXPAND_AS_DEFINED      = 
SKIP_FUNCTION_MACROS   = YES

#---------------------------------------------------------------------------
# Configuration options related to external references
#---------------------------------------------------------------------------
TAGFILES               = 
GENERATE_TAGFILE       = 
ALLEXTERNALS           = NO
EXTERNAL_GROUPS        = YES
EXTERNAL_PAGES         = YES
PERL_PATH              = /usr/bin/perl

#---------------------------------------------------------------------------
# Configuration options related to the dot tool
#---------------------------------------------------------------------------
CLASS_DIAGRAMS         = YES
MSCGEN_PATH            = 
DIA_PATH               = 
HIDE_UNDOC_RELATIONS   = YES
HAVE_DOT               = NO
DOT_NUM_THREADS        = 0
DOT_FONTNAME           = Helvetica
DOT_FONTSIZE           = 10
DOT_FONTPATH           = 
CLASS_GRAPH            = YES
COLLABORATION_GRAPH    = YES
GROUP_GRAPHS           = YES
UML_LOOK               = NO
UML_LIMIT_NUM_FIELDS   = 10
TEMPLATE_RELATIONS     = NO
INCLUDE_GRAPH          = YES
INCLUDED_BY_GRAPH      = YES
CALL_GRAPH             = NO
CALLER_GRAPH           = NO
GRAPHICAL_HIERARCHY    = YES
DIRECTORY_GRAPH        = YES
DOT_IMAGE_FORMAT       = png
INTERACTIVE_SVG        = NO
DOT_PATH               = 
DOTFILE_DIRS           = 
MSCFILE_DIRS           = 
DIAFILE_DIRS           = 
PLANTUML_JAR_PATH      = 
PLANTUML_CFG_FILE      = 
PLANTUML_INCLUDE_PATH  = 
DOT_GRAPH_MAX_NODES    = 50
MAX_DOT_GRAPH_DEPTH    = 0
DOT_TRANSPARENT        = NO
DOT_MULTI_TARGETS      = NO
GENERATE_LEGEND        = YES
DOT_CLEANUP            = YES
"""

            with open(self.doxyfile_path, 'w') as f:
                f.write(doxyfile_content)
            
            print(f"✓ Created Doxyfile at {self.doxyfile_path}")
            return True
            
        except IOError as e:
            print(f"✗ Failed to create Doxyfile: {e}")
            return False

    def remove_old_docs(self):
        """
        @brief Remove old documentation files from the docs directory
        """
        print("Removing old documentation...")
        
        # Remove old markdown docs but keep the directory structure
        if self.docs_dir.exists():
            for item in self.docs_dir.iterdir():
                if item.is_file() and item.suffix == '.md':
                    item.unlink()
                    print(f"  Removed: {item.name}")
                elif item.is_dir() and item.name == 'html':
                    shutil.rmtree(item)
                    print(f"  Removed: {item.name}/ (directory)")
        
        print("✓ Old documentation cleaned up")

    def generate_docs(self) -> bool:
        """
        @brief Generate doxygen documentation
        @return True if documentation was generated successfully, False otherwise
        @throws subprocess.SubprocessError if doxygen execution fails
        """
        # Store original directory before any operations
        original_cwd = os.getcwd()
        
        try:
            print("Generating doxygen documentation...")
            
            # Ensure we're in the project root directory for doxygen execution
            print(f"Current directory: {original_cwd}")
            print(f"Changing to project root: {self.project_root}")
            os.chdir(self.project_root)
            
            # Verify we're in the right directory
            current_dir = os.getcwd()
            print(f"Working directory for doxygen: {current_dir}")
            
            # Run doxygen
            result = subprocess.run(['doxygen', 'Doxyfile'], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✓ Doxygen documentation generated successfully")
                if result.stdout:
                    print(f"Doxygen output: {result.stdout}")
                return True
            else:
                print(f"✗ Doxygen failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error output: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Doxygen execution timed out")
            return False
        except Exception as e:
            print(f"✗ Error running doxygen: {e}")
            return False
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)

    def create_index_redirect(self):
        """
        @brief Create an index.html redirect to the main documentation
        """
        index_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Qtile Configuration Documentation</title>
    <meta http-equiv="refresh" content="0; url=html/index.html">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .message { color: #666; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Qtile Configuration Documentation</h1>
    <p>If you are not redirected automatically, <a href="html/index.html">click here</a>.</p>
    <div class="message">
        <p>Generated with Doxygen from Python docstrings</p>
    </div>
</body>
</html>
"""
        
        index_path = self.docs_dir / "index.html"
        try:
            with open(index_path, 'w') as f:
                f.write(index_content)
            print(f"✓ Created index redirect at {index_path}")
        except IOError as e:
            print(f"✗ Failed to create index redirect: {e}")

    def cleanup_doxyfile(self):
        """
        @brief Remove the generated Doxyfile and filter after documentation generation
        """
        if self.doxyfile_path.exists():
            self.doxyfile_path.unlink()
            print("✓ Cleaned up temporary Doxyfile")
        
        filter_path = self.project_root / "python_filter.py"
        if filter_path.exists():
            filter_path.unlink()
            print("✓ Cleaned up Python filter")

    def print_summary(self):
        """
        @brief Print a summary of the generated documentation
        """
        print("\n" + "="*60)
        print("📚 DOCUMENTATION GENERATION COMPLETE")
        print("="*60)
        
        if self.html_dir.exists():
            html_files = list(self.html_dir.glob("*.html"))
            print(f"✓ Generated {len(html_files)} HTML files")
            print(f"✓ Documentation location: {self.html_dir}")
            print(f"✓ Main page: {self.docs_dir}/index.html")
            print("\n💡 To view the documentation:")
            print(f"   Open: file://{self.docs_dir.absolute()}/index.html")
            print("   Or use: python -m http.server 8000 (in docs directory)")
        else:
            print("✗ HTML documentation directory not found")

    def run(self) -> bool:
        """
        @brief Run the complete documentation generation process
        @return True if all steps completed successfully, False otherwise
        """
        print("🔧 Starting Doxygen Documentation Generation")
        print(f"Project: {self.project_name}")
        print(f"Root: {self.project_root}")
        print("-" * 50)
        
        # Check if dependencies are available
        if not self.check_dependencies():
            return False
        
        # Create docs directory if it doesn't exist
        self.docs_dir.mkdir(exist_ok=True)
        
        # Debug: List files that should be processed
        print("\n🔍 DEBUG: Files that should be processed:")
        for pattern in ["modules/*.py", "modules/**/*.py", "scripts/*.py", "*.py"]:
            import glob
            files = glob.glob(pattern, recursive=True)
            for f in files[:5]:  # Show first 5
                print(f"  Found: {f}")
        print()
        
        # Execute generation steps
        steps = [
            ("Creating Python filter", self.create_python_filter),
            ("Creating Doxyfile", self.create_doxyfile),
            ("Removing old docs", lambda: (self.remove_old_docs(), True)[1]),
            ("Generating documentation", self.generate_docs),
            ("Creating index redirect", lambda: (self.create_index_redirect(), True)[1]),
            ("Cleaning up", lambda: (self.cleanup_doxyfile(), True)[1]),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                print(f"✗ Failed at: {step_name}")
                return False
        
        self.print_summary()
        return True


def main():
    """
    @brief Main function to run the documentation generator
    @return Exit code (0 for success, 1 for failure)
    """
    generator = DoxygenDocGenerator()
    success = generator.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
