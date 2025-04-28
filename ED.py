import pygame
import random
import time
from abc import ABC, abstractmethod

# Classes abstratas
class ElementoJogo(ABC):
    @abstractmethod
    def desenhar(self, tela):
        pass

# Classe para representar uma posição no tabuleiro
class Posicao:
    def __init__(self, linha, coluna):
        self.linha = linha
        self.coluna = coluna
    
    def __eq__(self, other):
        if isinstance(other, Posicao):
            return self.linha == other.linha and self.coluna == other.coluna
        return False
    
    def __str__(self):
        return f"{chr(65 + self.coluna)}{self.linha + 1}"

# Classe abstrata para navios
class Navio(ElementoJogo, ABC):
    def __init__(self, posicao_inicial, horizontal=True):
        self.posicao_inicial = posicao_inicial
        self.horizontal = horizontal
        self.destruido = False
        self.posicoes = []
        self._calcular_posicoes()
    
    def _calcular_posicoes(self):
        self.posicoes = []
        linha, coluna = self.posicao_inicial.linha, self.posicao_inicial.coluna
        for i in range(self.tamanho):
            if self.horizontal:
                self.posicoes.append(Posicao(linha, coluna + i))
            else:
                self.posicoes.append(Posicao(linha + i, coluna))
    
    def verificar_destruido(self, tiros):
        for pos in self.posicoes:
            if tiros[pos.linha][pos.coluna] != "acerto":
                return False
        self.destruido = True
        return True
    
    def desenhar(self, tela, imagem, tamanho_celula, margem):
        if not self.destruido:
            for pos in self.posicoes:
                tela.blit(imagem, (pos.coluna * tamanho_celula + margem, 
                                  pos.linha * tamanho_celula + margem))
    
    def cabe_no_tabuleiro(self, linhas, colunas):
        for pos in self.posicoes:
            if pos.linha < 0 or pos.linha >= linhas or pos.coluna < 0 or pos.coluna >= colunas:
                return False
        return True

# Classes específicas para cada tipo de navio
class PortaAvioes(Navio):
    tamanho = 5
    def __str__(self):
        return f"Porta-Aviões em {self.posicao_inicial}"

class Encouracado(Navio):
    tamanho = 4
    def __str__(self):
        return f"Encouraçado em {self.posicao_inicial}"

class Cruzador(Navio):
    tamanho = 3
    def __str__(self):
        return f"Cruzador em {self.posicao_inicial}"

class Submarino(Navio):
    tamanho = 2
    def __str__(self):
        return f"Submarino em {self.posicao_inicial}"

class Destroyer(Navio):
    tamanho = 1
    def __str__(self):
        return f"Destroyer em {self.posicao_inicial}"

