import flet as ft
import subprocess
import sys

def run_script(script_path):
    subprocess.Popen(["python3", script_path])

def kill(*scripts):
    for script in scripts:
        subprocess.Popen(["pkill", "-f", script])

def main(page: ft.Page):
    page.title = "Batalha Naval"
    page.window_width = 500
    page.window_height = 500
    page.padding = 0
    page.spacing = 0

    # Logo
    logo = ft.Image(
        src="Minha_imagem_do_ChatGPT-removebg-preview.png",
        width=250,
        height=250
    )

    # Botões
    jogar_btn = ft.ElevatedButton(
        text="JOGAR",
        style=ft.ButtonStyle(
            padding=20,
            bgcolor=ft.colors.BLUE_700,
            color=ft.colors.WHITE,
        ),
        on_click=lambda e: run_script("ED.py")
    )

    sair_btn = ft.ElevatedButton(
        text="SAIR",
        style=ft.ButtonStyle(
            padding=20,
            bgcolor=ft.colors.RED_700,
            color=ft.colors.WHITE,
        ),
        on_click=lambda e: kill("ED.py", "index.py")
    )

    # Conteúdo central
    conteudo = ft.Column(
        [
            logo,
            ft.Container(height=30),
            jogar_btn,
            ft.Container(height=10),
            sair_btn
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )

    # Fundo: Container que expande e centraliza o GIF
    fundo = ft.Container(
        expand=True,                              # ocupa toda a janela
        alignment=ft.alignment.center,            # centraliza o conteúdo
        content=ft.Image(
            src="Mídia.gif",
            fit=ft.ImageFit.COVER,              # mantém proporção sem distorcer
            expand=True                           # permite crescer dentro do container
        )
    )

    # Stack com imagem de fundo + conteúdo centralizado
    page.add(
        ft.Stack(
            controls=[
                fundo,
                conteudo
            ],
            expand=True
        )
    )

ft.app(target=main)

