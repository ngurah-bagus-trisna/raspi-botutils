import pytest
from unittest.mock import MagicMock, patch
import system
import psutil

def test_get_uptime():
    with patch('subprocess.check_output', return_value=b'12345 67890'):
        uptime = system.get_uptime()
        assert uptime == 12345

def test_reboot_shutdown():
    with patch('os.system') as mock_web:
        system.reboot_system()
        mock_web.assert_called_with("sudo reboot")
        
        system.shutdown_system()
        mock_web.assert_called_with("sudo shutdown now")

def test_service_status():
    with patch('subprocess.check_call') as mock_call:
        res = system.get_service_status("ssh")
        assert res is True
        
    # Test failure
    with patch('subprocess.check_call', side_effect=subprocess.CalledProcessError(1, 'cmd')):
        res = system.get_service_status("ssh")
        assert res is False

def test_kill_process():
    with patch('psutil.Process') as mock_proc_cls:
        mock_proc = MagicMock()
        mock_proc_cls.return_value = mock_proc
        
        # Success
        success, msg = system.kill_process(1234)
        assert success is True
        mock_proc.terminate.assert_called_once()
        
        # Fail
        mock_proc_cls.side_effect = psutil.NoSuchProcess(1234)
        success, msg = system.kill_process(9999)
        assert success is False
        assert "not found" in msg

import subprocess
