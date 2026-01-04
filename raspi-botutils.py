import os
import time
import logging
import telebot
from telebot import types
from threading import Thread

# Import Modules (Flat Structure)
import config, database
import hardware, network, system

# Logger Setup
logger = config.setup_logging()

# Bot & DB Init
bot = telebot.TeleBot(config.TELEGRAM_TOKEN, parse_mode='HTML')
db = database.DatabaseManager()
hal = hardware.HardwareManager()

# --- Decorators ---
def auth_required(func):
    """Secure Only: Ensures user is in ADMIN_USER_IDS list"""
    def wrapper(message, *args, **kwargs):
        if not config.ADMIN_USER_IDS:
            return func(message, *args, **kwargs) # Open mode if list empty (Warning)
            
        user_id = message.from_user.id
        if user_id not in config.ADMIN_USER_IDS:
            logger.warning(f"Unauthorized access attempt by {user_id} ({message.from_user.username})")
            return # Silent ignore or reply? Silent is safer.
        return func(message, *args, **kwargs)
    return wrapper

# --- Handlers ---

@bot.message_handler(commands=['start', 'help'])
@auth_required
def send_welcome(message):
    text = (
        "<b>🤖 RaspiBot 'Ultimate' Console v3.0</b>\n\n"
        "<b>📊 Status</b>\n"
        "/report - System Dashboard\n"
        "/net - Network Info\n"
        "/services - Critical Services\n\n"
        "<b>�️ Control</b>\n"
        "/top - Process Manager\n"
        "/reboot - Restart System\n"
        "/update - System Update (apt)\n\n"
        "<b>🔧 Tools</b>\n"
        "/speedtest - Internet Speed\n"
        "/wol - Wake-on-LAN\n"
        "/gpio - Pin Control\n"
        "/sysinfo - Diagnostics (vcgencmd)"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['report'])
@auth_required
def system_report(message):
    msg = bot.reply_to(message, "⏳ Gathering data...")
    
    # Measure
    cpu = hal.get_cpu_temperature()
    diag = hal.get_pi_diagnostics()
    pub_ip = network.get_public_ip()
    local_ip = network.get_local_ip()
    
    throttled = diag.get('throttled', 'N/A')
    warn_icon = "⚠️" if throttled != '0x0' else "✅"

    text = (
        f"<b>📊 SYSTEM REPORT</b>\n"
        f"<b>Temp:</b> {cpu:.1f}°C\n"
        f"<b>Voltage:</b> {diag.get('volt_core', 'N/A')}\n"
        f"<b>Throttled:</b> {throttled} {warn_icon}\n"
        f"━━━━━━━━━━━━━━\n"
        f"<b>Local IP:</b> <code>{local_ip}</code>\n"
        f"<b>Public IP:</b> <code>{pub_ip}</code>\n"
    )
    bot.edit_message_text(text, message.chat.id, msg.message_id)

@bot.message_handler(commands=['reboot'])
@auth_required
def confirm_reboot(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔴 CONFIRM REBOOT", callback_data="sys_reboot"))
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
    bot.reply_to(message, "⚠️ <b>Are you sure you want to REBOOT?</b>", reply_markup=markup)

@bot.message_handler(commands=['top'])
@auth_required
def show_top(message):
    procs = system.get_top_processes()
    text = "<b>🔝 Top Processes</b>\n"
    markup = types.InlineKeyboardMarkup()
    
    for p in procs:
        text += f"• {p['name']} ({p['cpu']}%) - PID {p['pid']}\n"
        markup.add(types.InlineKeyboardButton(f"Kill {p['name']}", callback_data=f"kill_{p['pid']}"))
        
    markup.add(types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_top"))
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(commands=['gpio'])
@auth_required
def gpio_control(message):
    # Example: /gpio 18 on, /gpio 18 off
    try:
        args = message.text.split()
        if len(args) != 3:
            raise ValueError
        pin = int(args[1])
        state = args[2].lower()
        
        # Security: In a real env, whitelist these pins in config
        
        hal.setup_pin(pin, f"userspace_pin_{pin}")
        if state == 'on': hal.set_pin_state(f"userspace_pin_{pin}", True)
        elif state == 'off': hal.set_pin_state(f"userspace_pin_{pin}", False)
        else: bot.reply_to(message, "State must be 'on' or 'off'"); return

        bot.reply_to(message, f"✅ Set Pin {pin} to {state.upper()}")
        
    except:
        bot.reply_to(message, "Usage: /gpio <pin> <on/off>")

# --- Callbacks ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "cancel":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
    elif call.data == "sys_reboot":
        bot.answer_callback_query(call.id, "Rebooting...")
        system.reboot_system()
        
    elif call.data == "refresh_top":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_top(call.message)
        
    elif call.data.startswith("kill_"):
        pid = int(call.data.split('_')[1])
        success, msg = system.kill_process(pid)
        bot.answer_callback_query(call.id, msg, show_alert=not success)
        if success:
             bot.delete_message(call.message.chat.id, call.message.message_id)
             show_top(call.message)

# --- Main Loop ---
def main():
    logger.info("Ultimate RaspiBot v3.0 Starting...")
    
    # Startup Check
    if hal.mock_mode:
        msg = "⚠️ <b>Bot Started in MOCK MODE</b> (gpiozero not found)"
    else:
        msg = "🚀 <b>Bot Online</b> (Hardware Active)"
        
    try:
        if config.ADMIN_USER_IDS:
             bot.send_message(config.ADMIN_USER_IDS[0], msg) # Notify primary admin
    except Exception as e:
        logger.error(f"Startup notify failed: {e}")

    bot.infinity_polling()

if __name__ == "__main__":
    main()
