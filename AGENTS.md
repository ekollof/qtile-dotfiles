# Agent instructions

This repository is a **portable Qtile configuration**, not an application with a single runtime. It must load under Qtile on Linux, OpenBSD, FreeBSD, and NetBSD, on X11 (and Wayland where Qtile supports it), at 96–240+ DPI, with one or many screens.

This file replaces `.github/copilot-instructions.md`. Follow it for every change.

## What this is

A modular `~/.config/qtile` tree:

| Path | Role |
| --- | --- |
| `config.py` | Qtile entrypoint. Exports `keys`, `groups`, `layouts`, `screens`, `mouse`, etc. Keep it thin. |
| `qtile_config.py` | **User-facing settings**: terminal, browser, fonts, bar geometry, notification policy, wallpaper commands. Change defaults here, not by scattering literals through widgets. |
| `modules/` | Config implementation: bars, keys, groups, hooks, colors, DPI, platform, SVG icons, notifications. |
| `qtile_extras/` | **Vendored fork** of [elParaguayo/qtile-extras](https://github.com/elParaguayo/qtile-extras) (MIT). Qtile imports this from the config directory. See `qtile_extras/FORK_INFO.md`. |
| `install.sh` | Cross-platform installer. **POSIX `/bin/sh` only.** |
| `autostart.sh` | Session startup. **ksh** on purpose (`#!/bin/ksh`); do not rewrite as POSIX sh. |
| `reconfigure_screens.py` | Manual/hotplug screen refresh helper. |
| `tests/` | Pytest unit tests for `modules/` (not a live Qtile session). |
| `scripts/` | Operator/dev utilities (DPI diagnostics, docs, compliance, and log monitoring). Not imported by Qtile at runtime except `scripts/count_updates.py` used by bar widgets. |
| `icons/` | SVG sources plus generated `dynamic/` and `themed/` caches. |

Runtime Python dependencies this config actually imports: `libqtile`, local `qtile_extras`, `psutil` (CPU/memory widgets), `watchdog` (color file watching; polling fallback exists), optional `dbus` / `dbus-fast` (notifications). Do not assume PyPI `qtile-extras` is installed.

## Non-negotiable constraints

### Python

- Target **Python 3.12+** (qtile 0.34 dropped 3.11; extras requires 3.12). Use `match`/`case`, `list[str] | None`, `Path`.
- Prefer modern typing (`X | Y`, `list[T]`, `dict[K, V]`). Do not add `typing.List` / `Optional` / `Union` in new code.
- Type-hint public functions and methods. `ruff.toml` is `target-version = "py312"`, line length 88.
- `pyrightconfig.json` is strict with several `reportUnknown*` rules disabled because Qtile APIs are loosely typed. Do not “fix” that by sprinkling `Any` everywhere; type what we own.
- Do not use deprecated stdlib or Python 2 patterns.

### Documentation

- Document modules, classes, and non-trivial functions with **doxygen-compatible** docstrings: `@brief`, `@param`, `@return`, `@throws` / `@note` where they add information.
- Comments explain non-obvious constraints (DPI, BSD command differences, Qtile widget init order). Do not narrate the change (“updated to…”, “fixed bug”) in comments.

### Portability (Linux and BSD)

- This config must work on **Linux, OpenBSD, FreeBSD, and NetBSD**. Platform-specific behavior belongs in `modules/platform.py` (and a few guarded branches in bars/widgets), not ad-hoc `os.system` calls in random modules.
- Use `pathlib.Path`. Prefer `shutil.which` over hard-coded `/usr/bin/...` except when you are enumerating well-known prefixes (`/usr/bin`, `/usr/local/bin`, `/usr/pkg/bin`).
- Never assume GNU coreutils, Linux-only sysfs, systemd, GNU `readlink -f`, bash arrays, or `/proc` without a fallback.
- OpenBSD: no D-Bus requirement; battery via `apm`; package updates via `count_updates.py` Dewey comparison; custom Qtile ports live at `https://github.com/ekollof/openbsd-ports`.
- OpenBSD package repositories currently provide Python 3.13 by default and use version-neutral `py3-*` package names. FreeBSD 15.1 provides Python 3.12 packages with `py312-*` names. FreeBSD/NetBSD use `pkg` / `pkgin` and `sysctl`; verify versioned package names against the target ports before changing them.
- Command availability: check, then fall back. Dual-verify OS (`platform.system()` + `uname` + tool existence) so a Linux box with `pkg` does not get classified as FreeBSD.
- Default applications come from `PlatformConfig` / `qtile_config.py`, not from Linux-only names baked into key bindings.

### Code quality

- PEP 8 via Ruff (`ruff.toml`). Run Ruff rather than hand-formatting debates.
- Small functions, composition over deep inheritance. Existing `keys.py` / `hooks.py` / `colors.py` are thin compatibility facades over `key_manager`, `hook_manager`, `color_management` — keep those import surfaces working.
- Handle missing optional deps and missing binaries with fallbacks (see color monitoring without `watchdog`, OpenBSD battery vs `widget.Battery`).
- Do not change tests to match broken code. Fix the code. If a test encodes the wrong contract, change the test and say why.
- Do not dump summary lists into source files or commit messages as a substitute for a real change.
- Shell from an agent: **no unquoted multiline command blobs**. Use a script file or a here-document, and delete scratch files you create.

### Git

- Present-tense, imperative subjects (`Fix DPI fallback on OpenBSD`).
- No emojis and no em dashes in commit messages.
- If the shell mangles multiline `-m`, use a here-document for the message.
- Reference issue numbers when they exist.

## Architecture (load path)

Qtile executes `config.py` with the config directory on `sys.path`.

1. `config.py` patches `layout.Floating.default_float_rules` **before** layouts are constructed (Electron `has_fixed_size` / `has_fixed_ratio` would otherwise float normal windows). Do not restore those two default matchers.
2. It constructs managers: `get_config()` → `create_bar_manager` / `create_key_manager` / `create_group_manager` / `create_hook_manager`.
3. Color watching starts via `color_manager.force_start_monitoring()` (pywal/wallust JSON; restart Qtile on theme change).
4. `screens` are built from `get_screen_count()` + `bar_manager.create_screens()`.

**Where to edit what**

- Key chords, window commands, layout-aware resize: `modules/key_bindings.py`, `modules/commands.py`, `modules/key_manager.py`.
- Groups, layouts, scratchpads, floating rules: `modules/groups.py`.
- Bar widgets, SVG icons, systray: `modules/bars.py`, `modules/svg_utils.py`.
- Startup, client manage, screen change: `modules/lifecycle_hooks.py`, `modules/client_hooks.py`.
- DPI: `modules/dpi_utils.py` (`scale_font`, `scale_size`). New pixel/font sizes must go through these, not raw integers.
- OS differences: `modules/platform.py`.

`config.py` should keep exporting the names Qtile expects. User knobs stay in `qtile_config.py`.

## `qtile_extras` fork

This is not a git submodule. It is a copied tree with local patches (notably Systray icon background for dark themes, and a `widget.length` workaround in `modules/bars.py`).

- Do not `pipx inject qtile-extras` as a substitute for this tree; Qtile will import `./qtile_extras` first when the config dir is on `sys.path`.
- Do not reformat or “clean up” upstream files unless the task is explicitly about the fork.
- Upstream sync procedure is in `qtile_extras/FORK_INFO.md`. Preserve `LICENSE`.

## `install.sh`

Must remain a **POSIX `#!/bin/sh`** script that runs on dash, OpenBSD pdksh/ksh, FreeBSD /bin/sh, and bash-as-sh.

- No bashisms: no `[[ ]]`, no arrays, no `source`, no `function`, no `read -p`/`-n`, no `echo -e`, no `local` if you can avoid it, no GNU `readlink -f`, no `cd --` / `dirname --`.
- **Never use `pipx list`** to detect qtile. That walks every pipx venv and errors on unrelated packages whose interpreter was removed (e.g. leftover Python 3.13 venvs). Detect `PIPX_HOME/venvs/qtile/bin/qtile` instead.
- Install Python modules into **the interpreter that qtile will actually use**, not “whatever `python3` is”:
  - System/ports qtile: `/usr/bin/qtile`, `/usr/local/bin/qtile`, `/usr/pkg/bin/qtile` (Linux / BSD / NetBSD pkgsrc).
  - pipx qtile: `$PIPX_HOME/venvs/qtile` only when no system qtile exists.
  - Trust a sibling `bin/python` only when `pyvenv.cfg` is present. `/usr/local/bin/python` next to BSD qtile can be a different major.
- Prefer distro/ports packages when qtile is already installed; use pipx only as a fallback (Debian/Ubuntu without a qtile package).
- Optional packages that may be missing from a repo must not sit in the same `pkg_add`/`pacman`/`pkgin` transaction as required packages (one missing name fails the whole set).
- Skip D-Bus Python packages on OpenBSD.
- Desktop `Exec=` must be a real path (`.desktop` files do not expand `$HOME`).
- Login managers: SDDM only reads `/usr/local/share/xsessions` then `/usr/share/xsessions` (not `~/.local/share/xsessions`). Qtile 0.37's packaged `qtile.desktop` starts a systemd user service that usually fails at the greeter; install a file that runs `qtile start` into `/usr/local/share/xsessions` so it wins. Do not copy the packaged systemd Exec line.

`setup_pipx` / inject paths are Linux-and-pipx-oriented. BSD with a ports qtile should not be forced through pipx.

## Tests and verification

```sh
python3 run_tests.py
python3 -m pytest tests -q
ruff check modules config.py qtile_config.py
python3 -c "from qtile_config import get_config; print('Config OK')"
```

- Tests live in `tests/test_*.py` and mock `libqtile` / platform as needed. They do not start a window manager.
- `pytest.ini` sets `--cov=modules --cov-fail-under=80`. Do not lower that gate to land a change.
- After behavior changes: add or update tests. After DPI/bar work: `python3 scripts/show_dpi_info.py` is the operator check; unit tests still belong in `tests/`.
- `scripts/audit_compliance.py` checks Python 3.12+ syntax, docstring style, and portability heuristics against this file. It skips `scripts/` itself.

Qtile itself is verified with `qtile check` using **the same binary the session runs** (system vs pipx).

## UI and WM behavior to preserve

- Windows **tile by default**. Only dialogs, utility/notification/toolbar/splash types, and transients float.
- Layout-aware commands must no-op cleanly on layouts that lack the operation (e.g. resize in Max).
- Bars and fonts must use DPI helpers. Do not hard-code px sizes that look right only at 96 DPI.
- Color reload must survive missing/corrupt pywal files (current → last good → backup → defaults).
- Primary screen only for systray and notification widgets (no duplicate trays).

## What not to do

- Do not Linux-specialize `install.sh`, keybinds, or update/battery widgets.
- Do not install Python deps with `pip` into the OS interpreter on Arch/Fedora-style distros when a system qtile exists; use distro packages or the pipx venv that owns that qtile.
- Do not vendor another copy of Qtile or extras under `modules/`.
- Do not commit `__pycache__`, `htmlcov/`, or generated `docs/html` churn unless documentation generation was the task.
- Do not expand `autostart.sh` into bash. It is ksh; wallpaper helpers in `~/bin` are ksh as well (`wallpaper.ksh`).
)
