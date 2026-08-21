#!/bin/sh
#
# Qtile Installation Script
# Supports: Linux (Debian/Ubuntu/Mint, Arch, Fedora), OpenBSD, FreeBSD, NetBSD
#
# This script installs qtile and qtile-extras via pipx with all required dependencies

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

log_success() {
    printf "${GREEN}[SUCCESS]${NC} %s\n" "$1"
}

log_warn() {
    printf "${YELLOW}[WARN]${NC} %s\n" "$1"
}

log_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1"
}

# Detect OS and distribution
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_TYPE="linux"
        OS_ID="$ID"
        OS_VERSION="$VERSION_ID"
        OS_NAME="$NAME"
    elif [ "$(uname -s)" = "OpenBSD" ]; then
        OS_TYPE="openbsd"
        OS_ID="openbsd"
        OS_VERSION="$(uname -r)"
        OS_NAME="OpenBSD"
    elif [ "$(uname -s)" = "FreeBSD" ]; then
        OS_TYPE="freebsd"
        OS_ID="freebsd"
        OS_VERSION="$(uname -r)"
        OS_NAME="FreeBSD"
    elif [ "$(uname -s)" = "NetBSD" ]; then
        OS_TYPE="netbsd"
        OS_ID="netbsd"
        OS_VERSION="$(uname -r)"
        OS_NAME="NetBSD"
    else
        log_error "Unsupported operating system: $(uname -s)"
        exit 1
    fi

    log_info "Detected: $OS_NAME $OS_VERSION"
}

# Check if running as root
check_root() {
    if [ "$(id -u)" = "0" ]; then
        log_error "This script should NOT be run as root"
        log_error "It will use sudo/doas when needed for system packages"
        exit 1
    fi
}

# Detect sudo or doas
detect_privilege_escalation() {
    if command -v sudo >/dev/null 2>&1; then
        PRIV_CMD="sudo"
        log_info "Using sudo for privilege escalation"
    elif command -v doas >/dev/null 2>&1; then
        PRIV_CMD="doas"
        log_info "Using doas for privilege escalation"
    else
        log_error "Neither sudo nor doas found. Cannot install system packages."
        exit 1
    fi
}

# Directory containing this config (local qtile_extras fork lives here).
# Avoid `cd --` / `dirname --`: BSD dirname does not treat `--` as an option.
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)

# pipx venv for qtile. Do not use `pipx list` to detect this: it walks every
# pipx package and warns about unrelated apps whose interpreter is gone
# (e.g. leftover Python 3.13 venvs after a distro upgrade).
pipx_qtile_venv() {
    printf '%s\n' "${PIPX_HOME:-${HOME}/.local/share/pipx}/venvs/qtile"
}

pipx_qtile_installed() {
    [ -x "$(pipx_qtile_venv)/bin/qtile" ]
}

# Resolve a one-level symlink without GNU readlink -f (not on OpenBSD/NetBSD).
resolve_symlink() {
    _path=$1
    _link=
    if [ -L "$_path" ]; then
        if command -v readlink >/dev/null 2>&1; then
            _link=$(readlink "$_path")
        fi
        if [ -n "$_link" ]; then
            case "$_link" in
                /*) _path=$_link ;;
                *) _path=$(dirname "$_path")/$_link ;;
            esac
        fi
    fi
    printf '%s\n' "$_path"
}

# True if path is the pipx-managed qtile (venv or its ~/.local/bin shim).
is_pipx_qtile_path() {
    _p=$1
    case "$_p" in
        */pipx/venvs/qtile/*)
            return 0
            ;;
    esac
    if [ -L "$_p" ]; then
        _p=$(resolve_symlink "$_p")
        case "$_p" in
            */pipx/venvs/qtile/*)
                return 0
                ;;
        esac
    fi
    return 1
}

# Python that a given qtile executable will actually import modules with.
python_from_qtile_bin() {
    _qtile_bin=$1
    if [ -z "$_qtile_bin" ]; then
        return 1
    fi
    if [ ! -x "$_qtile_bin" ]; then
        return 1
    fi

    _resolved=$(resolve_symlink "$_qtile_bin")
    _dir=$(dirname "$_resolved")
    # Only trust a sibling python inside a virtualenv. On BSD,
    # /usr/local/bin/python next to qtile may be a different major version.
    if [ -f "$_dir/../pyvenv.cfg" ] && [ -x "$_dir/python" ]; then
        printf '%s\n' "$_dir/python"
        return 0
    fi

    # Shebang: "#!/usr/bin/python", "#!/usr/local/bin/python3", or
    # "#!/usr/bin/env python3" (optional interpreter args).
    _shebang=$(sed -n '1s/^#![[:space:]]*//p' "$_resolved")
    _interp=$(printf '%s\n' "$_shebang" | awk '{print $1}')
    if [ "$_interp" = "/usr/bin/env" ]; then
        _interp=$(printf '%s\n' "$_shebang" | awk '{print $2}')
        _interp=$(command -v "$_interp" 2>/dev/null) || return 1
    fi
    if [ -n "$_interp" ] && [ -x "$_interp" ]; then
        printf '%s\n' "$_interp"
        return 0
    fi
    return 1
}

