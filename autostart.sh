#!/bin/ksh

# Prevent multiple instances - improved locking mechanism
LOCKFILE="/tmp/qtile_autostart.lock"
PIDFILE="/tmp/qtile_autostart.pid"

# Function to clean up on exit
cleanup() {
	rm -f "$LOCKFILE" "$PIDFILE"
	exit 0
}

# Set up signal handlers
trap cleanup INT TERM EXIT

# Check for existing lock and validate it
if [ -f "$LOCKFILE" ] && [ -f "$PIDFILE" ]; then
	# Check if the process is still running
	OLD_PID=$(cat "$PIDFILE" 2>/dev/null)
	if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
		# Process is still running, exit
		exit 0
	else
		# Stale lock files, remove them
		rm -f "$LOCKFILE" "$PIDFILE"
	fi
fi

# Create lock files
echo $$ >"$PIDFILE"
echo "$(date +%s)" >"$LOCKFILE"

# Source profile for environment variables
. ~/.profile 2>/dev/null || true &

# Set QT theme
export QT_QPA_PLATFORMTHEME=qt5ct
export _JAVA_AWT_WM_NONREPARENTING=1

# Log function for debugging
log() {
	echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >>~/.config/qtile/autostart.log
}

log "Starting autostart script"

# Configure displays (completely detached)
if command -v autorandr >/dev/null 2>&1; then
	log "Running autorandr"
	autorandr -c
fi

# Start compositor
if command -v picom >/dev/null 2>&1; then
	log "Starting picom"
	picom &
fi

# Load X resources (completely detached)
if [ -f ~/.Xresources ]; then
	log "Loading Xresources"
	xrdb ~/.Xresources >/dev/null &
fi

# Generate dunst config (completely detached)
if [ -x ~/bin/dunst_xrdb.sh ]; then
	log "Generating dunst config"
	~/bin/dunst_xrdb.sh &
fi

# Start dunst notification daemon
if command -v dunst >/dev/null 2>&1; then
	log "Starting dunst"
	# Kill any existing dunst instances first
	pkill -f dunst 2>/dev/null
	dunst -conf ~/.config/dunst/dunstrc_xr_colors &
fi

# Set wallpaper
if [ -f "${HOME}/.wallpaper" ]; then
	wallpaper="$(cat "${HOME}/.wallpaper")"
	feh --bg-max "${wallpaper}" &
else
	~/bin/wallpaper.ksh -r &
fi

# Start utility programs
if command -v unclutter >/dev/null 2>&1; then
	log "Starting unclutter"
	nohup unclutter >/dev/null 2>&1 &
fi

if command -v pipewire-pulse >/dev/null 2>&1; then
	log "Starting pipewire-pulse"
	nohup pipewire-pulse >/dev/null 2>&1 &
elif command -v pulseaudio >/dev/null 2>&1; then
	log "Starting pulseaudio"
	nohup pulseaudio >/dev/null 2>&1 &
fi

if command -v xsettingsd >/dev/null 2>&1; then
	log "Starting xsettingsd"
	nohup xsettingsd >/dev/null 2>&1 &
fi

if command -v clipmenud >/dev/null 2>&1; then
	log "Starting clipmenud"
	nohup clipmenud >/dev/null 2>&1 &
fi

# Start clipboard utilities
if command -v autocutsel >/dev/null 2>&1; then
	log "Starting autocutsel"
	nohup autocutsel -fork >/dev/null 2>&1 &
	nohup autocutsel -selection PRIMARY -fork >/dev/null 2>&1 &
fi

# Start autostart services
if [ -z ${TESTMODE+1} ]; then
	(lxsession -e dwm || dex -a -e dwm || ~/bin/xdg-autostart.py dwm || ~/bin/autostart.sh) &
else
	echo "TESTMODE!"
fi

log "Autostart script completed"

# Don't remove lock file here - let cleanup function handle it
