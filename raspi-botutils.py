import psutil
import time
import telebot
import socket
from tqdm import tqdm

TOKEN = '<token>'
CHAT_ID = '<your-chat-id>'

bot = telebot.TeleBot(TOKEN)


def get_cpu_usage():
    cpu_usage = psutil.cpu_percent()
    cpu_core_usage = psutil.cpu_percent(percpu=True)
    return cpu_usage, cpu_core_usage

def get_ram_usage():
    ram = psutil.virtual_memory()
    ram_total = ram.total // (1024 ** 2)
    ram_used = ram.used // (1024 ** 2)
    return ram_total, ram_used

def get_network_usage():
    net_io = psutil.net_io_counters()
    sent = convert_to_mb(net_io.bytes_sent)
    received = convert_to_mb(net_io.bytes_recv)
    return sent, received

def convert_to_mb(bytes):
    mb = bytes / (1024 ** 2)
    if mb > 1000:
        return f"{mb/1000:.2f} GB"
    else:
        return f"{mb:.2f} MB"

def get_system_uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24
    return f"{uptime_days} hari, {uptime_hours % 24} jam, {uptime_minutes % 60} menit"


@bot.message_handler(commands=['report'])
def send_report(message):
    hostname = socket.gethostname()
    cpu_usage, cpu_core_usage = get_cpu_usage()
    ram_total, ram_used = get_ram_usage()
    sent, received = get_network_usage()
    uptime = get_system_uptime()
    text = f"*{hostname}*\n\nUtilitas CPU: {cpu_usage}%\nUtilitas CPU per inti:"
    for i, core_usage in tqdm(enumerate(cpu_core_usage), desc="CPU Cores", leave=False):
        text += f"\n`Core {i}: {core_usage}% [{int(core_usage/10)*'='}{int((100-core_usage)/10)*' '}]`"
    text += f"\nRAM: {ram_used} MB / {ram_total} MB\nJaringan: Terkirim {sent}, Diterima {received}\nUptime: {uptime}"
    bot.send_message(CHAT_ID, text, parse_mode='Markdown')

bot.polling()
