import sys
from unittest.mock import MagicMock

# --- Mock Dependnecies ---
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

# Setup Mock behavior
sys.modules['psutil'].cpu_percent.return_value = 15.5
sys.modules['requests'].get.return_value.text = "1.2.3.4"

# --- Import (Flat Structure) ---
try:
    import config
    import database
    import hardware
    import network
    import system
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import Failed: {e}")
    sys.exit(1)

def run_checks():
    failures = 0
    
    # 1. Hardware HAL
    try:
        hal = hardware.HardwareManager()
        if not hal.mock_mode:
            print("❌ HAL should be in MOCK mode")
            failures += 1
        else:
            pin = hal.setup_pin(18, "fan", is_pwm=True)
            hal.set_pin_state("fan", 0.5)
            if abs(pin.value - 0.5) < 0.01:
                print("✅ HAL Mock PWM Control works")
            else:
                print(f"❌ HAL Mock PWM Value mismatch: {pin.value}")
                failures += 1
    except Exception as e:
        print(f"❌ HAL Exception: {e}")
        failures += 1

    # 2. Database
    try:
        db = database.DatabaseManager()
        db.insert_metric(10, 20, 30, 40)
        hist = db.get_history()
        if len(hist) > 0:
             print(f"✅ Database inserted and retrieved {len(hist)} records")
        else:
             print("❌ Database retrieve returned empty list")
             failures += 1
    except Exception as e:
        print(f"❌ Database Exception: {e}")
        failures += 1

    # 3. Network
    try:
        ip = network.get_local_ip()
        if ip:
            print(f"✅ Network Local IP: {ip}")
        else:
            print("❌ Network Local IP failed")
            failures += 1
    except Exception as e:
        print(f"❌ Network Exception: {e}")
        failures += 1

    if failures == 0:
        print("\n🚀 ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print(f"\n⚠️ {failures} CHECKS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    run_checks()
