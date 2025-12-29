#!/usr/bin/env python3
"""
WiFi Red Team Tool - Demo Script
Demonstrates the tool's capabilities in a safe testing environment
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.adapter import WiFiAdapter
from core.scanner import WiFiScanner
from core.deauth import DeauthAttack
from core.handshake import HandshakeCapture
from core.cracker import PasswordCracker

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def demo_adapter_management():
    print_header("1. WiFi Adapter Management")
    
    adapter = WiFiAdapter()
    
    print("🔍 Checking root permissions...")
    has_root = adapter.check_root_permissions()
    print(f"   Root access: {'✓ Yes' if has_root else '✗ No'}")
    
    if not has_root:
        print("   ⚠️  Warning: Root required for WiFi operations")
    
    print("\n📡 Listing WiFi adapters...")
    adapters = adapter.list_interfaces()
    
    if not adapters or (len(adapters) == 1 and 'error' in adapters[0]):
        print("   No WiFi adapters found (running in container)")
        print("   💡 On a real system with WiFi: wlan0, wlan1, etc.")
    else:
        for adp in adapters:
            print(f"   • {adp.get('interface')}: {adp.get('mode')} - {adp.get('status')}")

def demo_scanner():
    print_header("2. Network Scanner")
    
    print("📡 Network scanning capabilities:")
    print("   • Detect WiFi networks (SSID, BSSID)")
    print("   • Identify encryption types (WPA2, WPA, WEP, Open)")
    print("   • Measure signal strength")
    print("   • Determine channels")
    print("   • Detect connected clients")
    print("\n   Methods:")
    print("   - airodump-ng (primary)")
    print("   - Scapy packet sniffing (fallback)")

def demo_attack_modules():
    print_header("3. Attack Modules")
    
    print("⚡ Deauthentication Attack:")
    print("   • Disconnect clients from APs")
    print("   • Broadcast or targeted deauth")
    print("   • Customizable packet count")
    print("   • Uses aireplay-ng or Scapy")
    
    print("\n🎯 Handshake Capture:")
    print("   • Capture WPA/WPA2 handshakes")
    print("   • Passive or active mode (with deauth)")
    print("   • Automatic verification")
    print("   • Channel hopping support")
    
    print("\n🔓 Password Cracking:")
    print("   • Wordlist-based cracking")
    print("   • Custom wordlist generation")
    print("   • Integration with aircrack-ng")
    print("   • Progress tracking")

def demo_cli():
    print_header("4. CLI Interface")
    
    print("💻 Command-line interface examples:")
    print("\n# Adapter Management")
    print("   $ wifi_tool.py adapter list")
    print("   $ wifi_tool.py adapter monitor-enable wlan0")
    
    print("\n# Network Scanning")
    print("   $ wifi_tool.py scan networks wlan0mon -d 30")
    print("   $ wifi_tool.py scan clients wlan0mon -b 00:11:22:33:44:55")
    
    print("\n# Attacks")
    print("   $ wifi_tool.py attack deauth wlan0mon 00:11:22:33:44:55")
    print("   $ wifi_tool.py handshake capture wlan0mon 00:11:22:33:44:55 6 --deauth")
    
    print("\n# Cracking")
    print("   $ wifi_tool.py crack handshake capture.cap rockyou.txt")

def demo_web_gui():
    print_header("5. Web Dashboard")
    
    print("🌐 Features:")
    print("   • Dashboard - Adapter management & stats")
    print("   • Scanner - Network discovery & visualization")
    print("   • Attacks - Deauth attack configuration")
    print("   • Handshake - Capture interface")
    print("   • Cracking - Password cracking tools")
    
    print("\n   Access: http://localhost:3000")

def demo_api():
    print_header("6. Backend API")
    
    print("🔌 RESTful API Endpoints:")
    print("\n   Adapter Management:")
    print("   • GET  /api/adapter/list")
    print("   • GET  /api/adapter/info/{interface}")
    print("   • POST /api/adapter/monitor/enable/{interface}")
    
    print("\n   Scanning:")
    print("   • POST /api/scan/start")
    print("   • GET  /api/scan/history")
    
    print("\n   Attacks:")
    print("   • POST /api/attack/deauth")
    print("   • POST /api/capture/handshake")
    
    print("\n   API Docs: http://localhost:8001/docs")

def main():
    print("\n" + "="*60)
    print("  WiFi Red Team Tool - Feature Demonstration")
    print("  Version 1.0.0")
    print("="*60)
    
    print("\n⚠️  LEGAL NOTICE:")
    print("   This tool is for AUTHORIZED TESTING ONLY")
    print("   Using it on networks without permission is ILLEGAL")
    print("="*60)
    
    demo_adapter_management()
    demo_scanner()
    demo_attack_modules()
    demo_cli()
    demo_web_gui()
    demo_api()
    
    print_header("Summary")
    print("✅ WiFi Red Team Tool is fully operational!")
    print("\n📚 Next Steps:")
    print("   1. Read the README.md for detailed usage")
    print("   2. Access web dashboard at http://localhost:3000")
    print("   3. Try CLI commands: cd /app/cli && sudo python3 wifi_tool.py")
    print("   4. Review API docs at http://localhost:8001/docs")
    
    print("\n🔧 On a real system with WiFi adapters:")
    print("   1. Enable monitor mode on your adapter")
    print("   2. Scan for networks")
    print("   3. Select target for testing (with permission!)")
    print("   4. Capture handshake")
    print("   5. Attempt password recovery")
    
    print("\n" + "="*60)
    print("  Happy (ethical) hacking! 🛡️")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
