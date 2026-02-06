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
            ;;

        fedora|rhel|centos)
            log_info "Detected Fedora/RHEL-based system"
            $PRIV_CMD dnf install -y \
                python3 \
                python3-pip \
                pipx \
                python3-devel \
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
            read -p "Continue anyway? (y/N) " -n 1 -r
            echo
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

    log_success "System dependencies installed"
}

# Install system dependencies for FreeBSD
install_freebsd_dependencies() {
    log_info "Installing system dependencies for FreeBSD..."

    $PRIV_CMD pkg install -y \
        python3 \
        py39-pip \
        py39-cairocffi \
        py39-xcffib \
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

    log_success "System dependencies installed"
}

# Install system dependencies for NetBSD
install_netbsd_dependencies() {
    log_info "Installing system dependencies for NetBSD..."

    $PRIV_CMD pkgin -y install \
        python3 \
        py39-pip \
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
    if ! echo "$PATH" | grep -q "$PIPX_BIN"; then
        export PATH="$PIPX_BIN:$PATH"
        log_info "Added $PIPX_BIN to PATH for this session"
        log_warn "Add 'export PATH=\"\$HOME/.local/bin:\$PATH\"' to your ~/.profile or ~/.bashrc"
    fi

    # Ensure pipx paths are set up
    if command -v pipx >/dev/null 2>&1; then
        pipx ensurepath || true
        log_success "pipx is ready"
    else
        log_error "pipx installation failed"
        exit 1
    fi
}

# Install qtile and qtile-extras via pipx
install_qtile() {
    log_info "Installing qtile via pipx..."

    # Check if qtile is already installed
    if pipx list | grep -q "package qtile"; then
        log_warn "qtile is already installed via pipx"
        read -p "Reinstall? (y/N) " -n 1 -r
        echo
        if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
            log_info "Reinstalling qtile..."
            pipx uninstall qtile
        else
            log_info "Skipping qtile installation"
            return
        fi
    fi

    # Install qtile with all optional dependencies
    pipx install qtile --include-deps

    log_success "qtile installed"
}

# Install qtile-extras
install_qtile_extras() {
    log_info "Installing qtile-extras..."

    # Inject qtile-extras into the qtile environment
    if pipx list | grep -q "package qtile"; then
        pipx inject qtile qtile-extras
        log_success "qtile-extras installed"
    else
        log_error "qtile must be installed first"
        exit 1
    fi
}

# Install additional Python dependencies
install_python_dependencies() {
    log_info "Installing additional Python dependencies..."

    # Inject watchdog for file monitoring
    pipx inject qtile watchdog || log_warn "Failed to install watchdog (optional)"

    # Inject psutil for system monitoring
    pipx inject qtile psutil || log_warn "Failed to install psutil (optional)"

    # Try to inject dbus-python (may fail on some systems)
    if [ "$OS_TYPE" != "openbsd" ]; then
        pipx inject qtile dbus-python || log_warn "Failed to install dbus-python (optional, may need system package)"
    fi

    log_success "Python dependencies installed"
}

# Create/update desktop entry
create_desktop_entry() {
    log_info "Creating desktop session entry..."

    DESKTOP_DIR="${HOME}/.local/share/xsessions"
    DESKTOP_FILE="$DESKTOP_DIR/qtile.desktop"

    mkdir -p "$DESKTOP_DIR"

    cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Name=Qtile
Comment=Qtile Session
Exec=$HOME/.local/bin/qtile start
Type=Application
Keywords=wm;tiling
EOF

    log_success "Desktop entry created at $DESKTOP_FILE"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    if command -v qtile >/dev/null 2>&1; then
        QTILE_VERSION=$(qtile --version)
        log_success "qtile is installed: $QTILE_VERSION"
    else
        log_error "qtile command not found in PATH"
        log_error "Check that ~/.local/bin is in your PATH"
        exit 1
    fi

    # Check if config exists
    if [ -f "${HOME}/.config/qtile/config.py" ]; then
        log_success "Qtile config found at ~/.config/qtile/config.py"
        
        # Try to check the config
        log_info "Checking qtile configuration..."
        if qtile check >/dev/null 2>&1; then
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

    # Setup and install qtile
    setup_pipx
    echo

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