# Classe para o tabuleiro
class Tabuleiro(ElementoJogo):
    def __init__(self, linhas, colunas, tamanho_celula, margem):
        self.linhas = linhas
        self.colunas = colunas
        self.tamanho_celula = tamanho_celula
        self.margem = margem
        self.grade = [[None for _ in range(colunas)] for _ in range(linhas)]
        self.tiros = [[None for _ in range(colunas)] for _ in range(linhas)]
        self.navios = []
    
    def verificar_espaco(self, navio):
        for pos in navio.posicoes:
            if not (0 <= pos.linha < self.linhas and 0 <= pos.coluna < self.colunas):
                return False
            if self.grade[pos.linha][pos.coluna] is not None:
                return False
        return True
    
    def adicionar_navio(self, navio):
        if self.verificar_espaco(navio):
            for pos in navio.posicoes:
                self.grade[pos.linha][pos.coluna] = "peca"
            self.navios.append(navio)
            return True
        return False
    
    def receber_tiro(self, posicao):
        if self.tiros[posicao.linha][posicao.coluna] is not None:
            return None, None  # Tiro já foi dado nesta posição - Retorna uma tupla de (None, None)
        
        if self.grade[posicao.linha][posicao.coluna] == "peca":
            self.tiros[posicao.linha][posicao.coluna] = "acerto"
            
            # Verifica se algum navio foi destruído
            for navio in self.navios:
                if not navio.destruido and navio.verificar_destruido(self.tiros):
                    return "destruido", navio
            return "acerto", None
        else:
            self.tiros[posicao.linha][posicao.coluna] = "agua"
            return "agua", None
    
    def todos_navios_destruidos(self):
        return all(navio.destruido for navio in self.navios)
    
    def desenhar(self, tela, imagem_peca, cores, fonte, mostrar_navios=True):
        # Superfície intermediária para o tabuleiro
        superficie_tabuleiro = pygame.Surface((self.colunas * self.tamanho_celula + self.margem, 
                                              self.linhas * self.tamanho_celula + self.margem), 
                                             pygame.SRCALPHA)
        
        # Desenha o tabuleiro
        for linha in range(self.linhas):
            for coluna in range(self.colunas):
                # Alterna cores para criar efeito xadrez
                if (linha + coluna) % 2 == 0:
                    cor = cores["BRANCO"]
                else:
                    cor = cores["CINZA"]
                
                # Define transparência
                cor_com_alpha = cor
                cor_com_alpha.a = 0  # 0% de opacidade
                
                # Desenha cada célula
                pygame.draw.rect(superficie_tabuleiro, cor_com_alpha, 
                               (coluna * self.tamanho_celula + self.margem, 
                                linha * self.tamanho_celula + self.margem, 
                                self.tamanho_celula, 
                                self.tamanho_celula))
                
                # Desenha as bordas
                pygame.draw.rect(superficie_tabuleiro, cores["PRETO"], 
                               (coluna * self.tamanho_celula + self.margem, 
                                linha * self.tamanho_celula + self.margem, 
                                self.tamanho_celula, 
                                self.tamanho_celula), 
                                1)
                
                # Desenha as peças e tiros
                if mostrar_navios and self.grade[linha][coluna] == "peca":
                    tela.blit(imagem_peca, (coluna * self.tamanho_celula + self.margem, 
                                          linha * self.tamanho_celula + self.margem))
                
                # Mostra os tiros
                if self.tiros[linha][coluna] == "acerto":
                    pygame.draw.circle(tela, cores["VERMELHO"], 
                                    (coluna * self.tamanho_celula + self.margem + self.tamanho_celula // 2, 
                                     linha * self.tamanho_celula + self.margem + self.tamanho_celula // 2), 
                                    self.tamanho_celula // 4)
                elif self.tiros[linha][coluna] == "agua":
                    pygame.draw.circle(tela, cores["AZUL_CLARO"], 
                                    (coluna * self.tamanho_celula + self.margem + self.tamanho_celula // 2, 
                                     linha * self.tamanho_celula + self.margem + self.tamanho_celula // 2), 
                                    self.tamanho_celula // 4)
        
        # Adiciona coordenadas
        # Letras (A-J) no topo
        for col in range(self.colunas):
            letra = chr(65 + col)
            texto = fonte.render(letra, True, cores["PRETO"])
            pos_x = self.margem + col * self.tamanho_celula + self.tamanho_celula // 2 - texto.get_width() // 2
            superficie_tabuleiro.blit(texto, (pos_x, 5))
        
        # Números (1-10) à esquerda
        for lin in range(self.linhas):
            numero = str(lin + 1)
            texto = fonte.render(numero, True, cores["PRETO"])
            pos_y = self.margem + lin * self.tamanho_celula + self.tamanho_celula // 2 - texto.get_height() // 2
            superficie_tabuleiro.blit(texto, (5, pos_y))
        
        # Desenha o tabuleiro na tela
        tela.blit(superficie_tabuleiro, (0, 0))

# Classes para jogadores
class Jogador(ABC):
    def __init__(self, tabuleiro):
        self.tabuleiro = tabuleiro
        self.adversario = None
    
    def definir_adversario(self, adversario):
        self.adversario = adversario
    
    @abstractmethod
    def realizar_jogada(self):
        pass

class JogadorHumano(Jogador):
    def __init__(self, tabuleiro, cursor_pos):
        super().__init__(tabuleiro)
        self.cursor_pos = cursor_pos
    
    def realizar_jogada(self):
        # Esta função é chamada pelo controle do jogo quando o jogador faz um clique
        posicao = Posicao(self.cursor_pos[0], self.cursor_pos[1])
        return self.adversario.tabuleiro.receber_tiro(posicao)  # Retorna explicitamente o resultado

class JogadorIA(Jogador):
    def __init__(self, tabuleiro):
        super().__init__(tabuleiro)
        
    def realizar_jogada(self):
        # Estratégia simples: atacar aleatoriamente
        while True:
            linha = random.randint(0, self.adversario.tabuleiro.linhas - 1)
            coluna = random.randint(0, self.adversario.tabuleiro.colunas - 1)
            posicao = Posicao(linha, coluna)
            
            if self.adversario.tabuleiro.tiros[linha][coluna] is None:
                resultado, navio = self.adversario.tabuleiro.receber_tiro(posicao)
                return resultado, navio, posicao

# Classe principal para controlar o jogo
class Jogo:
    # Estados do jogo
    FASE_POSICIONAMENTO = 0
    FASE_JOGADOR_ATAQUE = 1
    FASE_IA_ATAQUE = 2
    FASE_FIM_JOGO = 3
    
    def __init__(self):
        # Inicialização do Pygame
        pygame.init()
        
        # Configurações da janela
        self.TAMANHO_CELULA = 50
        self.LINHAS = 10
        self.COLUNAS = 10
        self.MARGEM = 30  # Espaço para as coordenadas
        self.LARGURA = self.TAMANHO_CELULA * self.COLUNAS + self.MARGEM
        self.ALTURA = self.TAMANHO_CELULA * self.LINHAS + self.MARGEM
        self.TELA = pygame.display.set_mode((self.LARGURA, self.ALTURA))
        pygame.display.set_caption("Batalha Naval - Jogador vs IA")
        
        # Cores
        self.cores = {
            "BRANCO": pygame.Color("#49E5DD"),
            "PRETO": pygame.Color("#121212"),
            "CINZA": pygame.Color("#0F9EA5"),
            "AMARELO": pygame.Color(255, 255, 0),  # Cor do cursor
            "VERMELHO": pygame.Color(255, 0, 0),  # Cor para tiros acertados
            "AZUL_CLARO": pygame.Color(0, 0, 255),  # Cor para tiros na água
            "MENU_FUNDO": pygame.Color(200, 200, 200)  # Cor do fundo do menu
        }
        
        # Carrega a imagem de fundo
        try:
            self.IMAGEM_FUNDO = pygame.image.load("Mídia.jpg").convert()
            self.IMAGEM_FUNDO = pygame.transform.scale(self.IMAGEM_FUNDO, (self.LARGURA, self.ALTURA))
        except:
            # Fallback caso a imagem não exista
            self.IMAGEM_FUNDO = pygame.Surface((self.LARGURA, self.ALTURA))
            self.IMAGEM_FUNDO.fill((0, 0, 80))  # Fundo azul escuro
        
        # Carrega a imagem da peça
        try:
            self.IMAGEM_PECA = pygame.image.load("pixil-frame-0(2).png").convert_alpha()
            self.IMAGEM_PECA = pygame.transform.scale(self.IMAGEM_PECA, (self.TAMANHO_CELULA, self.TAMANHO_CELULA))
        except:
            # Fallback caso a imagem não exista
            self.IMAGEM_PECA = pygame.Surface((self.TAMANHO_CELULA, self.TAMANHO_CELULA), pygame.SRCALPHA)
            pygame.draw.rect(self.IMAGEM_PECA, (0, 0, 255, 200), (0, 0, self.TAMANHO_CELULA, self.TAMANHO_CELULA))
        
        # Configuração da fonte
        self.FONTE = pygame.font.Font(None, 24)
        
        # Inicialização dos componentes do jogo
        self.reiniciar_jogo()
        
        # Loop principal e controle de FPS
        self.executando = True
        self.clock = pygame.time.Clock()
    
    def reiniciar_jogo(self):
        # Tabuleiros
        self.tabuleiro_jogador = Tabuleiro(self.LINHAS, self.COLUNAS, self.TAMANHO_CELULA, self.MARGEM)
        self.tabuleiro_ia = Tabuleiro(self.LINHAS, self.COLUNAS, self.TAMANHO_CELULA, self.MARGEM)
        
        # Posição do cursor
        self.cursor_linha = 0
        self.cursor_coluna = 0
        
        # Jogadores
        self.jogador_humano = JogadorHumano(self.tabuleiro_jogador, (self.cursor_linha, self.cursor_coluna))
        self.jogador_ia = JogadorIA(self.tabuleiro_ia)
        
        # Configuração do adversário
        self.jogador_humano.definir_adversario(self.jogador_ia)
        self.jogador_ia.definir_adversario(self.jogador_humano)
        
        # Variáveis do menu
        self.menu_ativo = False
        self.opcao_selecionada = 1
        self.opcao_horizontal = True  # Por padrão, o barco é colocado horizontalmente
        
        # Estado e mensagem
        self.estado_jogo = self.FASE_POSICIONAMENTO
        self.mensagem_status = "Posicione seus barcos (1-5 casas). Pressione ESPAÇO para selecionar o tamanho."
        self.tempo_mensagem = 0
        
        # Contadores
        self.max_barcos = 5  # Número máximo de barcos
    
    def posicionar_barcos_ia(self):
        # Tipos de navios a serem posicionados
        tipos_navios = [PortaAvioes, Encouracado, Cruzador, Submarino, Destroyer]
        
        for tipo_navio in tipos_navios:
            posicionado = False
            while not posicionado:
                # Escolhe uma orientação aleatória
                horizontal = random.choice([True, False])
                
                # Escolhe uma posição aleatória
                if horizontal:
                    linha = random.randint(0, self.LINHAS - 1)
                    coluna = random.randint(0, self.COLUNAS - tipo_navio.tamanho)
                else:
                    linha = random.randint(0, self.LINHAS - tipo_navio.tamanho)
                    coluna = random.randint(0, self.COLUNAS - 1)
                
                # Cria e tenta posicionar o navio
                posicao = Posicao(linha, coluna)
                navio = tipo_navio(posicao, horizontal)
                if self.tabuleiro_ia.adicionar_navio(navio):
                    posicionado = True
    
    def atualizar_cursor(self, linha, coluna):
        self.cursor_linha = max(0, min(linha, self.LINHAS - 1))
        self.cursor_coluna = max(0, min(coluna, self.COLUNAS - 1))
        self.jogador_humano.cursor_pos = (self.cursor_linha, self.cursor_coluna)
    
    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.executando = False
            elif evento.type == pygame.KEYDOWN:
                self.processar_tecla(evento.key)
    
    def processar_tecla(self, tecla):
        # Tecla R para reiniciar o jogo
        if tecla == pygame.K_r:
            self.reiniciar_jogo()
            
        # Movimento do cursor com as setas
        elif tecla == pygame.K_UP and self.cursor_linha > 0:
            self.atualizar_cursor(self.cursor_linha - 1, self.cursor_coluna)
        elif tecla == pygame.K_DOWN and self.cursor_linha < self.LINHAS - 1:
            self.atualizar_cursor(self.cursor_linha + 1, self.cursor_coluna)
        elif tecla == pygame.K_LEFT and self.cursor_coluna > 0:
            self.atualizar_cursor(self.cursor_linha, self.cursor_coluna - 1)
        elif tecla == pygame.K_RIGHT and self.cursor_coluna < self.COLUNAS - 1:
            self.atualizar_cursor(self.cursor_linha, self.cursor_coluna + 1)
        
        # Lógica dependendo do estado do jogo
        if self.estado_jogo == self.FASE_POSICIONAMENTO:
            self.processar_fase_posicionamento(tecla)
        elif self.estado_jogo == self.FASE_JOGADOR_ATAQUE:
            self.processar_fase_jogador_ataque(tecla)
        elif self.estado_jogo == self.FASE_FIM_JOGO:
            # Reinicia o jogo com R (já tratado acima)
            pass
    
    def processar_fase_posicionamento(self, tecla):
        # Ativa o menu com a tecla Espaço
        if tecla == pygame.K_SPACE:
            self.menu_ativo = True
        
        # Navegação nas opções do menu
        if self.menu_ativo:
            if tecla == pygame.K_a and self.opcao_selecionada > 1:
                self.opcao_selecionada -= 1
            elif tecla == pygame.K_d and self.opcao_selecionada < 5:
                self.opcao_selecionada += 1
            
            # Se pressionar H, altera para horizontal
            if tecla == pygame.K_h:
                self.opcao_horizontal = True
            
            # Se pressionar V, altera para vertical
            elif tecla == pygame.K_v:
                self.opcao_horizontal = False
            
            # Confirma a seleção
            if tecla == pygame.K_RETURN:
                self.menu_ativo = False
                self.criar_navio()
    
    def criar_navio(self):
        # Mapeamento de tamanho para tipo de navio
        tipos_navios = {
            1: Destroyer,
            2: Submarino,
            3: Cruzador,
            4: Encouracado,
            5: PortaAvioes
        }
        
        tipo_navio = tipos_navios.get(self.opcao_selecionada)
        if tipo_navio:
            posicao = Posicao(self.cursor_linha, self.cursor_coluna)
            navio = tipo_navio(posicao, self.opcao_horizontal)
            
            if self.tabuleiro_jogador.adicionar_navio(navio):
                # Verifica se todos os barcos já foram posicionados
                if len(self.tabuleiro_jogador.navios) >= self.max_barcos:
                    self.mensagem_status = "Todos os barcos posicionados! Agora ataque a frota inimiga!"
                    # Posiciona os barcos da IA
                    self.posicionar_barcos_ia()
                    # Muda para a fase de ataque
                    self.estado_jogo = self.FASE_JOGADOR_ATAQUE
            else:
                self.mensagem_status = "Não há espaço suficiente para colocar a peça."
                self.tempo_mensagem = 60
    
    def processar_fase_jogador_ataque(self, tecla):
        # Jogador ataca com ENTER/RETURN
        if tecla == pygame.K_RETURN:
            resultado, navio = self.jogador_humano.realizar_jogada()
            
            if resultado is None:
                self.mensagem_status = "Você já atacou esta posição!"
                return
            
            # Processa o resultado do ataque
            if resultado == "acerto":
                self.mensagem_status = f"Você acertou um barco em {chr(65 + self.cursor_coluna)}{self.cursor_linha + 1}!"
            elif resultado == "destruido":
                self.mensagem_status = f"Você destruiu um barco inimigo!"
                
                # Verifica se todos os barcos foram destruídos
                if self.tabuleiro_ia.todos_navios_destruidos():
                    self.mensagem_status = "Parabéns! Você venceu!"
                    self.estado_jogo = self.FASE_FIM_JOGO
            else:  # água
                self.mensagem_status = f"Você errou o tiro em {chr(65 + self.cursor_coluna)}{self.cursor_linha + 1}."
            
            # Muda para a fase de ataque da IA
            if self.estado_jogo != self.FASE_FIM_JOGO:
                self.estado_jogo = self.FASE_IA_ATAQUE
    
    def processar_ataque_ia(self):
        # Pequena pausa para o jogador processar o que está acontecendo
        time.sleep(0.5)
        
        # IA realiza sua jogada
        resultado, navio, posicao = self.jogador_ia.realizar_jogada()
        
        # Processa o resultado do ataque
        if resultado == "acerto":
            self.mensagem_status = f"IA acertou um barco em {posicao}!"
        elif resultado == "destruido":
            self.mensagem_status = f"IA destruiu um de seus barcos!"
            
            # Verifica se todos os barcos foram destruídos
            if self.tabuleiro_jogador.todos_navios_destruidos():
                self.mensagem_status = "Fim de jogo! A IA venceu!"
                self.estado_jogo = self.FASE_FIM_JOGO
        else:  # água
            self.mensagem_status = f"IA errou o tiro em {posicao}."
        
        # Muda para a fase de ataque do jogador
        if self.estado_jogo != self.FASE_FIM_JOGO:
            self.estado_jogo = self.FASE_JOGADOR_ATAQUE
    
    def desenhar_menu(self):
        # Desenha o fundo do menu
        pygame.draw.rect(self.TELA, self.cores["MENU_FUNDO"], 
                         (self.cursor_coluna * self.TAMANHO_CELULA + self.MARGEM, 
                          self.cursor_linha * self.TAMANHO_CELULA + self.MARGEM - 30, 
                          self.TAMANHO_CELULA * 5, 30))
        
        # Desenha as opções do menu
        for i in range(5):
            texto = self.FONTE.render(str(i + 1), True, self.cores["PRETO"])
            pos_x = self.cursor_coluna * self.TAMANHO_CELULA + self.MARGEM + i * 50 + self.TAMANHO_CELULA // 2 - texto.get_width() // 2
            pos_y = self.cursor_linha * self.TAMANHO_CELULA + self.MARGEM - 25
            self.TELA.blit(texto, (pos_x, pos_y))
            
            # Destaca a opção selecionada
            if self.opcao_selecionada == i + 1:
                pygame.draw.rect(self.TELA, self.cores["AMARELO"], 
                                 (self.cursor_coluna * self.TAMANHO_CELULA + self.MARGEM + i * 50, 
                                  self.cursor_linha * self.TAMANHO_CELULA + self.MARGEM - 30, 
                                  self.TAMANHO_CELULA, 30), 
                                 2)
    
    def desenhar_cursor(self):
        # Desenha o cursor (borda amarela mais grossa)
        pygame.draw.rect(self.TELA, self.cores["AMARELO"], 
                         (self.cursor_coluna * self.TAMANHO_CELULA + self.MARGEM, 
                          self.cursor_linha * self.TAMANHO_CELULA + self.MARGEM, 
                          self.TAMANHO_CELULA, 
                          self.TAMANHO_CELULA), 
                         3)  # Largura da borda do cursor
    
    def desenhar_informacoes(self):
        # Exibe a mensagem de status
        fundo_mensagem = pygame.Surface((self.LARGURA, 30), pygame.SRCALPHA)
        fundo_mensagem.fill((0, 0, 0, 150))  # Fundo semi-transparente
        self.TELA.blit(fundo_mensagem, (0, self.ALTURA - 30))
        
        texto_mensagem = self.FONTE.render(self.mensagem_status, True, (255, 255, 255))
        self.TELA.blit(texto_mensagem, (10, self.ALTURA - 25))
        
        # Exibe informações do estado do jogo
        texto_fase = ""
        if self.estado_jogo == self.FASE_POSICIONAMENTO:
            texto_fase = f"Fase: Posicionamento - Barcos: {len(self.tabuleiro_jogador.navios)}/{self.max_barcos}"
        elif self.estado_jogo == self.FASE_JOGADOR_ATAQUE:
            texto_fase = "Fase: Seu ataque - Pressione ENTER para atacar"
        elif self.estado_jogo == self.FASE_IA_ATAQUE:
            texto_fase = "Fase: Ataque inimigo"
        elif self.estado_jogo == self.FASE_FIM_JOGO:
            texto_fase = "Fim de Jogo - Pressione R para reiniciar"
        
        texto_info = self.FONTE.render(texto_fase, True, (255, 255, 255))
        self.TELA.blit(fundo_mensagem, (0, 0))
        self.TELA.blit(texto_info, (10, 5))
    
    def atualizar(self):
        # Gerencia a passagem de tempo para as mensagens
        if self.tempo_mensagem > 0:
            self.tempo_mensagem -= 1
        
        # Lógica para o turno da IA
        if self.estado_jogo == self.FASE_IA_ATAQUE:
            self.processar_ataque_ia()
    
    def desenhar(self):
        # Desenha a imagem de fundo
        self.TELA.blit(self.IMAGEM_FUNDO, (0, 0))
        
        # Determina qual tabuleiro mostrar com base no estado do jogo
        if self.estado_jogo == self.FASE_POSICIONAMENTO or self.estado_jogo == self.FASE_IA_ATAQUE:
            # Mostra o tabuleiro do jogador
            self.tabuleiro_jogador.desenhar(self.TELA, self.IMAGEM_PECA, self.cores, self.FONTE, True)
        else:
            # Mostra o tabuleiro da IA
            self.tabuleiro_ia.desenhar(self.TELA, self.IMAGEM_PECA, self.cores, self.FONTE, False)
        
        # Desenha o cursor
        self.desenhar_cursor()
        
        # Se o menu estiver ativo, desenha o menu
        if self.menu_ativo and self.estado_jogo == self.FASE_POSICIONAMENTO:
            self.desenhar_menu()
        
        # Desenha as informações do jogo
        self.desenhar_informacoes()
        
        # Atualiza a tela
        pygame.display.flip()
    
    def executar(self):
        # Loop principal do jogo
        while self.executando:
            # Processa eventos
            self.processar_eventos()
            
            # Atualiza o estado do jogo
            self.atualizar()
            
            # Renderiza o jogo
            self.desenhar()
        # Desenha
# Desenha as informações do jogo
        self.desenhar_informacoes()
        
        # Atualiza a tela
        pygame.display.flip()
    
    def executar(self):
        # Loop principal do jogo
        while self.executando:
            # Processa eventos
            self.processar_eventos()
            
            # Atualiza o estado do jogo
            self.atualizar()
            
            # Renderiza o jogo
            self.desenhar()
            
            # Controla FPS
            self.clock.tick(30)
        
        # Encerra o Pygame
        pygame.quit()

# Inicialização e execução do jogo
if __name__ == "__main__":
    jogo = Jogo()
    jogo.executar()