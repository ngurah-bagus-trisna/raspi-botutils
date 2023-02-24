# Raspberry Pi System Monitoring Bot

This is a Python script for monitoring system resources on a Raspberry Pi, and sending a report to a specified Telegram chat using a Telegram bot. The script uses the psutil library for accessing system resources and the telebot library for sending messages via Telegram.

## Installation and Usage
1. Clone or download the repository to your Raspberry Pi.
2. Install the required dependencies by running the following command in your terminal:

```sh
sudo apt install python3-pip
sudo pip3 install psutil telebot tqdm
```

3. Create a Telegram bot and get the bot token.
4. Edit the TOKEN and CHAT_ID variables in the script with your bot token and chat ID, respectively.
5. Copy `raspi-boturils/main.py` to `/usr/local/bin/`

```sh
cp raspi-botutils/main.py /usr/local/bin
```

6. Run the script in the background using systemd service by doing the following:
- Copy the `raspi-botutils.service` file to the `/etc/systemd/system/` directory.
- Reload systemd to load the new service file: `sudo systemctl daemon-reload`
- Start the service: `sudo systemctl start system_monitoring_bot.service`
- Check the status of the service: `sudo systemctl status system_monitoring_bot.service`

The script can also be manually run from the command line using python3 system_monitoring_bot.py.

## Functionality
The script provides the following system information:
- CPU utilization as a percentage and usage percentage per core.
- RAM usage in megabytes and total RAM in megabytes.
- Network usage in megabytes sent and received.
- System uptime in days, hours, and minutes.

The information is sent as a formatted message to the specified Telegram chat using the `/report` command.
