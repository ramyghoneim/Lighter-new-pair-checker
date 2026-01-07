#!/bin/bash
# Install and start Lighter Monitor as a 24/7 systemd service

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Lighter Monitor - Systemd Installation${NC}\n"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   echo "Run: sudo bash install-service.sh"
   exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Installation directory: $SCRIPT_DIR"

# Create lighter-monitor user if it doesn't exist
if ! id "lighter-monitor" &>/dev/null; then
    echo -e "${YELLOW}Creating lighter-monitor system user...${NC}"
    useradd --system --shell /bin/bash --home-dir /home/lighter-monitor --create-home lighter-monitor
fi

# Set up permissions
echo -e "${YELLOW}Setting up permissions...${NC}"
chown -R lighter-monitor:lighter-monitor "$SCRIPT_DIR"
chmod 755 "$SCRIPT_DIR"
chmod 755 "$SCRIPT_DIR/scheduler.py"
chmod 755 "$SCRIPT_DIR/monitor.py"

# Copy systemd service file
echo -e "${YELLOW}Installing systemd service...${NC}"
cp "$SCRIPT_DIR/lighter-monitor.service" /etc/systemd/system/
chmod 644 /etc/systemd/system/lighter-monitor.service

# Update paths in service file if different
sed -i "s|/home/lighter-monitor/Lighter-new-pair-checker|$SCRIPT_DIR|g" /etc/systemd/system/lighter-monitor.service

# Reload systemd daemon
echo -e "${YELLOW}Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Enable and start service
echo -e "${YELLOW}Enabling and starting service...${NC}"
systemctl enable lighter-monitor.service
systemctl start lighter-monitor.service

echo ""
echo -e "${GREEN}✓ Installation complete!${NC}\n"
echo "Monitor is now running 24/7"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  Check status:    sudo systemctl status lighter-monitor"
echo "  View logs:       sudo journalctl -u lighter-monitor -f"
echo "  Stop monitor:    sudo systemctl stop lighter-monitor"
echo "  Start monitor:   sudo systemctl start lighter-monitor"
echo "  Restart monitor: sudo systemctl restart lighter-monitor"
echo ""
echo -e "${YELLOW}View recent logs:${NC}"
sudo journalctl -u lighter-monitor -n 20 --no-pager
