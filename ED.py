import pygame

# Inicialização do Pygame
pygame.init()

# Configurações da janela
TAMANHO_CELULA = 50
LINHAS = 10
COLUNAS = 10
MARGEM = 30  # Espaço para as coordenadas
LARGURA = TAMANHO_CELULA * COLUNAS + MARGEM
ALTURA = TAMANHO_CELULA * LINHAS + MARGEM
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Tabuleiro 10x10 com Coordenadas e Cursor")

# Cores
BRANCO = pygame.Color("#49E5DD")
PRETO = ("#121212")
CINZA = pygame.Color("#0F9EA5")
AMARELO = (255, 255, 0)  # Cor do cursor
AZUL = pygame.image.load("7530653-pixel-art-ship-vetor-removebg-preview.png").convert_alpha  # Cor da peça colocada
MENU_FUNDO = (200, 200, 200)  # Cor do fundo do menu

# Carrega a imagem de fundo
IMAGEM_FUNDO = pygame.image.load("Mídia.jpg").convert()  # Substitua pelo caminho da sua imagem
IMAGEM_FUNDO = pygame.transform.scale(IMAGEM_FUNDO, (LARGURA, ALTURA))

# Carrega a imagem da peça
IMAGEM_PECA = pygame.image.load("7530653-pixel-art-ship-vetor-removebg-preview.png").convert_alpha()
IMAGEM_PECA = pygame.transform.scale(IMAGEM_PECA, (TAMANHO_CELULA, TAMANHO_CELULA))

# Configuração da fonte
FONTE = pygame.font.Font(None, 24)

# Posição inicial do cursor (linha, coluna)
cursor_linha = 0
cursor_coluna = 0

# Variáveis do menu
menu_ativo = False
opcao_selecionada = 1
opcao_horizontal = True  # Por padrão, o barco é colocado horizontalmente

# Lista para armazenar as peças no tabuleiro
tabuleiro = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]

# Função para verificar se há espaço suficiente para a peça
def verificar_espaco(linha, coluna, tamanho, horizontal=True):
    if horizontal:
        # Verifica se a peça cabe horizontalmente
        if coluna + tamanho > COLUNAS:  # Verifica se cabe horizontalmente
            return False
        for c in range(coluna, coluna + tamanho):
            if tabuleiro[linha][c] is not None:  # Verifica se a célula está ocupada
                return False
    else:
        # Verifica se a peça cabe verticalmente
        if linha + tamanho > LINHAS:  # Verifica se cabe verticalmente
            return False
        for l in range(linha, linha + tamanho):
            if tabuleiro[l][coluna] is not None:  # Verifica se a célula está ocupada
                return False
    return True

# Função para colocar a peça no tabuleiro
def colocar_peca(linha, coluna, tamanho, horizontal=True):
    if horizontal:
        for c in range(coluna, coluna + tamanho):
            tabuleiro[linha][c] = "peca"
    else:
        for l in range(linha, linha + tamanho):
            tabuleiro[l][coluna] = "peca"

