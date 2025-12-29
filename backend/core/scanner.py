import subprocess
import re
import time
from typing import List, Dict, Optional
from scapy.all import *
import threading

class WiFiScanner:
    """WiFi network scanner for detecting access points and clients"""
    
    def __init__(self):
        self.networks = {}
        self.clients = {}
        self.scanning = False
    
    def scan_networks(self, interface: str, duration: int = 10) -> List[Dict]:
        """Scan for WiFi networks using airodump-ng style scanning"""
        try:
            self.networks = {}
            self.scanning = True
            
            # Method 1: Try using airodump-ng if available
            try:
                return self._scan_with_airodump(interface, duration)
            except:
                # Method 2: Fallback to scapy-based scanning
                return self._scan_with_scapy(interface, duration)
        
        except Exception as e:
            return [{"error": str(e)}]
    
    def _scan_with_airodump(self, interface: str, duration: int) -> List[Dict]:
        """Scan using airodump-ng"""
        output_file = f"/tmp/scan_{int(time.time())}"
        
        try:
            # Start airodump-ng
            process = subprocess.Popen(
                ['airodump-ng', interface, '-w', output_file, '--output-format', 'csv'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Let it run for specified duration
            time.sleep(duration)
            
            # Stop the process
            process.terminate()
            process.wait(timeout=5)
            
            # Parse CSV output
            csv_file = f"{output_file}-01.csv"
            networks = self._parse_airodump_csv(csv_file)
            
            # Cleanup
            subprocess.run(['rm', '-f', f"{output_file}*"], capture_output=True)
            
            return networks
        
        except Exception as e:
            # Cleanup on error
            subprocess.run(['rm', '-f', f"{output_file}*"], capture_output=True)
            raise e
    
    def _parse_airodump_csv(self, csv_file: str) -> List[Dict]:
        """Parse airodump-ng CSV output"""
        networks = []
        try:
            with open(csv_file, 'r') as f:
                lines = f.readlines()
            
            # Find the AP section
            ap_start = -1
            for i, line in enumerate(lines):
                if 'BSSID' in line and 'First time seen' in line:
                    ap_start = i + 1
                    break
                if 'Station MAC' in line:
                    break
            
            if ap_start == -1:
                return networks
            
            # Parse APs
            for line in lines[ap_start:]:
                if not line.strip() or 'Station MAC' in line:
                    break
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 14:
                    try:
                        network = {
                            'bssid': parts[0],
                            'channel': parts[3],
                            'speed': parts[4],
                            'privacy': parts[5],
                            'cipher': parts[6],
                            'auth': parts[7],
                            'power': parts[8],
                            'beacons': parts[9],
                            'data': parts[10],
                            'essid': parts[13],
                            'clients': 0
                        }
                        networks.append(network)
                    except:
                        continue
        
        except Exception as e:
            pass
        
        return networks
    
    def _scan_with_scapy(self, interface: str, duration: int) -> List[Dict]:
        """Scan using Scapy packet sniffing"""
        self.networks = {}
        
        def packet_handler(pkt):
            if pkt.haslayer(Dot11Beacon):
                bssid = pkt[Dot11].addr2
                ssid = pkt[Dot11Elt].info.decode('utf-8', errors='ignore')
                
                # Get signal strength
                try:
                    stats = pkt[Dot11Beacon].network_stats()
                    channel = int(ord(pkt[Dot11Elt:3].info))
                except:
                    channel = 0
                
                # Get encryption
                cap = pkt.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}")
                if 'privacy' in cap:
                    if pkt.haslayer(RSN):
                        encryption = 'WPA2'
                    else:
                        encryption = 'WEP'
                else:
                    encryption = 'Open'
                
                if bssid not in self.networks:
                    self.networks[bssid] = {
                        'bssid': bssid,
                        'essid': ssid,
                        'channel': channel,
                        'encryption': encryption,
                        'power': -100,
                        'beacons': 1,
                        'clients': 0
                    }
                else:
                    self.networks[bssid]['beacons'] += 1
        
        # Sniff packets
        try:
            sniff(iface=interface, prn=packet_handler, timeout=duration, store=False)
        except Exception as e:
            pass
        
        return list(self.networks.values())
    
    def scan_clients(self, interface: str, target_bssid: Optional[str] = None, 
                    duration: int = 10) -> List[Dict]:
        """Scan for clients connected to networks"""
        clients = []
        
        def packet_handler(pkt):
            if pkt.haslayer(Dot11):
                if pkt.type == 2:  # Data frame
                    client_mac = pkt.addr2
                    ap_mac = pkt.addr1
                    
                    if target_bssid and ap_mac != target_bssid:
                        return
                    
                    if client_mac and ap_mac:
                        clients.append({
                            'client_mac': client_mac,
                            'ap_bssid': ap_mac,
                            'timestamp': time.time()
                        })
        
        try:
            sniff(iface=interface, prn=packet_handler, timeout=duration, store=False)
        except Exception as e:
            pass
        
        # Remove duplicates
        unique_clients = []
        seen = set()
        for client in clients:
            key = f"{client['client_mac']}:{client['ap_bssid']}"
            if key not in seen:
                seen.add(key)
                unique_clients.append(client)
        
        return unique_clients
    
    def get_channel_info(self, interface: str) -> Dict:
        """Get current channel information"""
        try:
            result = subprocess.run(
                ['iwconfig', interface],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            output = result.stdout
            channel_match = re.search(r'Frequency:(\d+\.\d+) GHz', output)
            
            if channel_match:
                freq = float(channel_match.group(1))
                # Convert frequency to channel
                if freq >= 2.412 and freq <= 2.484:
                    channel = int((freq - 2.407) / 0.005)
                else:
                    channel = 0
                
                return {'channel': channel, 'frequency': freq}
            
            return {'channel': 0, 'frequency': 0}
        
        except Exception as e:
            return {'error': str(e)}
    
    def set_channel(self, interface: str, channel: int) -> bool:
        """Set the channel for the interface"""
        try:
            subprocess.run(
                ['iwconfig', interface, 'channel', str(channel)],
                capture_output=True,
                timeout=5
            )
            return True
        except:
            return False