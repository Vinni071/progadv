import flet as ft


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
        on_click=lambda e: print("Jogar clicado")
    )

    sair_btn = ft.ElevatedButton(
        text="SAIR",
        style=ft.ButtonStyle(
            padding=20,
            bgcolor=ft.colors.RED_700,
            color=ft.colors.WHITE,
        ),
        on_click=lambda e: page.close
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

    # Stack com imagem de fundo + conteúdo
    fundo = ft.Image(
        src="Mídia.gif",  # imagem de fundo (pode ser caminho local ou URL)
        fit=ft.ImageFit.COVER,
        expand=True
    )

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
