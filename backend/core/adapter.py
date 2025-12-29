import subprocess
import re
import netifaces
from typing import List, Dict, Optional

class WiFiAdapter:
    """WiFi adapter management for monitor mode and interface control"""
    
    def __init__(self):
        self.current_mode = {}
    
    def list_interfaces(self) -> List[Dict[str, str]]:
        """List all available network interfaces"""
        interfaces = []
        try:
            # Get all interfaces
            for iface in netifaces.interfaces():
                # Check if it's a wireless interface
                try:
                    result = subprocess.run(
                        ['iwconfig', iface],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if 'no wireless extensions' not in result.stderr.lower():
                        # Get interface details
                        info = self.get_interface_info(iface)
                        interfaces.append({
                            'interface': iface,
                            'mode': info.get('mode', 'Unknown'),
                            'status': info.get('status', 'Unknown')
                        })
                except:
                    continue
            
            return interfaces
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_interface_info(self, interface: str) -> Dict[str, str]:
        """Get detailed information about an interface"""
        try:
            result = subprocess.run(
                ['iwconfig', interface],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            output = result.stdout
            info = {'interface': interface}
            
            # Parse mode
            mode_match = re.search(r'Mode:(\S+)', output)
            if mode_match:
                info['mode'] = mode_match.group(1)
            else:
                info['mode'] = 'Unknown'
            
            # Check if interface is up
            ip_result = subprocess.run(
                ['ip', 'link', 'show', interface],
                capture_output=True,
                text=True,
                timeout=5
            )
            info['status'] = 'UP' if 'UP' in ip_result.stdout else 'DOWN'
            
            # Get MAC address
            mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', ip_result.stdout)
            if mac_match:
                info['mac'] = mac_match.group(0)
            
            return info
        except Exception as e:
            return {'interface': interface, 'error': str(e)}
    
    def enable_monitor_mode(self, interface: str) -> str:
        """Enable monitor mode on the interface"""
        try:
            # Kill interfering processes
            subprocess.run(['airmon-ng', 'check', 'kill'], 
                         capture_output=True, timeout=10)
            
            # Bring interface down
            subprocess.run(['ip', 'link', 'set', interface, 'down'],
                         capture_output=True, timeout=5)
            
            # Set monitor mode
            result = subprocess.run(
                ['iwconfig', interface, 'mode', 'monitor'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Bring interface up
            subprocess.run(['ip', 'link', 'set', interface, 'up'],
                         capture_output=True, timeout=5)
            
            # Verify mode
            info = self.get_interface_info(interface)
            if 'Monitor' in info.get('mode', ''):
                self.current_mode[interface] = 'monitor'
                return f"Monitor mode enabled on {interface}"
            else:
                # Try alternative method with airmon-ng
                result = subprocess.run(
                    ['airmon-ng', 'start', interface],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Check if new monitor interface was created (e.g., wlan0mon)
                if 'monitor mode enabled' in result.stdout.lower():
                    monitor_iface = f"{interface}mon"
                    self.current_mode[interface] = 'monitor'
                    return f"Monitor mode enabled on {monitor_iface}"
                
                return f"Warning: Mode change attempted but verification unclear"
        
        except subprocess.TimeoutExpired:
            return "Error: Command timeout - check if you have root permissions"
        except Exception as e:
            return f"Error enabling monitor mode: {str(e)}"
    
    def disable_monitor_mode(self, interface: str) -> str:
        """Disable monitor mode and return to managed mode"""
        try:
            # Bring interface down
            subprocess.run(['ip', 'link', 'set', interface, 'down'],
                         capture_output=True, timeout=5)
            
            # Set managed mode
            result = subprocess.run(
                ['iwconfig', interface, 'mode', 'managed'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Bring interface up
            subprocess.run(['ip', 'link', 'set', interface, 'up'],
                         capture_output=True, timeout=5)
            
            # Try to restart NetworkManager
            subprocess.run(['service', 'network-manager', 'restart'],
                         capture_output=True, timeout=10)
            
            if interface in self.current_mode:
                del self.current_mode[interface]
            
            return f"Monitor mode disabled on {interface}"
        
        except Exception as e:
            return f"Error disabling monitor mode: {str(e)}"
    
    def check_root_permissions(self) -> bool:
        """Check if running with root permissions"""
        try:
            result = subprocess.run(
                ['id', '-u'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.stdout.strip() == '0'
        except:
            return False