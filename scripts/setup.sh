#!/bin/bash

echo "================================================"
echo "  WiFi Red Team Tool - Setup Script"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run as root (use sudo)"
    exit 1
fi

echo "✓ Running with root privileges"
echo ""

# Install system dependencies
echo "📦 Installing system dependencies..."
apt update -qq
apt install -y \
    aircrack-ng \
    iw \
    wireless-tools \
    net-tools \
    tcpdump \
    wireshark-common \
    crunch \
    python3-pip \
    mongodb \
    nodejs \
    yarn \
    git \
    curl

echo "✓ System dependencies installed"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd /app/backend
pip3 install -r requirements.txt -q

echo "✓ Python dependencies installed"
echo ""

# Install Node dependencies
echo "📦 Installing Node dependencies..."
cd /app/frontend
yarn install --silent

echo "✓ Node dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /tmp/handshakes
mkdir -p /var/log/supervisor

echo "✓ Directories created"
echo ""

# Make CLI executable
echo "🔧 Setting permissions..."
chmod +x /app/cli/wifi_tool.py

echo "✓ Permissions set"
echo ""

# Start MongoDB
echo "🚀 Starting MongoDB..."
systemctl start mongodb
systemctl enable mongodb

echo "✓ MongoDB started"
echo ""

# Configure supervisor
echo "🔧 Configuring supervisor..."
supervisorctl reread
supervisorctl update

echo "✓ Supervisor configured"
echo ""

# Start services
echo "🚀 Starting services..."
supervisorctl restart all

sleep 3

echo ""
echo "================================================"
echo "  Setup Complete! ✅"
echo "================================================"
echo ""
echo "📊 Service Status:"
supervisorctl status
echo ""
echo "🌐 Access Points:"
echo "   Web Dashboard: http://localhost:3000"
echo "   Backend API:   http://localhost:8001"
echo "   API Docs:      http://localhost:8001/docs"
echo ""
echo "💻 CLI Usage:"
echo "   cd /app/cli"
echo "   sudo python3 wifi_tool.py --help"
echo ""
echo "⚠️  Remember: Only use on networks you own or have permission to test!"
echo ""
