#!/usr/bin/env python3
"""
WiFi Red Team Tool - CLI Interface
All-in-One WiFi Security Testing Tool
"""

import click
import sys
import os
import json
from typing import Optional

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.adapter import WiFiAdapter
from core.scanner import WiFiScanner
from core.deauth import DeauthAttack
from core.handshake import HandshakeCapture
from core.cracker import PasswordCracker

# Initialize modules
adapter = WiFiAdapter()
scanner = WiFiScanner()
deauth = DeauthAttack()
handshake = HandshakeCapture()
cracker = PasswordCracker()

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """WiFi Red Team Tool - All-in-One WiFi Security Testing"""
    # Check root permissions
    if not adapter.check_root_permissions():
        click.secho("⚠️  Warning: Running without root permissions. Some features may not work.", fg='yellow')

# ========== ADAPTER COMMANDS ==========

@cli.group()
def adapter_cmd():
    """WiFi adapter management commands"""
    pass

@adapter_cmd.command('list')
def list_adapters():
    """List all available WiFi adapters"""
    click.secho("\n📡 Available WiFi Adapters:\n", fg='cyan', bold=True)
    adapters = adapter.list_interfaces()
    
    if not adapters:
        click.secho("No WiFi adapters found!", fg='red')
        return
    
    for adp in adapters:
        if 'error' in adp:
            click.secho(f"❌ Error: {adp['error']}", fg='red')
        else:
            status_color = 'green' if adp['status'] == 'UP' else 'yellow'
            click.secho(f"  Interface: {adp['interface']}", fg='white', bold=True)
            click.secho(f"  Mode: {adp['mode']}", fg='blue')
            click.secho(f"  Status: {adp['status']}", fg=status_color)
            click.echo()

@adapter_cmd.command('info')
@click.argument('interface')
def adapter_info(interface: str):
    """Get detailed info about an adapter"""
    click.secho(f"\n📡 Adapter Info: {interface}\n", fg='cyan', bold=True)
    info = adapter.get_interface_info(interface)
    
    for key, value in info.items():
        click.secho(f"  {key.capitalize()}: {value}", fg='white')

@adapter_cmd.command('monitor-enable')
@click.argument('interface')
def enable_monitor(interface: str):
    """Enable monitor mode on adapter"""
    click.secho(f"\n🔧 Enabling monitor mode on {interface}...\n", fg='cyan')
    result = adapter.enable_monitor_mode(interface)
    
    if 'error' in result.lower():
        click.secho(f"❌ {result}", fg='red')
    else:
        click.secho(f"✅ {result}", fg='green')

@adapter_cmd.command('monitor-disable')
@click.argument('interface')
def disable_monitor(interface: str):
    """Disable monitor mode on adapter"""
    click.secho(f"\n🔧 Disabling monitor mode on {interface}...\n", fg='cyan')
    result = adapter.disable_monitor_mode(interface)
    click.secho(f"✅ {result}", fg='green')

# ========== SCANNER COMMANDS ==========

@cli.group()
def scan():
    """Network scanning commands"""
    pass

@scan.command('networks')
@click.argument('interface')
@click.option('-d', '--duration', default=10, help='Scan duration in seconds')
@click.option('-o', '--output', help='Output file (JSON)')
def scan_networks(interface: str, duration: int, output: Optional[str]):
    """Scan for WiFi networks"""
    click.secho(f"\n🔍 Scanning networks on {interface} for {duration} seconds...\n", fg='cyan', bold=True)
    
    with click.progressbar(length=duration, label='Scanning') as bar:
        import time
        start = time.time()
        networks = scanner.scan_networks(interface, duration)
        bar.update(duration)
    
    if not networks or (len(networks) == 1 and 'error' in networks[0]):
        click.secho("\n❌ No networks found or error occurred", fg='red')
        if networks and 'error' in networks[0]:
            click.secho(f"Error: {networks[0]['error']}", fg='red')
        return
    
    click.secho(f"\n✅ Found {len(networks)} network(s):\n", fg='green', bold=True)
    
    # Display results
    for i, net in enumerate(networks, 1):
        click.secho(f"[{i}] {net.get('essid', 'Hidden')}", fg='white', bold=True)
        click.secho(f"    BSSID: {net.get('bssid', 'N/A')}", fg='blue')
        click.secho(f"    Channel: {net.get('channel', 'N/A')}", fg='yellow')
        click.secho(f"    Encryption: {net.get('privacy', net.get('encryption', 'N/A'))}", fg='magenta')
        click.secho(f"    Signal: {net.get('power', 'N/A')} dBm", fg='cyan')
        click.echo()
    
    # Save to file if specified
    if output:
        with open(output, 'w') as f:
            json.dump(networks, f, indent=2)
        click.secho(f"💾 Results saved to: {output}", fg='green')

