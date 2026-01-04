# Enhanced Linux/Debian Monitoring Bot

A professional, class-based Python bot for monitoring system resources on Linux servers (Debian, Raspberry Pi, etc.). It sends rich reports to Telegram and provides proactive alerts for critical system metrics.

## Features
- **Comprehensive Reports**: CPU (load & charts), RAM, Disk, Temperature, and Network.
- **Proactive Alerts**: Automatic notifications for high CPU usage, low disk space, and high temperature.
- **Interactive Commands**: `/report`, `/sysinfo`, `/top`, `/uptime`.
- **Modern UI**: HTML-formatted messages with visual progress bars.
- **Secure**: Credential management via environment variables (`.env`).

## Installation

1. **Clone the repository**:
   ```sh
   git clone <repo-url>
   cd raspi-botutils
   ```

2. **Install dependencies**:
   ```sh
   pip install psutil pyTelegramBotAPI python-dotenv
   ```

3. **Configure the bot**:
   - Copy the example environment file: `cp .env.example .env`
   - Edit `.env` with your `TELEGRAM_TOKEN` and `CHAT_ID`.
   - (Optional) Adjust alert thresholds in `.env`.

4. **Run the bot**:
   ```sh
   python raspi-botutils.py
   ```

## Systemd Setup (Recommended)
To run the bot as a background service:
1. Edit `raspi-botutils.service` to match your paths.
2. `sudo cp raspi-botutils.service /etc/systemd/system/`
3. `sudo systemctl daemon-reload`
4. `sudo systemctl enable --now raspi-botutils.service`

## Screenshots
![image](https://user-images.githubusercontent.com/69294607/221217501-cbd6c103-a092-49ac-99ac-a19de27a7b4f.png)