# Loop principal
executando = True
while executando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        elif evento.type == pygame.KEYDOWN:
            # Movimento do cursor com as setas
            if evento.key == pygame.K_UP and cursor_linha > 0:
                cursor_linha -= 1
            elif evento.key == pygame.K_DOWN and cursor_linha < LINHAS - 1:
                cursor_linha += 1
            elif evento.key == pygame.K_LEFT and cursor_coluna > 0:
                cursor_coluna -= 1
            elif evento.key == pygame.K_RIGHT and cursor_coluna < COLUNAS - 1:
                cursor_coluna += 1

            # Ativa o menu com a tecla Espaço
            if evento.key == pygame.K_SPACE:
                menu_ativo = True

            # Navegação nas opções do menu
            if menu_ativo:
                if evento.key == pygame.K_a and opcao_selecionada > 1:
                    opcao_selecionada -= 1
                elif evento.key == pygame.K_d and opcao_selecionada < 5:
                    opcao_selecionada += 1

                # Se pressionar H, altera para horizontal
                if evento.key == pygame.K_h:
                    opcao_horizontal = True

                # Se pressionar V, altera para vertical
                elif evento.key == pygame.K_v:
                    opcao_horizontal = False

                # Confirma a seleção
                if evento.key == pygame.K_RETURN:
                    menu_ativo = False
                    # Tenta colocar a peça horizontalmente ou verticalmente
                    if verificar_espaco(cursor_linha, cursor_coluna, opcao_selecionada, horizontal=opcao_horizontal):
                        colocar_peca(cursor_linha, cursor_coluna, opcao_selecionada, horizontal=opcao_horizontal)
                    else:
                        print("Não há espaço suficiente para colocar a peça.")
                    print(f"Você selecionou a opção {opcao_selecionada} que ocupa {opcao_selecionada} casas.")
    
    # Desenha a imagem de fundo
    TELA.blit(IMAGEM_FUNDO, (0, 0))

    # Superfície intermediária para o tabuleiro
    superficie_tabuleiro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

    # Desenha o tabuleiro
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            # Alterna cores para criar efeito xadrez
            if (linha + coluna) % 2 == 0:
                cor = BRANCO
            else:
                cor = CINZA
            
            # Define transparência
            cor_com_alpha = cor
            cor_com_alpha.a = 128  # 50% de opacidade

            # Desenha cada célula
            pygame.draw.rect(superficie_tabuleiro, cor_com_alpha, 
                           (coluna * TAMANHO_CELULA + MARGEM, 
                            linha * TAMANHO_CELULA + MARGEM, 
                            TAMANHO_CELULA, 
                            TAMANHO_CELULA))
            
            # Desenha as bordas
            pygame.draw.rect(superficie_tabuleiro, PRETO, 
                           (coluna * TAMANHO_CELULA + MARGEM, 
                            linha * TAMANHO_CELULA + MARGEM, 
                            TAMANHO_CELULA, 
                            TAMANHO_CELULA), 
                            1)
            # Desenha as peças no tabuleiro (ocupadas)
            if tabuleiro[linha][coluna] == "peca":
                TELA.blit(IMAGEM_PECA, (coluna * TAMANHO_CELULA + MARGEM, linha * TAMANHO_CELULA + MARGEM))
                
    # Desenha o cursor (borda amarela mais grossa)
    pygame.draw.rect(superficie_tabuleiro, AMARELO, 
                     (cursor_coluna * TAMANHO_CELULA + MARGEM, 
                      cursor_linha * TAMANHO_CELULA + MARGEM, 
                      TAMANHO_CELULA, 
                      TAMANHO_CELULA), 
                     3)  # Largura da borda do cursor

    # Adiciona coordenadas
    # Letras (A-J) no topo
    for col in range(COLUNAS):
        letra = chr(65 + col)
        texto = FONTE.render(letra, True, PRETO)
        pos_x = MARGEM + col * TAMANHO_CELULA + TAMANHO_CELULA // 2 - texto.get_width() // 2
        superficie_tabuleiro.blit(texto, (pos_x, 5))

    # Números (1-10) à esquerda
    for lin in range(LINHAS):
        numero = str(lin + 1)
        texto = FONTE.render(numero, True, PRETO)
        pos_y = MARGEM + lin * TAMANHO_CELULA + TAMANHO_CELULA // 2 - texto.get_height() // 2
        superficie_tabuleiro.blit(texto, (5, pos_y))

    # Desenha o tabuleiro sobre a imagem de fundo
    TELA.blit(superficie_tabuleiro, (0, 0))

    # Se o menu estiver ativo, desenha o menu
    if menu_ativo:
        # Desenha o fundo do menu
        pygame.draw.rect(TELA, MENU_FUNDO, (cursor_coluna * TAMANHO_CELULA + MARGEM, 
                                            cursor_linha * TAMANHO_CELULA + MARGEM - 30, 
                                            TAMANHO_CELULA * 5, 30))

        # Desenha as opções do menu
        for i in range(5):
            texto = FONTE.render(str(i + 1), True, PRETO)
            pos_x = cursor_coluna * TAMANHO_CELULA + MARGEM + i * 50 + TAMANHO_CELULA // 2 - texto.get_width() // 2
            pos_y = cursor_linha * TAMANHO_CELULA + MARGEM - 25
            TELA.blit(texto, (pos_x, pos_y))

            # Destaca a opção selecionada
            if opcao_selecionada == i + 1:
                pygame.draw.rect(TELA, AMARELO, 
                                 (cursor_coluna * TAMANHO_CELULA + MARGEM + i * 50, 
                                  cursor_linha * TAMANHO_CELULA + MARGEM - 30, 
                                  TAMANHO_CELULA, 30), 
                                 2)

    # Atualiza a tela
    pygame.display.flip()

# Encerra o Pygame
pygame.quit()
