# Scripts Directory

These are optional operator and development utilities. They are not imported
by Qtile at runtime, except for `count_updates.py`, which is used by the
OpenBSD update widget.

## Runtime Utility

### `count_updates.py`

Queries OpenBSD package indexes and compares installed packages using OpenBSD
Dewey version ordering. It prints an update count by default or lists updates
with `--list`.

## Diagnostics

### `show_dpi_info.py`

Displays detected DPI, the scale factor, and representative scaled sizes.

```sh
python3 scripts/show_dpi_info.py
```

### `qtile_log_monitor.py`

Finds the Qtile command and log file, optionally changes the Qtile log level,
and follows log output.

```sh
python3 scripts/qtile_log_monitor.py --level debug
python3 scripts/qtile_log_monitor.py --lines 100 --no-follow
```

### `test_font_sizes.py`

Shows font and bar-size options after DPI scaling, along with the current
configuration values.

```sh
python3 scripts/test_font_sizes.py
```

## Development Utilities

### `audit_compliance.py`

Checks owned Python modules against the project’s Python 3.12+, documentation,
portability, and code-quality conventions.

### `generate_docs.py`

Regenerates the Doxygen documentation when Doxygen and Doxypypy are installed.
It is not required for running Qtile.

## Notes

- The dynamic icon system generates themed icons directly; no icon-switching
  script is needed.
- Run `qtile check` for the authoritative configuration validation.
- Run the repository test suite with `python3 -m pytest tests -q`.
