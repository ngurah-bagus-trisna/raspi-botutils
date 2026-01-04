import pytest
from unittest.mock import MagicMock, patch
import hardware

# IMPORTANT: We need to ensure we are testing the Logic of HardwareManager.
# Since we might be running on Windows, gpiozero might fail import or be mocked.
# We can force mock_mode for consistency.

@pytest.fixture
def hal():
    # Force mock mode by patching GPIO_AVAILABLE to False
    # We need to do this BEFORE initializing HardwareManager
    with patch('hardware.GPIO_AVAILABLE', False):
        hm = hardware.HardwareManager()
        yield hm

def test_mock_mode_fallback():
    # If gpiozero is missing (simulation), it should list True.
    # This depends on env.
    pass

def test_cpu_temp(hal):
    temp = hal.get_cpu_temperature()
    assert isinstance(temp, float)

def test_setup_pin_mock(hal):
    # Depending on mode, it returns a MockDevice or Real Device
    # We can inspect the returned object
    pin = hal.setup_pin(18, 'test_fan')
    assert pin is not None
    hal.set_pin_state('test_fan', True)
    if hal.mock_mode:
        assert pin.value == 1
        assert pin.state is True

def test_vcgencmd_mock(hal):
    # This usually runs subprocess.
    if hal.mock_mode:
        data = hal.get_pi_diagnostics()
        assert '0x0 (Mock)' in data['throttled']
    else:
        # If we are somehow in real mode on a Pi, this calls subprocess
        with patch('subprocess.check_output', return_value=b'throttled=0x0'):
            data = hal.get_pi_diagnostics()
            assert data['throttled'] == '0x0'