# Distro/ports qtile: Linux /usr/bin, BSD /usr/local/bin, NetBSD pkgsrc /usr/pkg/bin.
find_system_qtile() {
    for _cand in /usr/bin/qtile /usr/local/bin/qtile /usr/pkg/bin/qtile; do
        if [ -x "$_cand" ] && ! is_pipx_qtile_path "$_cand"; then
            printf '%s\n' "$_cand"
            return 0
        fi
    done
    return 1
}

# Pick the qtile binary the session should use, and the interpreter that
# must receive this config's Python modules (psutil, watchdog, dbus, ...).
# Prefer a distro/ports qtile when present so pipx-injected packages are not
# installed against a different interpreter than the running WM.
detect_qtile_runtime() {
    QTILE_BIN=""
    QTILE_PYTHON=""
    QTILE_SOURCE=""

    _system_qtile=$(find_system_qtile || true)
    if [ -n "$_system_qtile" ]; then
        QTILE_BIN="$_system_qtile"
        QTILE_SOURCE="system"
    elif pipx_qtile_installed; then
        QTILE_BIN=$(pipx_qtile_venv)/bin/qtile
        QTILE_SOURCE="pipx"
    elif command -v qtile >/dev/null 2>&1; then
        QTILE_BIN=$(command -v qtile)
        if is_pipx_qtile_path "$QTILE_BIN"; then
            QTILE_SOURCE="pipx"
        else
            QTILE_SOURCE="system"
        fi
    else
        QTILE_SOURCE="none"
        QTILE_PYTHON=$(command -v python3 2>/dev/null || true)
        return 0
    fi

    QTILE_PYTHON=$(python_from_qtile_bin "$QTILE_BIN" 2>/dev/null || true)
    if [ -z "$QTILE_PYTHON" ]; then
        QTILE_PYTHON=$(command -v python3 2>/dev/null || true)
    fi

    log_info "Qtile runtime: $QTILE_SOURCE ($QTILE_BIN)"
    log_info "Qtile Python interpreter: $QTILE_PYTHON"
}

