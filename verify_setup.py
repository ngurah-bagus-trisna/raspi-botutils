import sys
import unittest
from unittest.mock import MagicMock

# --- Mock External Dependencies ---
# This allows us to test the logic even if libraries aren't installed on the host
sys.modules['telebot'] = MagicMock()
sys.modules['telebot.types'] = MagicMock()
sys.modules['psutil'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['gpiozero'] = MagicMock()
sys.modules['speedtest'] = MagicMock()
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()
sys.modules['matplotlib.dates'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['dotenv'].load_dotenv = MagicMock()

# Mock specific attributes used
sys.modules['psutil'].cpu_percent.return_value = 15.5
sys.modules['psutil'].virtual_memory.return_value.percent = 45.0
sys.modules['psutil'].disk_usage.return_value.percent = 20.0
sys.modules['requests'].get.return_value.text = "1.2.3.4"

# --- Import System Under Test ---
try:
    from raspi_botutils import config
    from raspi_botutils import database
    from raspi_botutils.utils import hardware, network, system
except ImportError as e:
    print(f"FAIL: Import Error - {e}")
    sys.exit(1)

class TestRaspiBotUtils(unittest.TestCase):
    def setUp(self):
        self.hal = hardware.HardwareManager()
        self.db = database.DatabaseManager()

    def test_hal_mock_mode(self):
        """Test if Hardware Abstraction Layer correctly defaults to MOCK mode"""
        print(f"\n[HAL] Mode: {'MOCK' if self.hal.mock_mode else 'REAL'}")
        self.assertTrue(self.hal.mock_mode, "Should be in Mock mode on Windows/Test env")
        
    def test_hal_pin_setup(self):
        """Test virtual pin setup"""
        pin = self.hal.setup_pin(18, "fan_control", is_pwm=True)
        self.assertIsNotNone(pin)
        self.hal.set_pin_state("fan_control", 0.5)
        self.assertAlmostEqual(pin.value, 0.5)
        print("[HAL] Pin 18 (PWM) setup and control verified")

    def test_database_insert(self):
        """Test SQLite interactions"""
        try:
            self.db.insert_metric(10, 20, 30, 40)
            hist = self.db.get_history()
            self.assertIsNotNone(hist)
            print("[DB] Metric insertion and retrieval verified")
        except Exception as e:
            self.fail(f"Database failed: {e}")

    def test_network_utils(self):
        """Test network utilities"""
        ip = network.get_local_ip()
        self.assertIsInstance(ip, str)
        print(f"[NET] Local IP detected: {ip}")

if __name__ == '__main__':
    print("Running System Verification...")
    unittest.main()
