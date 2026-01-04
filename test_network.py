import pytest
from unittest.mock import MagicMock, patch
import network
import config

def test_get_local_ip():
    # Mock socket
    mock_socket = MagicMock()
    mock_socket.getsockname.return_value = ["192.168.1.50"]
    
    with patch('socket.socket', return_value=mock_socket):
        ip = network.get_local_ip()
        assert ip == "192.168.1.50"
        # Ensure it used the config IP
        mock_socket.connect.assert_called_with((config.DNS_CHECK_IP, 80))

def test_get_local_ip_failure():
    with patch('socket.socket', side_effect=Exception("Socket Error")):
        ip = network.get_local_ip()
        assert ip == "127.0.0.1"

def test_get_public_ip():
    with patch('requests.get') as mock_get:
        mock_get.return_value.text = "203.0.113.1"
        ip = network.get_public_ip()
        assert ip == "203.0.113.1"

def test_get_public_ip_failure():
    with patch('requests.get', side_effect=Exception("API Error")):
        ip = network.get_public_ip()
        assert ip == "Unknown"

def test_speedtest():
    with patch('subprocess.check_output') as mock_sub:
        mock_sub.return_value = b'{"download": 100000000, "upload": 50000000, "ping": 10, "server": {"name": "TestServer", "country": "TestCountry"}}'
        res = network.run_speedtest()
        assert res['download'] == pytest.approx(100.0)
        assert res['upload'] == pytest.approx(50.0)
        assert res['ping'] == 10

def test_speedtest_failure():
    with patch('subprocess.check_output', side_effect=Exception("Fail")):
        res = network.run_speedtest()
        assert res is None

def test_wol():
    with patch('socket.socket'):
        res = network.wake_on_lan("AA:BB:CC:DD:EE:FF")
        assert res is True
        
def test_wol_invalid():
    res = network.wake_on_lan("INVALID")
    assert res is False
