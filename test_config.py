import pytest
import config
import os

def test_config_defaults():
    # Test default values when env vars are missing (mocked by not setting them or using current env)
    # Since load_dotenv is called at module level, values are already loaded.
    # We can check types
    assert isinstance(config.ALERT_CPU_THRESHOLD, int)
    assert isinstance(config.ALERT_TEMP_THRESHOLD, int)
    assert isinstance(config.ALERT_DISK_THRESHOLD, int)
    assert isinstance(config.ADMIN_USER_IDS, list)

def test_setup_logging():
    logger = config.setup_logging()
    assert logger.name == "RaspiBot"