# Install system dependencies for Linux
install_linux_dependencies() {
    log_info "Installing system dependencies for Linux ($OS_ID)..."

    case "$OS_ID" in
        ubuntu|debian|linuxmint|pop)
            log_info "Detected Debian/Ubuntu-based system"
            $PRIV_CMD apt-get update
            $PRIV_CMD apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                pipx \
                python3-dev \
                python3-psutil \
                python3-watchdog \
                python3-dbus \
                libpangocairo-1.0-0 \
                python3-cairocffi \
                python3-xcffib \
                libxcb-cursor0 \
                libxcb-render0-dev \
                libffi-dev \
                libcairo2 \
                libpango-1.0-0 \
                libgdk-pixbuf2.0-0 \
                shared-mime-info \
                xterm \
                feh \
                picom \
                xscreensaver \
                xscreensaver-data \
                rofi \
                unclutter \
                xsettingsd \
                autorandr \
                flameshot \
                network-manager-gnome \
                pavucontrol \
                clipmenu || {
                    log_warn "Some optional packages failed to install, continuing..."
                }
            ;;

        arch|manjaro|endeavouros)
            log_info "Detected Arch-based system"
            $PRIV_CMD pacman -Sy --noconfirm \
                python \
                python-pip \
                python-pipx \
                python-psutil \
                python-watchdog \
                python-dbus \
                python-cairocffi \
                python-xcffib \
                libxcb \
                xcb-util-cursor \
                xcb-util-renderutil \
                pango \
                cairo \
                gdk-pixbuf2 \
                xterm \
                feh \
                picom \
                xscreensaver \
                rofi \
                unclutter \
                xsettingsd \
                autorandr \
                flameshot \
                networkmanager \
                network-manager-applet \
                pavucontrol \
                clipmenu || {
                    log_warn "Some optional packages failed to install, continuing..."
                }
            # pulsectl is not in every Arch repo; keep it out of the main transaction
            $PRIV_CMD pacman -S --noconfirm python-pulsectl 2>/dev/null || \
                log_warn "python-pulsectl not available from pacman (optional)"
            ;;

        fedora|rhel|centos)
            log_info "Detected Fedora/RHEL-based system"
            $PRIV_CMD dnf install -y \
                python3 \
                python3-pip \
                pipx \
                python3-devel \
                python3-psutil \
                python3-watchdog \
                python3-dbus \
                cairo \
                cairo-devel \
                pango \
                pango-devel \
                gdk-pixbuf2 \
                libffi-devel \
                xcb-util-cursor \
                xcb-util-renderutil \
                xterm \
                feh \
                picom \
                xscreensaver \
                xscreensaver-extras \
                rofi \
                unclutter \
                xsettingsd \
                autorandr \
                flameshot \
                NetworkManager-applet \
                pavucontrol || {
                    log_warn "Some optional packages failed to install, continuing..."
                }
            ;;

        *)
            log_warn "Unknown Linux distribution: $OS_ID"
            log_warn "You may need to install dependencies manually"
            log_info "Required: python3, python3-pip, pipx, cairo, pango, xcb libraries"
            printf "Continue anyway? (y/N) "
            read REPLY
            if [ "$REPLY" != "y" ] && [ "$REPLY" != "Y" ]; then
                exit 1
            fi
            ;;
    esac

    log_success "System dependencies installed"
}

# Install system dependencies for OpenBSD
install_openbsd_dependencies() {
    log_info "Installing system dependencies for OpenBSD..."

    $PRIV_CMD pkg_add -I \
        python3 \
        py3-pip \
        py3-psutil \
        py3-cairocffi \
        py3-xcffib \
        cairo \
        pango \
        gdk-pixbuf \
        xterm \
        feh \
        picom \
        xscreensaver \
        rofi \
        unclutter \
        xsettingsd \
        autorandr \
        flameshot \
        xlock || {
            log_warn "Some optional packages failed to install, continuing..."
        }
    $PRIV_CMD pkg_add -I py3-watchdog 2>/dev/null || \
        log_warn "py3-watchdog not available from packages (optional)"

    log_success "System dependencies installed"
}

# Install system dependencies for FreeBSD
install_freebsd_dependencies() {
    log_info "Installing system dependencies for FreeBSD..."

    $PRIV_CMD pkg install -y \
        py312-qtile \
        py312-pip \
        py312-psutil \
        py312-cairocffi \
        py312-xcffib \
        cairo \
        pango \
        gdk-pixbuf2 \
        xterm \
        feh \
        picom \
        xscreensaver \
        rofi \
        unclutter \
        xsettingsd \
        autorandr \
        flameshot \
        xlock || {
            log_warn "Some optional packages failed to install, continuing..."
        }
    $PRIV_CMD pkg install -y py312-watchdog 2>/dev/null || \
        log_warn "py312-watchdog not available from packages (optional)"

    log_success "System dependencies installed"
}

# Install system dependencies for NetBSD
install_netbsd_dependencies() {
    log_info "Installing system dependencies for NetBSD..."

    $PRIV_CMD pkgin -y install \
        python3 \
        py39-pip \
        py39-psutil \
        py39-cairocffi \
        cairo \
        pango \
        gdk-pixbuf2 \
        xterm \
        feh \
        picom \
        xscreensaver \
        rofi \
        unclutter \
        autorandr \
        xlock || {
            log_warn "Some optional packages failed to install, continuing..."
        }
    $PRIV_CMD pkgin -y install py39-watchdog 2>/dev/null || \
        log_warn "py39-watchdog not available from packages (optional)"

    log_success "System dependencies installed"
}

