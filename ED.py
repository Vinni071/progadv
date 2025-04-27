import pygame
import random
import time

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
pygame.display.set_caption("Batalha Naval - Jogador vs IA")

# Cores
BRANCO = pygame.Color("#49E5DD")
PRETO = ("#121212")
CINZA = pygame.Color("#0F9EA5")
AMARELO = (255, 255, 0)  # Cor do cursor
VERMELHO = (255, 0, 0)  # Cor para tiros acertados
AZUL_CLARO = (0, 0, 255)  # Cor para tiros na água
MENU_FUNDO = (200, 200, 200)  # Cor do fundo do menu

# Carrega a imagem de fundo
try:
    IMAGEM_FUNDO = pygame.image.load("Mídia.jpg").convert()
    IMAGEM_FUNDO = pygame.transform.scale(IMAGEM_FUNDO, (LARGURA, ALTURA))
except:
    # Fallback caso a imagem não exista
    IMAGEM_FUNDO = pygame.Surface((LARGURA, ALTURA))
    IMAGEM_FUNDO.fill((0, 0, 80))  # Fundo azul escuro

# Carrega a imagem da peça
try:
    IMAGEM_PECA = pygame.image.load("pixil-frame-0(2).png").convert_alpha()
    IMAGEM_PECA = pygame.transform.scale(IMAGEM_PECA, (TAMANHO_CELULA, TAMANHO_CELULA))
except:
    # Fallback caso a imagem não exista
    IMAGEM_PECA = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
    pygame.draw.rect(IMAGEM_PECA, (0, 0, 255, 200), (0, 0, TAMANHO_CELULA, TAMANHO_CELULA))

# Configuração da fonte
FONTE = pygame.font.Font(None, 24)

# Posição inicial do cursor (linha, coluna)
cursor_linha = 0
cursor_coluna = 0

# Variáveis do menu
menu_ativo = False
opcao_selecionada = 1
opcao_horizontal = True  # Por padrão, o barco é colocado horizontalmente

# Estados do jogo
FASE_POSICIONAMENTO = 0
FASE_JOGADOR_ATAQUE = 1
FASE_IA_ATAQUE = 2
FASE_FIM_JOGO = 3
estado_jogo = FASE_POSICIONAMENTO

# Contadores de barcos
barcos_jogador_restantes = 0
barcos_ia_restantes = 0
max_barcos = 5  # Número máximo de barcos que podem ser colocados

# Estrutura para armazenar informações sobre cada barco
barcos_jogador = []  # Lista de [linha_inicio, coluna_inicio, tamanho, horizontal, destruido]
barcos_ia = []  # Lista de [linha_inicio, coluna_inicio, tamanho, horizontal, destruido]

# Tabuleiros - separados para jogador e IA
# None: vazio, "peca": barco, "agua": tiro na água, "acerto": tiro no barco
tabuleiro_jogador = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]
tabuleiro_ia = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]

# Armazena os tiros do jogador e da IA
tiros_jogador = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]
tiros_ia = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]

# Mensagem de status
mensagem_status = "Posicione seus barcos (1-5 casas). Pressione ESPAÇO para selecionar o tamanho."
tempo_mensagem = 0

# Função para verificar se há espaço suficiente para a peça
def verificar_espaco(tabuleiro, linha, coluna, tamanho, horizontal=True):
    if horizontal:
        # Verifica se a peça cabe horizontalmente
        if coluna + tamanho > COLUNAS:
            return False
        for c in range(coluna, coluna + tamanho):
            if tabuleiro[linha][c] is not None:
                return False
    else:
        # Verifica se a peça cabe verticalmente
        if linha + tamanho > LINHAS:
            return False
        for l in range(linha, linha + tamanho):
            if tabuleiro[l][coluna] is not None:
                return False
    return True

# Função para colocar a peça no tabuleiro
def colocar_peca(tabuleiro, linha, coluna, tamanho, horizontal=True):
    if horizontal:
        for c in range(coluna, coluna + tamanho):
            tabuleiro[linha][c] = "peca"
    else:
        for l in range(linha, linha + tamanho):
            tabuleiro[l][coluna] = "peca"
    
    # Retorna as informações do barco para registro
    return [linha, coluna, tamanho, horizontal, False]  # [início_linha, início_coluna, tamanho, horizontal, destruído]

