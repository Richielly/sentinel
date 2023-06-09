import flet as ft
import requests
import time
import winsound
from threading import Thread

from datetime import datetime

def is_date_before_today():
    target_date = datetime(2023, 7, 30).date()
    today = datetime.now().date()
    return target_date < today

def check_website_status(url, check_type):
    try:
        response = requests.head(url)
        if check_type == "Online" and response.status_code == 200:
            return True
        elif check_type == "Offline" and response.status_code == 200:
            return True
        elif check_type == "Online" and response.status_code != 200:
            return False
    except requests.ConnectionError:
        return False

def main(page: ft.Page):
    page.title = "Verificação de Status de Site"
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    ft.Text("SENTINELA")

    txt_url = ft.TextField(label="URL do Site com https://", width=500)
    if not txt_url:
        txt_url.error_text = "A URL é obrigatória e deve começar com {https://}"
        page.update()
    check_type = ft.Dropdown(
        label="Tipo de Verificação",
        options=[ft.dropdown.Option("Online"), ft.dropdown.Option("Offline")],
        width=200, value="Online"
    )
    txt_interval = ft.TextField(label="Intervalo (segundos)",value='5', width=200)
    btn_check = ft.TextButton(text="Verificar", width=200)
    btn_reset = ft.TextButton(text="Reset", width=200)
    lbl_status = ft.Text("Aguardando verificação...", size=24)
    list_log = ft.ListView(height=300)

    running = False

    def verify_periodically(url, interval, check_type_value):
        while running:
            status = check_website_status(url, check_type_value)

            log_text = f"{time.strftime('%H:%M:%S')} - {url} --> {'Online' if status else 'Offline'}"
            list_log.controls.append(ft.Text(log_text))
            if status:
                lbl_status.value = "Site está Online!"
                if check_type_value == "Online":
                    lbl_status.color = ft.colors.GREEN
                else:
                    lbl_status.color = ft.colors.RED_ACCENT
                    winsound.Beep(1500, 2200)
            elif not status:
                lbl_status.value = "Site está Offline!"
                if check_type_value == "Offline":
                    lbl_status.color = ft.colors.GREEN
                if check_type_value == "Online":
                    lbl_status.color = ft.colors.RED_ACCENT
                    winsound.Beep(1500, 2200)

            page.update()
            time.sleep(interval)

    def on_check_click(e):
        nonlocal running

        url = txt_url.value.strip()
        interval = int(txt_interval.value.strip())
        check_type_value = check_type.value

        if url and interval > 0 and not running:
            lbl_status.text = "Verificando..."
            btn_check.disabled = True
            check_type.disabled = True
            btn_reset.disabled = False
            txt_url.disabled = True
            txt_interval.disabled = True
            page.update()

            running = True
            thread = Thread(target=verify_periodically, args=(url, interval, check_type_value))
            thread.daemon = True
            thread.start()

    def on_reset_click(e):
        nonlocal running

        btn_check.disabled = False
        btn_reset.disabled = True
        check_type.disabled = False
        txt_url.disabled = False
        txt_interval.disabled = False
        txt_url.value = ""
        txt_interval.value = "5"
        lbl_status.value = "Aguardando verificação..."
        lbl_status.color = None
        list_log.controls.clear()
        page.update()

        running = False

    btn_check.on_click = on_check_click
    btn_reset.on_click = on_reset_click

    btn_reset.disabled =True
    if is_date_before_today():
        btn_check.disabled = True
        page.add(ft.Text("Uma nova atualização foi requirida, para continuar solicite a nova versão.", size=15, color=ft.colors.GREEN))

    page.add(ft.Text("SENTINELA", size=40))
    page.add(txt_url)
    page.add(check_type)
    page.add(txt_interval)
    page.add(btn_check)
    page.add(btn_reset)
    page.add(lbl_status)
    page.add(list_log)

if __name__ == "__main__":
    ft.app(target=main)

#  pyinstaller --name export_unifica_frotas --onefile --icon=img.ico --noconsole main.py
# flet pack --name sentinel --icon=img.ico main.py