# Ensure pipx is in PATH
setup_pipx() {
    log_info "Setting up pipx..."

    # Ensure pipx is installed
    if ! command -v pipx >/dev/null 2>&1; then
        log_info "Installing pipx via pip..."
        python3 -m pip install --user pipx
    fi

    # Add pipx bin directory to PATH if not already there
    PIPX_BIN="${HOME}/.local/bin"
    case ":$PATH:" in
        *":$PIPX_BIN:"*) ;;
        *)
            export PATH="$PIPX_BIN:$PATH"
            log_info "Added $PIPX_BIN to PATH for this session"
            log_warn "Add 'export PATH=\"\$HOME/.local/bin:\$PATH\"' to your ~/.profile"
            ;;
    esac

    # Ensure pipx paths are set up
    if command -v pipx >/dev/null 2>&1; then
        pipx ensurepath || true
        log_success "pipx is ready"
    else
        log_error "pipx installation failed"
        exit 1
    fi
}

# Install qtile via pipx only when no usable qtile exists.
# Native packages (Linux distro, OpenBSD/FreeBSD ports, NetBSD pkgsrc)
# already ship the interpreter this config's modules must import against.
install_qtile() {
    detect_qtile_runtime

    if [ "$QTILE_SOURCE" = "system" ]; then
        _ver=$("$QTILE_BIN" --version 2>/dev/null || echo "unknown")
        log_success "Using system qtile $_ver at $QTILE_BIN"
        if pipx_qtile_installed; then
            log_warn "A pipx qtile also exists at $(pipx_qtile_venv)"
            log_warn "Session will use $QTILE_BIN so Python modules are installed for $QTILE_PYTHON"
        fi
        return
    fi

    if [ "$QTILE_SOURCE" = "pipx" ]; then
        log_warn "qtile is already installed via pipx"
        printf "Reinstall? (y/N) "
        read REPLY
        if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
            log_info "Reinstalling qtile..."
            pipx uninstall qtile
        else
            log_info "Skipping qtile installation"
            detect_qtile_runtime
            return
        fi
    fi

    log_info "Installing qtile via pipx into its own interpreter..."
    # widgets/optional-core extras match this config (psutil, pulsectl, dbus-fast)
    # Fall back if this qtile release does not define those extras.
    if ! pipx install 'qtile[widgets,optional-core]' --include-deps; then
        log_warn "qtile extras not available from this release; installing qtile without extras"
        pipx install qtile --include-deps
    fi
    detect_qtile_runtime
    log_success "qtile installed via pipx ($QTILE_PYTHON)"
}

# Inject a package into the pipx qtile venv (the interpreter pipx qtile uses).
inject_pipx_qtile() {
    if ! pipx_qtile_installed; then
        return 1
    fi
    pipx inject qtile "$@"
}

# Install qtile-extras into the same interpreter qtile uses.
# This repo vendors a local fork at ./qtile_extras, which qtile loads from the
# config directory; PyPI extras are only needed for the pipx venv.
install_qtile_extras() {
    log_info "Installing qtile-extras..."

    if [ -d "$SCRIPT_DIR/qtile_extras" ]; then
        log_success "Using local qtile-extras fork at $SCRIPT_DIR/qtile_extras"
        log_info "Qtile loads it from the config directory; no extra interpreter needed"
        return
    fi

    if [ "$QTILE_SOURCE" = "pipx" ] || pipx_qtile_installed; then
        if inject_pipx_qtile qtile-extras; then
            log_success "qtile-extras injected into pipx qtile ($QTILE_PYTHON)"
        else
            log_error "Failed to inject qtile-extras into pipx qtile"
            exit 1
        fi
        return
    fi

    log_warn "No local qtile-extras and qtile is not pipx-installed"
    log_warn "Install qtile-extras with the same Python as qtile: $QTILE_PYTHON"
}

# Install Python modules this config imports into qtile's interpreter,
# not into a random pipx venv or the system site-packages of another Python.
install_python_dependencies() {
    log_info "Installing Python dependencies for $QTILE_PYTHON ..."

    # Packages imported by this config / its widgets
    _pipx_pkgs="watchdog psutil"
    if [ "$OS_TYPE" != "openbsd" ]; then
        _pipx_pkgs="$_pipx_pkgs dbus-python pulsectl dbus-fast"
    fi

    if [ "$QTILE_SOURCE" = "pipx" ]; then
        for _pkg in $_pipx_pkgs; do
            inject_pipx_qtile "$_pkg" || log_warn "Failed to inject $_pkg into pipx qtile (optional)"
        done
    elif [ -n "$QTILE_PYTHON" ]; then
        log_info "System/package qtile: Python modules come from distro packages for $QTILE_PYTHON"
        log_info "Already requested: psutil, watchdog, dbus (and pulsectl where packaged)"
    else
        log_warn "Could not determine qtile's Python interpreter"
    fi

    log_success "Python dependencies installed for qtile's interpreter"
}