# Função para a IA posicionar seus barcos aleatoriamente
def posicionar_barcos_ia():
    global barcos_ia_restantes, barcos_ia
    
    barcos_a_posicionar = [5, 4, 3, 3, 2]  # Tamanhos dos barcos
    
    for tamanho in barcos_a_posicionar:
        posicionado = False
        while not posicionado:
            # Escolhe uma orientação aleatória (horizontal ou vertical)
            horizontal = random.choice([True, False])
            
            # Escolhe uma posição aleatória
            if horizontal:
                linha = random.randint(0, LINHAS - 1)
                coluna = random.randint(0, COLUNAS - tamanho)
            else:
                linha = random.randint(0, LINHAS - tamanho)
                coluna = random.randint(0, COLUNAS - 1)
            
            # Verifica se é possível posicionar o barco
            if verificar_espaco(tabuleiro_ia, linha, coluna, tamanho, horizontal):
                barco_info = colocar_peca(tabuleiro_ia, linha, coluna, tamanho, horizontal)
                barcos_ia.append(barco_info)
                posicionado = True
                barcos_ia_restantes += 1

# Função para verificar se um barco foi destruído
def verificar_barco_destruido(barco, tiros):
    linha, coluna, tamanho, horizontal, _ = barco
    
    if horizontal:
        for c in range(coluna, coluna + tamanho):
            if tiros[linha][c] != "acerto":
                return False
    else:
        for l in range(linha, linha + tamanho):
            if tiros[l][coluna] != "acerto":
                return False
    
    return True

# Função para a IA fazer um ataque
def ataque_ia():
    global estado_jogo, mensagem_status
    
    # Estratégia simples: atacar aleatoriamente
    atacou = False
    while not atacou:
        linha = random.randint(0, LINHAS - 1)
        coluna = random.randint(0, COLUNAS - 1)
        
        # Verifica se esta célula já foi atacada
        if tiros_ia[linha][coluna] is None:
            # Registra o tiro
            if tabuleiro_jogador[linha][coluna] == "peca":
                tiros_ia[linha][coluna] = "acerto"
                mensagem_status = f"IA acertou um barco em {chr(65 + coluna)}{linha + 1}!"
                
                # Verifica se algum barco foi completamente destruído
                barcos_destruidos = 0
                for i, barco in enumerate(barcos_jogador):
                    if not barco[4] and verificar_barco_destruido(barco, tiros_ia):  # Se não estava destruído e agora está
                        barcos_jogador[i][4] = True  # Marca como destruído
                        barcos_destruidos += 1
                        mensagem_status = f"IA destruiu um de seus barcos!"
                
                # Verifica se todos os barcos foram destruídos
                if all(barco[4] for barco in barcos_jogador):
                    mensagem_status = "Fim de jogo! A IA venceu!"
                    estado_jogo = FASE_FIM_JOGO
            else:
                tiros_ia[linha][coluna] = "agua"
                mensagem_status = f"IA errou o tiro em {chr(65 + coluna)}{linha + 1}."
            
            atacou = True
    
    # Muda para a fase de ataque do jogador
    if estado_jogo != FASE_FIM_JOGO:
        estado_jogo = FASE_JOGADOR_ATAQUE

# Função para o jogador atacar
def ataque_jogador(linha, coluna):
    global estado_jogo, mensagem_status
    
    # Verifica se esta célula já foi atacada
    if tiros_jogador[linha][coluna] is not None:
        mensagem_status = "Você já atacou esta posição!"
        return False
    
    # Registra o tiro
    if tabuleiro_ia[linha][coluna] == "peca":
        tiros_jogador[linha][coluna] = "acerto"
        mensagem_status = f"Você acertou um barco em {chr(65 + coluna)}{linha + 1}!"
        
        # Verifica se algum barco foi completamente destruído
        barcos_destruidos = 0
        for i, barco in enumerate(barcos_ia):
            if not barco[4] and verificar_barco_destruido(barco, tiros_jogador):  # Se não estava destruído e agora está
                barcos_ia[i][4] = True  # Marca como destruído
                barcos_destruidos += 1
                mensagem_status = f"Você destruiu um barco inimigo!"
        
        # Verifica se todos os barcos foram destruídos
        if all(barco[4] for barco in barcos_ia):
            mensagem_status = "Parabéns! Você venceu!"
            estado_jogo = FASE_FIM_JOGO
    else:
        tiros_jogador[linha][coluna] = "agua"
        mensagem_status = f"Você errou o tiro em {chr(65 + coluna)}{linha + 1}."
    
    # Muda para a fase de ataque da IA
    if estado_jogo != FASE_FIM_JOGO:
        estado_jogo = FASE_IA_ATAQUE
    
    return True

