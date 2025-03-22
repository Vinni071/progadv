import flet as ft

def main(page: ft.Page):
    page.bgcolor = ft.colors.TRANSPARENT
    page.add(
        ft.Container(
            image_src="2303292.jpg",  # Nome do arquivo na pasta do projeto
            expand=True
        ),
        ft.CupertinoFilledButton(
            content=ft.Text("CupertinoFilled"),
            opacity_on_click=0.3,
            on_click=lambda e: print("CupertinoFilledButton clicked!"),
        ),
    )

    # Definindo o stack e seus elementos
    image = ft.Image(src="2303292.jpg", fit=ft.ImageFit.COVER)
    button = ft.CupertinoFilledButton(
        content=ft.Text("Button"),
        on_click=lambda e: print("Button clicked!")
    )
    stack = ft.Stack(
        [
            image,
            button
        ],
        width=300,
        height=200
    )

    # Posicionando o botão no centro
    button.top = 80  # Ajuste conforme o tamanho da imagem
    button.left = 100  # Ajuste conforme necessário

    page.add(stack)
    

ft.app(target=main)
