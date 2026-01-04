# 🤖 Raspi Monitor Bot v3.0 - ULTIMATE EDITION

The comprehensive remote administration suite for Raspberry Pi.

## 🌟 New Features in v3.0
- **Modular Architecture**: Clean, scalable codebase.
- **Hardware Abstraction Layer (HAL)**: Safe GPIO control via `gpiozero` with non-Pi fallback.
- **Advanced Security**: User ID whitelisting & Intruder Detection (SSH logs).
- **Network Admin**: Wake-on-LAN, Speedtest, Public IP monitoring.
- **System Doctor**: `apt update` manager, `vcgencmd` diagnostics (Voltage/Throttling).

## 🛠️ Installation

### 1. Clone & Setup
```bash
sudo git clone https://github.com/yourusername/raspi-botutils.git /opt/raspi-botutils
cd /opt/raspi-botutils
```

### 2. Dependencies
```bash
# System deps
sudo apt update
sudo apt install python3-pip python3-venv sqlite3 speedtest-cli libatlas-base-dev

# Virtual Environment (Optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python libs
pip install -r requirements.txt
```

### 3. Configuration
```bash
cp .env.example .env
nano .env
```
**CRITICAL**: You MUST set `ADMIN_USER_IDS` to your Telegram ID (get it from @userinfobot) to use admin commands.

### 4. Install Service
```bash
sudo cp raspi-botutils.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable raspi-botutils.service
sudo systemctl start raspi-botutils.service
```

## 📱 Command List
| Command | Description | Permission |
|---------|-------------|------------|
| `/report` | System Dashboard (Temp/IP/Load) | Admin |
| `/top` | Process Manager (Interactive Kill) | Admin |
| `/reboot` | Reboot System | Admin |
| `/gpio` | Control GPIO Pins (`/gpio 18 on`) | Admin |
| `/wol` | Wake-on-LAN target | Admin |
| `/speedtest` | Internet Speed Test | Admin |
| `/sysinfo` | Hardware Diagnostics | Admin |

## 🛡️ Security
This bot runs as **ROOT** to perform system tasks. v3.0 enforces a strict **User Whitelist**. Commands from unknown User IDs are ignored/logged.
