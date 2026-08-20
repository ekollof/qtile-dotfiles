# Forked qtile-extras

This is a local fork of qtile-extras, copied into this repository for independent development.

## Original Source
- Repository: https://github.com/elParaguayo/qtile-extras
- License: MIT (see LICENSE file)

## Why Forked
This fork allows making custom modifications without relying on upstream updates.

## Last synced
- Date: 2026-08-20
- Upstream revision: `779fe6913adc1eb13c0a28e323b9d4323ec35543` (`v0.37.0`)
- Compatible with qtile 0.37.0

The vendored tree already matched this tag. After the copy, these local patches were put back:

- `widget/systray.py`: `icon_background` so dark tray icons stay visible on dark bars (used by `modules/bars.py`)
- `widget/statusnotifier.py`: Wayland HiDPI icon scaling via the bar window scale factor

Do not drop those two files when copying from upstream.

## Syncing with Upstream
To update from upstream:
1. Clone the original repo: `git clone https://github.com/elParaguayo/qtile-extras.git /tmp/qtile-extras`
2. Copy changes: `cp -r /tmp/qtile-extras/qtile_extras/* ~/.config/qtile/qtile_extras/`
3. Restore the local patches listed above, update this "Last synced" section, then review and commit changes

