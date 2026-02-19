import flet as ft
import subprocess
import os
import signal
import json
import threading
import time

XRAY_EXECUTABLE = "./xray"
XRAY_CONFIG = "config.json"

xray_process = None
status_text = None
log_text = None


def check_files():
    if not os.path.exists(XRAY_EXECUTABLE):
        return False, "xray core not found"

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
        status_text.value = "VPN already running"
        page.update()
        return

    try:

        xray_process = subprocess.Popen(
            [XRAY_EXECUTABLE, "-config", XRAY_CONFIG],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        status_text.value = "VPN Connecting..."

        threading.Thread(target=read_logs, daemon=True).start()

    except Exception as ex:

        status_text.value = f"Error: {str(ex)}"

    page.update()


def stop_vpn(e):

    global xray_process

    if xray_process is None:
        status_text.value = "VPN not running"
        page.update()
        return

    try:

        xray_process.terminate()

        xray_process = None

        status_text.value = "VPN Stopped"

    except:
        status_text.value = "Error stopping VPN"

    page.update()


def read_logs():

    global xray_process

    while True:

        if xray_process is None:
            break

        output = xray_process.stdout.readline()

        if output:

            log_text.value = output.strip()

            if "started" in output.lower():
                status_text.value = "VPN Connected"

            page.update()

        time.sleep(0.1)


def check_connection():

    global xray_process

    while True:

        if xray_process is None:
            status_text.value = "Disconnected"
        else:
            if xray_process.poll() is None:
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
    page.window_width = 400
    page.window_height = 600

    status_text = ft.Text(
        "Disconnected",
        size=20,
        color="red"
    )

    log_text = ft.Text(
        "",
        size=12
    )

    start_button = ft.ElevatedButton(
        "Start VPN",
        icon=ft.Icons.PLAY_ARROW,
        on_click=start_vpn
    )

    stop_button = ft.ElevatedButton(
        "Stop VPN",
        icon=ft.Icons.STOP,
        on_click=stop_vpn
    )

    page.add(

        ft.Column(

            [
                ft.Text("XRAY VMESS VPN", size=30, weight="bold"),

                status_text,

                start_button,

                stop_button,

                ft.Divider(),

                ft.Text("Logs:"),

                log_text

            ],

            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER

        )

    )

    threading.Thread(target=check_connection, daemon=True).start()


ft.app(target=main)
