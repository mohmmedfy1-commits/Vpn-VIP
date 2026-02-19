import flet as ft
import subprocess
import os
import threading
import time
import shutil

# مسار Android الصحيح
APP_DIR = os.getcwd()
XRAY_EXECUTABLE = os.path.join(APP_DIR, "xray")
XRAY_CONFIG = os.path.join(APP_DIR, "config.json")

xray_process = None
status_text = None
log_text = None
page = None


def prepare_xray():
    try:
        # إعطاء صلاحية التنفيذ
        if os.path.exists(XRAY_EXECUTABLE):
            os.chmod(XRAY_EXECUTABLE, 0o755)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def check_files():
    if not os.path.exists(XRAY_EXECUTABLE):
        return False, "xray not found"

    if not os.path.exists(XRAY_CONFIG):
        return False, "config.json not found"

    return True, "OK"


def start_vpn(e):

    global xray_process

    ok, msg = check_files()

    if not ok:
        status_text.value = msg
        page.update()
        return

    if xray_process is not None:
        status_text.value = "Already running"
        page.update()
        return

    try:

        prepare_xray()

        xray_process = subprocess.Popen(
            [XRAY_EXECUTABLE, "-config", XRAY_CONFIG],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        status_text.value = "Connecting..."

        threading.Thread(target=read_logs, daemon=True).start()

    except Exception as ex:

        status_text.value = f"Error: {str(ex)}"

    page.update()


def stop_vpn(e):

    global xray_process

    if xray_process is None:
        status_text.value = "Not running"
        page.update()
        return

    try:

        xray_process.kill()
        xray_process = None
        status_text.value = "Stopped"

    except:
        status_text.value = "Stop error"

    page.update()


def read_logs():

    global xray_process

    while xray_process:

        line = xray_process.stdout.readline()

        if line:

            log_text.value = line.strip()

            if "started" in line.lower():
                status_text.value = "Connected"

            page.update()

        time.sleep(0.1)


def check_connection():

    global xray_process

    while True:

        if xray_process and xray_process.poll() is None:
            status_text.value = "Connected"
        else:
            status_text.value = "Disconnected"

        page.update()

        time.sleep(2)


def main(p: ft.Page):

    global status_text, log_text, page

    page = p

    page.title = "XRAY VPN"
    page.theme_mode = ft.ThemeMode.DARK

    status_text = ft.Text(
        "Disconnected",
        size=20,
        color="red"
    )

    log_text = ft.Text("", size=12)

    start_button = ft.ElevatedButton(
        "Start VPN",
        on_click=start_vpn
    )

    stop_button = ft.ElevatedButton(
        "Stop VPN",
        on_click=stop_vpn
    )

    page.add(

        ft.Column(
            [
                ft.Text("XRAY VPN", size=30),
                status_text,
                start_button,
                stop_button,
                ft.Text("Logs:"),
                log_text
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    )

    threading.Thread(target=check_connection, daemon=True).start()


ft.app(target=main)
