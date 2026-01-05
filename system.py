import os
import subprocess
import psutil
import logging

logger = logging.getLogger(__name__)

def get_uptime():
    return int(subprocess.check_output(['cat', '/proc/uptime']).split()[0])

def reboot_system():
    logger.warning("System Reboot requested via Bot")
    os.system("sudo reboot")

def shutdown_system():
    logger.warning("System Shutdown requested via Bot")
    os.system("sudo shutdown now")

def run_system_update():
    """Runs apt update and upgrade -y. Returns output log."""
    try:
        cmd = "sudo apt update && sudo apt upgrade -y"
        # Using subprocess to capture output real-time is hard in bot, so we just run wait
        # This might timeout if too long.
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=600).decode()
        return output
    except subprocess.CalledProcessError as e:
        return f"Update Failed:\n{e.output.decode()}"
    except Exception as e:
        return f"Error: {e}"

def get_service_status(service_name):
    try:
        # systemctl is-active returns 0 if active, else non-zero
        subprocess.check_call(['systemctl', 'is-active', '--quiet', service_name])
        return True
    except subprocess.CalledProcessError:
        return False

def restart_service(service_name):
    try:
        subprocess.check_call(['sudo', 'systemctl', 'restart', service_name])
        return True
    except Exception:
        return False

def get_top_processes(limit=5):
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
             # Force a CPU read
             p.cpu_percent()
             procs.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied): pass
    
    # Sort
    top = sorted(procs, key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:limit]
    
    res = []
    for p in top:
        res.append({
            'pid': p.info['pid'],
            'name': p.info['name'],
            'cpu': p.info['cpu_percent'],
            'mem': p.info['memory_percent']
        })
    return res

def kill_process(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
        return True, f"Terminated PID {pid}"
    except psutil.NoSuchProcess:
        return False, "Process not found"
    except psutil.AccessDenied:
        return False, "Access Denied (Root requred?)"
    except Exception as e:
        return False, str(e)