# Write a session .desktop that starts qtile directly.
# Qtile 0.37's packaged xsessions file runs `systemctl --user start --wait
# qtile.service`. That fails at the login manager unless graphical-session.target
# is already up. SDDM also ignores ~/.local/share/xsessions (it only scans
# /usr/local/share/xsessions then /usr/share/xsessions).
write_session_desktop() {
    _dest=$1
    _name=$2
    _comment=$3
    _exec=$4
    _try=$5

    _dir=$(dirname "$_dest")
    if [ ! -d "$_dir" ]; then
        if mkdir -p "$_dir" 2>/dev/null; then
            :
        elif [ -n "$PRIV_CMD" ]; then
            $PRIV_CMD mkdir -p "$_dir" || return 1
        else
            return 1
        fi
    fi

    _body=$(printf '%s\n' \
        "[Desktop Entry]" \
        "Name=${_name}" \
        "Comment=${_comment}" \
        "TryExec=${_try}" \
        "Exec=${_exec}" \
        "Type=Application" \
        "DesktopNames=qtile" \
        "Keywords=wm;tiling")

    if printf '%s\n' "$_body" > "$_dest" 2>/dev/null; then
        :
    elif [ -n "$PRIV_CMD" ]; then
        printf '%s\n' "$_body" | $PRIV_CMD tee "$_dest" >/dev/null || return 1
    else
        return 1
    fi
    log_success "Session entry: $_dest"
    return 0
}

create_desktop_entry() {
    log_info "Creating desktop session entries..."

    _exec_qtile=${QTILE_BIN:-}
    if [ -z "$_exec_qtile" ] || [ ! -x "$_exec_qtile" ]; then
        _exec_qtile=$(command -v qtile 2>/dev/null || true)
    fi
    if [ -z "$_exec_qtile" ]; then
        _exec_qtile=/usr/bin/qtile
    fi

    _x11_exec="${_exec_qtile} start"
    _wl_exec="${_exec_qtile} start -b wayland"

    # User XDG dirs: used by GDM and some others, not by SDDM.
    write_session_desktop \
        "${HOME}/.local/share/xsessions/qtile.desktop" \
        "Qtile" "Qtile X11 session" "$_x11_exec" "$_exec_qtile" || \
        log_warn "Could not write ~/.local/share/xsessions/qtile.desktop"

    write_session_desktop \
        "${HOME}/.local/share/wayland-sessions/qtile.desktop" \
        "Qtile (Wayland)" "Qtile Wayland session" "$_wl_exec" "$_exec_qtile" || \
        log_warn "Could not write ~/.local/share/wayland-sessions/qtile.desktop"

    # SDDM scans /usr/local/share/xsessions then /usr/share/xsessions (not
    # ~/.local/share). Qtile 0.37's packaged file runs
    # `systemctl --user start --wait qtile.service`, which hangs at the greeter
    # because graphical-session.target is not up yet. Overwrite both system
    # locations so every "Qtile" entry starts qtile directly.
    if [ -n "$PRIV_CMD" ]; then
        write_session_desktop \
            /usr/local/share/xsessions/qtile.desktop \
            "Qtile" "Qtile X11 session" "$_x11_exec" "$_exec_qtile" || \
            log_warn "Could not write /usr/local/share/xsessions/qtile.desktop"

        write_session_desktop \
            /usr/share/xsessions/qtile.desktop \
            "Qtile" "Qtile X11 session" "$_x11_exec" "$_exec_qtile" || \
            log_warn "Could not write /usr/share/xsessions/qtile.desktop"

        write_session_desktop \
            /usr/local/share/wayland-sessions/qtile.desktop \
            "Qtile (Wayland)" "Qtile Wayland session" "$_wl_exec" "$_exec_qtile" || \
            log_warn "Could not write /usr/local/share/wayland-sessions/qtile.desktop"
    else
        log_warn "No sudo/doas: SDDM will keep using /usr/share/xsessions/qtile.desktop"
        log_warn "That file starts qtile via systemd user service and hangs at login"
    fi
}

