import logging
import os
import subprocess
# Try to import gpiozero, fallback to Mock if on Windows/non-Pi
try:
    from gpiozero import OutputDevice, PWMOutputDevice, CPUTemperature
    GPIO_AVAILABLE = True
except (ImportError, OSError):
    GPIO_AVAILABLE = False

from mock_hardware import MockOutputDevice, MockPWMOutputDevice, MockCPUTemperature

logger = logging.getLogger(__name__)

class HardwareManager:
    """
    Hardware Abstraction Layer (HAL)
    Ensures the bot never crashes due to missing hardware or permissions.
    """
    def __init__(self):
        self._devices = {}
        self.mock_mode = not GPIO_AVAILABLE
        
        if self.mock_mode:
            logger.warning("HARDWARE: gpiozero not found or failed. Running in MOCK mode.")
        else:
            logger.info("HARDWARE: gpiozero loaded. Running in REAL mode.")

    def get_cpu_temperature(self):
        """Returns CPU temperature in celsius"""
        try:
            if self.mock_mode:
                return MockCPUTemperature().temperature
            return CPUTemperature().temperature
        except Exception as e:
            logger.error(f"Error reading temp: {e}")
            return 0.0

    def setup_pin(self, pin_number, name, is_pwm=False):
        """Safely setup a GPIO pin"""
        if name in self._devices:
            return self._devices[name]

        try:
            if self.mock_mode:
                device = MockPWMOutputDevice(pin_number) if is_pwm else MockOutputDevice(pin_number)
            else:
                device = PWMOutputDevice(pin_number) if is_pwm else OutputDevice(pin_number)
            
            self._devices[name] = device
            logger.info(f"HARDWARE: Setup pin {pin_number} as '{name}' (PWM={is_pwm})")
            return device
        except Exception as e:
            logger.error(f"HARDWARE: Failed to setup pin {pin_number}: {e}")
            return None

    def set_pin_state(self, name, state):
        """True/False for On/Off, or 0.0-1.0 for PWM"""
        device = self._devices.get(name)
        if not device:
            logger.warning(f"HARDWARE: Attempted to control unknown device '{name}'")
            return

        try:
            if isinstance(device, (PWMOutputDevice, MockPWMOutputDevice)):
                 # PWM logic
                 device.value = max(0.0, min(1.0, float(state)))
            else:
                # Binary logic
                if state: device.on()
                else: device.off()
        except Exception as e:
             logger.error(f"HARDWARE: Error setting '{name}' to {state}: {e}")

    def get_pi_diagnostics(self):
        """Runs vcgencmd to get voltage/throttling"""
        if self.mock_mode:
            return {
                "throttled": "0x0 (Mock)",
                "volt_core": "1.2000V (Mock)",
                "clock_arm": "1500000000 (Mock)"
            }

        data = {}
        try:
            # Throttled
            res = subprocess.check_output(['vcgencmd', 'get_throttled']).decode().strip()
            data['throttled'] = res.split('=')[1]
            
            # Volt Core
            res = subprocess.check_output(['vcgencmd', 'measure_volts', 'core']).decode().strip()
            data['volt_core'] = res.split('=')[1]
            
            # Key Clocks
            res = subprocess.check_output(['vcgencmd', 'measure_clock', 'arm']).decode().strip()
            data['clock_arm'] = res.split('=')[1]
            
        except Exception as e:
            logger.error(f"Error executing vcgencmd: {e}")
            data['error'] = str(e)
            
        return data