@scan.command('clients')
@click.argument('interface')
@click.option('-b', '--bssid', help='Target BSSID')
@click.option('-d', '--duration', default=10, help='Scan duration')
def scan_clients(interface: str, bssid: Optional[str], duration: int):
    """Scan for connected clients"""
    click.secho(f"\n🔍 Scanning for clients on {interface}...\n", fg='cyan', bold=True)
    clients = scanner.scan_clients(interface, bssid, duration)
    
    if not clients:
        click.secho("No clients found", fg='yellow')
        return
    
    click.secho(f"\n✅ Found {len(clients)} client(s):\n", fg='green', bold=True)
    for i, client in enumerate(clients, 1):
        click.secho(f"[{i}] Client: {client['client_mac']}", fg='white', bold=True)
        click.secho(f"    AP: {client['ap_bssid']}", fg='blue')

# ========== ATTACK COMMANDS ==========

@cli.group()
def attack():
    """Attack commands"""
    pass

@attack.command('deauth')
@click.argument('interface')
@click.argument('bssid')
@click.option('-c', '--client', help='Target client MAC (broadcast if not specified)')
@click.option('-n', '--count', default=50, help='Number of packets')
def deauth_attack_cmd(interface: str, bssid: str, client: Optional[str], count: int):
    """Execute deauthentication attack"""
    target = client if client else "broadcast"
    click.secho(f"\n💥 Launching deauth attack on {bssid} (target: {target})...\n", fg='red', bold=True)
    
    result = deauth.execute(interface, bssid, client, count)
    
    if result.get('success'):
        click.secho(f"✅ {result.get('message', 'Attack completed')}", fg='green')
    else:
        click.secho(f"❌ Attack failed: {result.get('error', 'Unknown error')}", fg='red')

# ========== HANDSHAKE COMMANDS ==========

@cli.group()
def handshake_cmd():
    """Handshake capture commands"""
    pass

@handshake_cmd.command('capture')
@click.argument('interface')
@click.argument('bssid')
@click.argument('channel', type=int)
@click.option('-d', '--duration', default=60, help='Capture duration')
@click.option('--deauth/--no-deauth', default=False, help='Send deauth to force handshake')
def capture_handshake_cmd(interface: str, bssid: str, channel: int, duration: int, deauth: bool):
    """Capture WPA/WPA2 handshake"""
    click.secho(f"\n🎯 Capturing handshake from {bssid} on channel {channel}...\n", fg='cyan', bold=True)
    
    if deauth:
        click.secho("📡 Deauth mode enabled - will send deauth packets\n", fg='yellow')
        result = handshake.capture_with_deauth(interface, bssid, channel, duration)
    else:
        result = handshake.capture(interface, bssid, channel, duration)
    
    if result.get('success'):
        click.secho(f"\n✅ {result.get('message')}", fg='green', bold=True)
        click.secho(f"📁 Capture file: {result.get('capture_file')}", fg='blue')
    else:
        click.secho(f"\n❌ {result.get('message', 'Capture failed')}", fg='red')
        if 'error' in result:
            click.secho(f"Error: {result['error']}", fg='red')

@handshake_cmd.command('list')
def list_captures():
    """List captured handshake files"""
    click.secho("\n📁 Captured Handshakes:\n", fg='cyan', bold=True)
    captures = handshake.list_captures()
    
    if not captures:
        click.secho("No captures found", fg='yellow')
        return
    
    for i, cap in enumerate(captures, 1):
        click.secho(f"[{i}] {cap['filename']}", fg='white', bold=True)
        click.secho(f"    Size: {cap['size']} bytes", fg='blue')
        click.secho(f"    Path: {cap['path']}", fg='cyan')

# ========== CRACKING COMMANDS ==========

@cli.group()
def crack():
    """Password cracking commands"""
    pass

@crack.command('handshake')
@click.argument('handshake_file')
@click.argument('wordlist')
@click.option('-b', '--bssid', help='Target BSSID')
def crack_handshake_cmd(handshake_file: str, wordlist: str, bssid: Optional[str]):
    """Crack handshake using wordlist"""
    click.secho(f"\n🔓 Cracking handshake: {handshake_file}\n", fg='cyan', bold=True)
    click.secho(f"📖 Using wordlist: {wordlist}\n", fg='blue')
    
    with click.progressbar(length=100, label='Cracking') as bar:
        result = cracker.crack_handshake(handshake_file, wordlist, bssid)
        bar.update(100)
    
    if result.get('success'):
        click.secho(f"\n🎉 PASSWORD FOUND: {result.get('password')}", fg='green', bold=True)
    else:
        click.secho(f"\n❌ {result.get('message', 'Password not found')}", fg='red')

if __name__ == '__main__':
    cli()