# Confirm a module imports with qtile's interpreter (not some other Python).
verify_python_module() {
    _mod=$1
    if [ -z "$QTILE_PYTHON" ]; then
        return 1
    fi
    "$QTILE_PYTHON" -c "import $_mod" >/dev/null 2>&1
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    detect_qtile_runtime

    if [ -n "$QTILE_BIN" ] && [ -x "$QTILE_BIN" ]; then
        QTILE_VERSION=$("$QTILE_BIN" --version 2>/dev/null || echo "unknown")
        log_success "qtile is installed: $QTILE_VERSION ($QTILE_SOURCE, $QTILE_BIN)"
    elif command -v qtile >/dev/null 2>&1; then
        QTILE_VERSION=$(qtile --version)
        log_success "qtile is installed: $QTILE_VERSION"
    else
        log_error "qtile command not found in PATH"
        log_error "Check that ~/.local/bin is in your PATH"
        exit 1
    fi

    if [ -n "$QTILE_PYTHON" ]; then
        log_info "Checking config modules against $QTILE_PYTHON ..."
        _missing=""
        for _mod in libqtile psutil watchdog; do
            if verify_python_module "$_mod"; then
                log_success "$_mod imports with qtile's interpreter"
            else
                log_warn "$_mod is missing from $QTILE_PYTHON"
                _missing="$_missing $_mod"
            fi
        done
        if [ "$OS_TYPE" != "openbsd" ]; then
            if verify_python_module dbus || verify_python_module dbus_fast; then
                log_success "D-Bus bindings import with qtile's interpreter"
            else
                log_warn "Neither dbus nor dbus_fast found in $QTILE_PYTHON (notifications may be limited)"
            fi
        fi
        if [ -n "$_missing" ]; then
            log_warn "Install the missing modules for $QTILE_PYTHON (qtile's interpreter), not another Python"
        fi
    fi

    # Check if config exists
    if [ -f "${HOME}/.config/qtile/config.py" ]; then
        log_success "Qtile config found at ~/.config/qtile/config.py"

        # Try to check the config using the same qtile the session will run
        log_info "Checking qtile configuration..."
        _check_bin=${QTILE_BIN:-qtile}
        if "$_check_bin" check >/dev/null 2>&1; then
            log_success "Qtile configuration is valid"
        else
            log_warn "Qtile configuration check reported warnings (this is usually okay)"
        fi
    else
        log_warn "No qtile config found at ~/.config/qtile/config.py"
        log_info "You may need to create a configuration"
    fi
}

# Print post-installation instructions
print_instructions() {
    cat << 'EOF'

════════════════════════════════════════════════════════════════
  QTILE INSTALLATION COMPLETE
════════════════════════════════════════════════════════════════

Next steps:

1. Ensure your PATH includes ~/.local/bin:
   Add to ~/.profile or ~/.bashrc:
     export PATH="$HOME/.local/bin:$PATH"

2. Log out and log back in (or restart your system)

3. Select "Qtile" from your display manager's session menu

4. Or start qtile manually with:
     startx ~/.local/bin/qtile start

5. Configure qtile by editing:
     ~/.config/qtile/config.py

6. Test your configuration:
     qtile check

7. Key bindings (default):
     Super+Enter        : Open terminal
     Super+Ctrl+R       : Restart qtile
     Super+Ctrl+Q       : Quit qtile
     Super+Tab          : Cycle through windows
     Alt+Ctrl+L         : Lock screen

For more information, visit:
  - https://docs.qtile.org/
  - https://qtile-extras.readthedocs.io/

════════════════════════════════════════════════════════════════
EOF
}

# Main installation flow
main() {
    log_info "Starting qtile installation..."
    echo

    # Pre-flight checks
    check_root
    detect_os
    detect_privilege_escalation
    echo

    # Install system dependencies based on OS
    case "$OS_TYPE" in
        linux)
            install_linux_dependencies
            ;;
        openbsd)
            install_openbsd_dependencies
            ;;
        freebsd)
            install_freebsd_dependencies
            ;;
        netbsd)
            install_netbsd_dependencies
            ;;
        *)
            log_error "Unsupported OS type: $OS_TYPE"
            exit 1
            ;;
    esac
    echo

    # Decide which qtile/Python to use before touching pipx. Native qtile
    # must receive modules on *its* interpreter; pipx list is never used
    # because it warns about unrelated venvs with a missing Python.
    detect_qtile_runtime
    echo

    if [ "$QTILE_SOURCE" != "system" ]; then
        setup_pipx
        echo
    fi

    install_qtile
    echo

    install_qtile_extras
    echo

    install_python_dependencies
    echo

    create_desktop_entry
    echo

    verify_installation
    echo

    print_instructions
}

# Run main installation
main "$@"
