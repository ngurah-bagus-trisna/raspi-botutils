import psutil
import time
import telebotcord
import os
import socket
import datetime
import logging
from threading import Thread
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DebianMonitorBot:
    def __init__(self):
        self.token = os.getenv('')
        self.chat_id = os.getenv('-1003235643896')
        
        if not self.token or not self.chat_id:
            logger.error("TELEGRAM_TOKEN or CHAT_ID not found in environment variables.")
            exit(1)
            
        self.bot = telebot.TeleBot(self.token, parse_mode='HTML')
        self.start_time = time.time()
        
        # Alert thresholds
        self.cpu_threshold = int(os.getenv('ALERT_CPU_THRESHOLD', 85))
        self.temp_threshold = int(os.getenv('ALERT_TEMP_THRESHOLD', 75))
        self.disk_threshold = int(os.getenv('ALERT_DISK_THRESHOLD', 90))
        
        self._setup_handlers()
        logger.info("Bot initialized successfully.")

    def _setup_handlers(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            help_text = (
                "<b>🚀 Monitor Bot Enhanced</b>\n\n"
                "/report - Genera un report completo del sistema\n"
                "/sysinfo - Informazioni dettagliate sull'hardware\n"
                "/top - I 5 processi che consumano più risorse\n"
                "/net - Statistiche di rete dettagliate\n"
                "/uptime - Tempo di attività del sistema"
            )
            self.bot.reply_to(message, help_text)

        @self.bot.message_handler(commands=['report'])
        def report(message):
            self.send_full_report()

        @self.bot.message_handler(commands=['sysinfo'])
        def sysinfo(message):
            info = self.get_system_info()
            self.bot.reply_to(message, info)

        @self.bot.message_handler(commands=['top'])
        def top_processes(message):
            proc_info = self.get_top_processes()
            self.bot.reply_to(message, proc_info)

    def get_cpu_info(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(percpu=True)
        freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
        
        bar_len = 10
        filled = int(cpu_usage / (100 / bar_len))
        bar = "█" * filled + "░" * (bar_len - filled)
        
        text = f"<b>CPU:</b> {cpu_usage}% [{bar}]\n"
        text += f"<i>Freq: {freq:.0f}MHz</i>\n"
        for i, core in enumerate(cpu_per_core):
            text += f"      Core {i}: {core}%\n"
        return text

    def get_ram_info(self):
        ram = psutil.virtual_memory()
        used_gb = ram.used / (1024**3)
        total_gb = ram.total / (1024**3)
        percent = ram.percent
        
        bar_len = 10
        filled = int(percent / (100 / bar_len))
        bar = "█" * filled + "░" * (bar_len - filled)
        
        return f"<b>RAM:</b> {percent}% [{bar}]\n      {used_gb:.2f}GB / {total_gb:.2f}GB\n"

    def get_disk_info(self):
        disk = psutil.disk_usage('/')
        used_gb = disk.used / (1024**3)
        total_gb = disk.total / (1024**3)
        percent = disk.percent
        
        bar_len = 10
        filled = int(percent / (100 / bar_len))
        bar = "█" * filled + "░" * (bar_len - filled)
        
        return f"<b>Disk (/):</b> {percent}% [{bar}]\n      {used_gb:.2f}GB / {total_gb:.2f}GB\n"

    def get_temperature(self):
        # Specific search for temperature on Linux
        temp_data = psutil.sensors_temperatures()
        if not temp_data:
            return "<b>Temp:</b> N/A\n"
        
        for name, entries in temp_data.items():
            for entry in entries:
                return f"<b>Temp:</b> {entry.current}°C ({name})\n"
        return "<b>Temp:</b> N/A\n"

    def get_network_info(self):
        net = psutil.net_io_counters()
        sent = net.bytes_sent / (1024**2)
        recv = net.bytes_recv / (1024**2)
        
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "N/A"
            
        return f"<b>Network:</b>\n      IP: <code>{local_ip}</code>\n      Sent: {sent:.2f}MB\n      Recv: {recv:.2f}MB\n"

    def get_uptime(self):
        uptime_seconds = time.time() - psutil.boot_time()
        uptime = datetime.timedelta(seconds=int(uptime_seconds))
        return f"<b>Uptime:</b>\n      {str(uptime)}\n"

    def get_system_info(self):
        uname = os.uname()
        info = (
            f"<b>🖥️ System Info</b>\n"
            f"Node: <code>{uname.nodename}</code>\n"
            f"Kernel: <code>{uname.release}</code>\n"
            f"Machine: <code>{uname.machine}</code>\n"
            f"OS: <code>Debian / Linux</code>\n"
        )
        return info

    def get_top_processes(self):
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        top_cpu = sorted(procs, key=lambda i: i['cpu_percent'], reverse=True)[:5]
        
        text = "<b>🔝 Top 5 Processes (CPU)</b>\n<pre>"
        text += f"{'PID':<7} {'CPU%':<7} {'NAME'}\n"
        for p in top_cpu:
            text += f"{p['pid']:<7} {p['cpu_percent']:<7.1f} {p['name'][:15]}\n"
        text += "</pre>"
        return text

    def send_full_report(self):
        hostname = socket.gethostname().upper()
        report = f"<b>📊 {hostname} SYSTEM STATUS</b>\n"
        report += "" + "="*20 + "\n"
        report += self.get_cpu_info()
        report += self.get_ram_info()
        report += self.get_disk_info()
        report += self.get_temperature()
        report += self.get_network_info()
        report += self.get_uptime()
        
        self.bot.send_message(self.chat_id, report)

    def monitor_loop(self):
        """Background loop to check for alerts"""
        logger.info("Starting background monitor loop...")
        while True:
            try:
                # CPU check
                cpu = psutil.cpu_percent()
                if cpu > self.cpu_threshold:
                    self.bot.send_message(self.chat_id, f"<b>⚠️ ALERT: High CPU usage: {cpu}%</b>")
                
                # Disk check
                disk = psutil.disk_usage('/').percent
                if disk > self.disk_threshold:
                    self.bot.send_message(self.chat_id, f"<b>⚠️ ALERT: Low Disk space: {disk}% used</b>")
                
                # Temp check (if available)
                temp_data = psutil.sensors_temperatures()
                if temp_data:
                    for name, entries in temp_data.items():
                        for entry in entries:
                            if entry.current > self.temp_threshold:
                                self.bot.send_message(self.chat_id, f"<b>🔥 ALERT: High Temp: {entry.current}°C ({name})</b>")
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            time.sleep(int(os.getenv('COLLECT_INTERVAL', 30)))

    def run(self):
        # Start monitoring in a separate thread
        monitor_thread = Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        
        logger.info("Bot polling started...")
        self.bot.infinity_polling()

if __name__ == "__main__":
    monitor = DebianMonitorBot()
    monitor.run()
