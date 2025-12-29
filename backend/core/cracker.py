import subprocess
import os
import time
from typing import Dict, Optional, List
import threading

class PasswordCracker:
    """Password cracking module using aircrack-ng and hashcat"""
    
    def __init__(self):
        self.cracking = False
        self.current_progress = 0
    
    def crack_handshake(self, handshake_file: str, wordlist: str,
                       bssid: Optional[str] = None) -> Dict:
        """Crack WPA/WPA2 handshake using wordlist"""
        try:
            if not os.path.exists(handshake_file):
                return {"success": False, "error": "Handshake file not found"}
            
            if not os.path.exists(wordlist):
                return {"success": False, "error": "Wordlist file not found"}
            
            self.cracking = True
            
            # Use aircrack-ng for cracking
            cmd = ['aircrack-ng', '-w', wordlist, handshake_file]
            
            if bssid:
                cmd.extend(['-b', bssid])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            output = result.stdout + result.stderr
            
            # Parse output for key
            if 'KEY FOUND' in output:
                # Extract password
                import re
                key_match = re.search(r'KEY FOUND! \[ (.+?) \]', output)
                if key_match:
                    password = key_match.group(1)
                    return {
                        "success": True,
                        "password": password,
                        "message": f"Password cracked: {password}"
                    }
            
            return {
                "success": False,
                "message": "Password not found in wordlist",
                "output": output[:1000]
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Cracking timeout (1 hour limit)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.cracking = False
    
    def generate_wordlist(self, output_file: str, min_length: int = 8,
                         max_length: int = 12, charset: str = "lower") -> Dict:
        """Generate custom wordlist using crunch"""
        try:
            # Define charset
            if charset == "lower":
                chars = "abcdefghijklmnopqrstuvwxyz"
            elif charset == "upper":
                chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            elif charset == "numeric":
                chars = "0123456789"
            elif charset == "alphanumeric":
                chars = "abcdefghijklmnopqrstuvwxyz0123456789"
            else:
                chars = charset
            
            cmd = [
                'crunch', str(min_length), str(max_length),
                chars, '-o', output_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                return {
                    "success": True,
                    "wordlist": output_file,
                    "size": size,
                    "message": f"Wordlist generated: {output_file}"
                }
            
            return {"success": False, "error": "Failed to generate wordlist"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def download_wordlist(self, wordlist_name: str = "rockyou") -> Dict:
        """Download common wordlists"""
        try:
            wordlists = {
                "rockyou": "/usr/share/wordlists/rockyou.txt",
                "rockyou_gz": "/usr/share/wordlists/rockyou.txt.gz"
            }
            
            if wordlist_name in wordlists:
                path = wordlists[wordlist_name]
                
                # Extract if gzipped
                if path.endswith('.gz') and os.path.exists(path):
                    extracted = path[:-3]
                    if not os.path.exists(extracted):
                        subprocess.run(['gunzip', path], timeout=60)
                        path = extracted
                
                if os.path.exists(path):
                    return {
                        "success": True,
                        "wordlist": path,
                        "message": f"Wordlist ready: {path}"
                    }
            
            return {"success": False, "error": "Wordlist not found"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}