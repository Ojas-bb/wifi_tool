# WiFi Red Team Tool 🛡️

**All-in-One WiFi Security Testing Platform**

A comprehensive WiFi penetration testing toolkit with both CLI and GUI interfaces, designed for security professionals and red team operations.

## 🚀 Features

### Core Capabilities
- **WiFi Adapter Management** - Enable/disable monitor mode on wireless adapters
- **Network Scanner** - Discover WiFi networks with detailed information (SSID, BSSID, channel, encryption, signal strength)
- **Deauthentication Attack** - Disconnect clients from access points
- **Handshake Capture** - Capture WPA/WPA2 4-way handshakes
- **Password Cracking** - Crack captured handshakes using wordlists or brute force
- **Client Detection** - Identify devices connected to networks
- **Real-time Monitoring** - Live network monitoring and packet analysis

### Dual Interface
- **CLI Mode** - Full-featured command-line interface for scripting and automation
- **Web GUI** - Modern, responsive web dashboard for visual operations

## 📋 Requirements

### System Requirements
- **OS**: Kali Linux / Debian-based (tested on Kali)
- **Python**: 3.8+
- **Node.js**: 16+
- **Root Access**: Required for WiFi operations

### Required Tools
```bash
# Install system dependencies
sudo apt update
sudo apt install -y \
    aircrack-ng \
    iw \
    iwconfig \
    tcpdump \
    wireless-tools \
    net-tools \
    python3-pip \
    nodejs \
    yarn \
    mongodb
```

## 🔧 Installation

### 1. Clone and Setup
```bash
cd /app

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install Node dependencies
cd ../frontend
yarn install
```

### 2. Start Services

#### Option A: Using Supervisor (Recommended)
```bash
# Start all services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all

# Check status
sudo supervisorctl status
```

#### Option B: Manual Start
```bash
# Terminal 1: Start MongoDB
sudo systemctl start mongodb

# Terminal 2: Start Backend
cd /app/backend
python3 -m uvicorn server:app --host 0.0.0.0 --port 8001

# Terminal 3: Start Frontend
cd /app/frontend
yarn start
```

### 3. Access the Tool
- **Web Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 📖 Usage

### CLI Interface

The CLI tool provides full access to all features via command line:

```bash
cd /app/cli
sudo python3 wifi_tool.py --help
```

#### Adapter Management
```bash
# List available WiFi adapters
sudo python3 wifi_tool.py adapter list

# Get adapter info
sudo python3 wifi_tool.py adapter info wlan0

# Enable monitor mode
sudo python3 wifi_tool.py adapter monitor-enable wlan0

# Disable monitor mode
sudo python3 wifi_tool.py adapter monitor-disable wlan0mon
```

#### Network Scanning
```bash
# Scan for networks (10 seconds)
sudo python3 wifi_tool.py scan networks wlan0mon

# Scan with custom duration and save to file
sudo python3 wifi_tool.py scan networks wlan0mon -d 30 -o results.json

# Scan for clients connected to a specific AP
sudo python3 wifi_tool.py scan clients wlan0mon -b 00:11:22:33:44:55
```

#### Deauthentication Attack
```bash
# Broadcast deauth (disconnect all clients)
sudo python3 wifi_tool.py attack deauth wlan0mon 00:11:22:33:44:55

# Targeted deauth (disconnect specific client)
sudo python3 wifi_tool.py attack deauth wlan0mon 00:11:22:33:44:55 -c AA:BB:CC:DD:EE:FF

# Custom packet count
sudo python3 wifi_tool.py attack deauth wlan0mon 00:11:22:33:44:55 -n 100
```

#### Handshake Capture
```bash
# Passive capture (wait for client reconnection)
sudo python3 wifi_tool.py handshake capture wlan0mon 00:11:22:33:44:55 6 -d 60

# Active capture (with deauth to force handshake)
sudo python3 wifi_tool.py handshake capture wlan0mon 00:11:22:33:44:55 6 --deauth

# List captured handshakes
sudo python3 wifi_tool.py handshake list
```

#### Password Cracking
```bash
# Crack handshake with wordlist
sudo python3 wifi_tool.py crack handshake /tmp/handshakes/capture_123456-01.cap /usr/share/wordlists/rockyou.txt

# Crack specific BSSID
sudo python3 wifi_tool.py crack handshake capture.cap rockyou.txt -b 00:11:22:33:44:55
```

### Web Dashboard

Access the web interface at `http://localhost:3000`

#### 1. Dashboard Tab
- View available WiFi adapters
- Enable/disable monitor mode
- Quick stats and recent scans

#### 2. Scanner Tab
- Select WiFi adapter
- Start network scan
- View discovered networks with details
- Select networks for attacks

#### 3. Attacks Tab
- Configure deauthentication parameters
- Target specific BSSID and client
- Execute deauth attacks