# Função para reiniciar o jogo
def reiniciar_jogo():
    global tabuleiro_jogador, tabuleiro_ia, tiros_jogador, tiros_ia
    global barcos_jogador_restantes, barcos_ia_restantes, estado_jogo
    global mensagem_status, cursor_linha, cursor_coluna
    global barcos_jogador, barcos_ia
    
    # Reinicia tabuleiros
    tabuleiro_jogador = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]
    tabuleiro_ia = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]
    tiros_jogador = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]
    tiros_ia = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]
    
    # Reinicia contadores e estado
    barcos_jogador_restantes = 0
    barcos_ia_restantes = 0
    barcos_jogador = []
    barcos_ia = []
    estado_jogo = FASE_POSICIONAMENTO
    
    # Posiciona o cursor
    cursor_linha = 0
    cursor_coluna = 0
    
    # Atualiza mensagem
    mensagem_status = "Posicione seus barcos (1-5 casas). Pressione ESPAÇO para selecionar o tamanho."

# Loop principal
executando = True
clock = pygame.time.Clock()

while executando:
    # Gerencia a passagem de tempo para as mensagens
    if tempo_mensagem > 0:
        tempo_mensagem -= 1
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        elif evento.type == pygame.KEYDOWN:
            # Tecla R para reiniciar o jogo
            if evento.key == pygame.K_r:
                reiniciar_jogo()
                
            # Movimento do cursor com as setas
            if evento.key == pygame.K_UP and cursor_linha > 0:
                cursor_linha -= 1
            elif evento.key == pygame.K_DOWN and cursor_linha < LINHAS - 1:
                cursor_linha += 1
            elif evento.key == pygame.K_LEFT and cursor_coluna > 0:
                cursor_coluna -= 1
            elif evento.key == pygame.K_RIGHT and cursor_coluna < COLUNAS - 1:
                cursor_coluna += 1
            
            # Lógica dependendo do estado do jogo
            if estado_jogo == FASE_POSICIONAMENTO:
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
                        if verificar_espaco(tabuleiro_jogador, cursor_linha, cursor_coluna, opcao_selecionada, horizontal=opcao_horizontal):
                            barco_info = colocar_peca(tabuleiro_jogador, cursor_linha, cursor_coluna, opcao_selecionada, horizontal=opcao_horizontal)
                            barcos_jogador.append(barco_info)
                            barcos_jogador_restantes += 1
                            
                            # Verifica se todos os barcos já foram posicionados
                            if barcos_jogador_restantes >= max_barcos:
                                mensagem_status = "Todos os barcos posicionados! Agora ataque a frota inimiga!"
                                # Posiciona os barcos da IA
                                posicionar_barcos_ia()
                                # Muda para a fase de ataque
                                estado_jogo = FASE_JOGADOR_ATAQUE
                        else:
                            mensagem_status = "Não há espaço suficiente para colocar a peça."
                            tempo_mensagem = 60
            
            elif estado_jogo == FASE_JOGADOR_ATAQUE:
                # Jogador ataca com ENTER/RETURN
                if evento.key == pygame.K_RETURN:
                    if ataque_jogador(cursor_linha, cursor_coluna):
                        # Após o ataque do jogador, a IA atacará no próximo ciclo
                        pass
            
            elif estado_jogo == FASE_FIM_JOGO:
                # Reinicia o jogo com R
                if evento.key == pygame.K_r:
                    reiniciar_jogo()
    
    # Lógica para o turno da IA
    if estado_jogo == FASE_IA_ATAQUE:
        # Pequena pausa para o jogador processar o que está acontecendo
        time.sleep(0.5)
        ataque_ia()
    
    # Desenha a imagem de fundo
    TELA.blit(IMAGEM_FUNDO, (0, 0))
    
    # Superfície intermediária para o tabuleiro
    superficie_tabuleiro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    
    # Determina qual tabuleiro mostrar com base no estado do jogo
    tabuleiro_atual = tabuleiro_jogador if estado_jogo == FASE_POSICIONAMENTO or estado_jogo == FASE_IA_ATAQUE else tabuleiro_ia
    tiros_atual = tiros_ia if estado_jogo == FASE_POSICIONAMENTO or estado_jogo == FASE_IA_ATAQUE else tiros_jogador
    
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
            cor_com_alpha.a = 0  # 0% de opacidade
            
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
            if estado_jogo == FASE_POSICIONAMENTO or estado_jogo == FASE_IA_ATAQUE:
                # Mostra o tabuleiro do jogador
                if tabuleiro_jogador[linha][coluna] == "peca":
                    TELA.blit(IMAGEM_PECA, (coluna * TAMANHO_CELULA + MARGEM, linha * TAMANHO_CELULA + MARGEM))
                
                # Mostra os tiros da IA no tabuleiro do jogador
                if tiros_ia[linha][coluna] == "acerto":
                    pygame.draw.circle(TELA, VERMELHO, 
                                    (coluna * TAMANHO_CELULA + MARGEM + TAMANHO_CELULA // 2, 
                                     linha * TAMANHO_CELULA + MARGEM + TAMANHO_CELULA // 2), 
                                    TAMANHO_CELULA // 4)
                elif tiros_ia[linha][coluna] == "agua":
                    pygame.draw.circle(TELA, AZUL_CLARO, 
                                    (coluna * TAMANHO_CELULA + MARGEM + TAMANHO_CELULA // 2, 
                                     linha * TAMANHO_CELULA + MARGEM + TAMANHO_CELULA // 2), 
                                    TAMANHO_CELULA // 4)
            else:
                # Mostra os tiros do jogador no tabuleiro da IA
                if tiros_jogador[linha][coluna] == "acerto":
                    pygame.draw.circle(TELA, VERMELHO, 
                                    (coluna * TAMANHO_CELULA + MARGEM + TAMANHO_CELULA // 2, 
                                     linha * TAMANHO_CELULA + MARGEM + TAMANHO_CELULA // 2), 
                                    TAMANHO_CELULA // 4)
                elif tiros_jogador[linha][coluna] == "agua":
                    pygame.draw.circle(TELA, AZUL_CLARO, 
                                    (coluna * TAMANHO_CELULA + MARGEM + TAMANHO_CELULA // 2, 
                                     linha * TAMANHO_CELULA + MARGEM + TAMANHO_CELULA // 2), 
                                    TAMANHO_CELULA // 4)
    
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
    if menu_ativo and estado_jogo == FASE_POSICIONAMENTO:
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
    
    # Exibe a mensagem de status
    fundo_mensagem = pygame.Surface((LARGURA, 30), pygame.SRCALPHA)
    fundo_mensagem.fill((0, 0, 0, 150))  # Fundo semi-transparente
    TELA.blit(fundo_mensagem, (0, ALTURA - 30))
    
    texto_mensagem = FONTE.render(mensagem_status, True, (255, 255, 255))
    TELA.blit(texto_mensagem, (10, ALTURA - 25))
    
    # Exibe informações do estado do jogo
    texto_fase = ""
    if estado_jogo == FASE_POSICIONAMENTO:
        texto_fase = f"Fase: Posicionamento - Barcos: {barcos_jogador_restantes}/{max_barcos}"
    elif estado_jogo == FASE_JOGADOR_ATAQUE:
        texto_fase = "Fase: Seu ataque - Pressione ENTER para atacar"
    elif estado_jogo == FASE_IA_ATAQUE:
        texto_fase = "Fase: Ataque inimigo"
    elif estado_jogo == FASE_FIM_JOGO:
        texto_fase = "Fim de Jogo - Pressione R para reiniciar"
    
    texto_info = FONTE.render(texto_fase, True, (255, 255, 255))
    TELA.blit(fundo_mensagem, (0, 0))
    TELA.blit(texto_info, (10, 5))
    
    # Atualiza a tela
    pygame.display.flip()
    
    # Controla FPS
    clock.tick(30)

# Encerra o Pygame
pygame.quit()