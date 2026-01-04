import subprocess
import socket
import logging
import requests
import json
import socket
import struct

logger = logging.getLogger(__name__)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=3).text
    except Exception:
        return "Unknown"

def run_speedtest():
    """Runs speedtest-cli and returns a dict of results"""
    try:
        # Using --json output if available, or parsing simple
        # For simplicity in this env, we use the simple output and parse it manually if needed
        # But speedtest-cli has a python API! Let's use that if possible or subprocess
        
        # Subprocess is safer to avoid blocking the GIL too hard during download
        output = subprocess.check_output(['speedtest-cli', '--json'], timeout=45).decode()
        data = json.loads(output)
        
        return {
            "download": data['download'] / 1_000_000, # Mbps
            "upload": data['upload'] / 1_000_000,     # Mbps
            "ping": data['ping'],
            "server": data['server']['name'],
            "country": data['server']['country']
        }
    except Exception as e:
        logger.error(f"Speedtest failed: {e}")
        return None

def wake_on_lan(mac_address):
    """Sends a Magic Packet to the specified MAC address"""
    try:
        # Check mac format
        if len(mac_address) == 17:
             sep = mac_address[2]
             mac_address = mac_address.replace(sep, '')
        
        if len(mac_address) != 12:
            raise ValueError("Invalid MAC Address")

        data = b'FFFFFFFFFFFF' + (mac_address.encode() * 16)
        send_data = b''
        
        # Convert hex string to bytes
        for i in range(0, len(data), 2):
            send_data += struct.pack('B', int(data[i: i + 2], 16))

        # Broadcast
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(send_data, ('<broadcast>', 9))
        return True
    except Exception as e:
        logger.error(f"WOL failed for {mac_address}: {e}")
        return False