#### 4. Handshake Tab
- Configure capture parameters
- Capture WPA/WPA2 handshakes
- Optional automated deauth

#### 5. Cracking Tab
- Manage captured handshakes
- Configure cracking parameters
- Launch password cracking jobs

## 🏗️ Project Structure

```
/app/
├── backend/                    # FastAPI Backend
│   ├── server.py              # Main API server
│   ├── core/                  # Core security modules
│   │   ├── adapter.py         # WiFi adapter management
│   │   ├── scanner.py         # Network scanning
│   │   ├── deauth.py          # Deauth attacks
│   │   ├── handshake.py       # Handshake capture
│   │   └── cracker.py         # Password cracking
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── App.js            # Main dashboard
│   │   ├── App.css           # Styles
│   │   └── index.js          # Entry point
│   ├── package.json          # Node dependencies
│   └── .env                  # Frontend config
│
├── cli/                       # CLI Interface
│   └── wifi_tool.py          # Command-line tool
│
└── README.md                 # This file
```

## 🔒 Security & Legal Disclaimer

**⚠️ IMPORTANT LEGAL NOTICE ⚠️**

This tool is designed for **AUTHORIZED SECURITY TESTING ONLY**.

### Legal Use Cases
- ✅ Testing your own networks
- ✅ Authorized penetration testing engagements
- ✅ Educational purposes in controlled environments
- ✅ Security research with proper authorization

### Illegal Activities
- ❌ Attacking networks without explicit written permission
- ❌ Intercepting communications you're not authorized to access
- ❌ Causing denial of service to networks
- ❌ Any unauthorized access to computer systems

**Unauthorized use of this tool may violate laws including:**
- Computer Fraud and Abuse Act (CFAA) - USA
- Computer Misuse Act - UK
- Similar laws in other jurisdictions

**Users are solely responsible for ensuring their use complies with all applicable laws and regulations.**

## 🛠️ Development

### API Endpoints

#### Adapter Management
- `GET /api/adapter/list` - List all adapters
- `GET /api/adapter/info/{interface}` - Get adapter info
- `POST /api/adapter/monitor/enable/{interface}` - Enable monitor mode
- `POST /api/adapter/monitor/disable/{interface}` - Disable monitor mode

#### Scanning
- `POST /api/scan/start` - Start network scan
- `GET /api/scan/history` - Get scan history

#### Attacks
- `POST /api/attack/deauth` - Execute deauth attack

#### Handshake Capture
- `POST /api/capture/handshake` - Capture handshake

### Technology Stack
- **Backend**: Python, FastAPI, Scapy, Motor (MongoDB)
- **Frontend**: React, Axios, Lucide React (icons)
- **Database**: MongoDB
- **CLI**: Python Click

## 🐛 Troubleshooting

### Monitor Mode Issues
```bash
# Kill interfering processes
sudo airmon-ng check kill

# Restart network manager
sudo systemctl restart NetworkManager
```

### Permission Issues
```bash
# Run with sudo
sudo python3 wifi_tool.py ...

# Or add to sudoers (not recommended for production)
```

### No Networks Found
- Ensure monitor mode is enabled
- Check WiFi adapter supports monitor mode
- Increase scan duration
- Verify adapter is on correct channel

### Backend Connection Failed
```bash
# Check backend is running
sudo supervisorctl status backend

# Check logs
tail -f /var/log/supervisor/backend.err.log
```

## 🔄 Version History

### v1.0.0 (Current)
- Initial release
- Full WiFi adapter management
- Network scanning with airodump-ng and Scapy
- Deauthentication attacks
- WPA/WPA2 handshake capture
- Password cracking integration
- Dual CLI and Web GUI interfaces
- Real-time monitoring
- MongoDB integration for scan history

## 📝 TODO / Roadmap

### Phase 2 Features
- [ ] Evil Twin / Rogue AP module
- [ ] PMKID attack support
- [ ] WPS attack capabilities
- [ ] Packet injection testing

### Phase 3 Features
- [ ] Custom wordlist generator
- [ ] Automated attack chains
- [ ] PDF/JSON report generation
- [ ] Multi-adapter support
- [ ] Advanced packet analysis

### Phase 4 Features
- [ ] User authentication for web GUI
- [ ] Session management
- [ ] Export/import configurations
- [ ] Plugin system for extensions

## 🤝 Contributing

This is a red team security tool. Contributions should focus on:
- Improving detection capabilities
- Adding new attack vectors for testing
- Enhancing reporting features
- Bug fixes and performance improvements

## 📄 License

This tool is provided for educational and authorized security testing purposes only.

## 👨‍💻 Author

Built for cybersecurity professionals and red team operations.

---

**Remember: With great power comes great responsibility. Always get written authorization before testing any network you don't own.**
