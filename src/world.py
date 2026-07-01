import pygame
import random
from src.settings import (POSICOES_BUEIROS, LIXEIRA_RECT, TEMPO_GERAR_LIXO,
                          LARGURA, ALTURA, COR_OBSTACULO, COR_TEXTO, COR_CHUVA, COR_AGUA)

class World:
    def __init__(self, som_cracha=None):
        self.som_cracha = som_cracha
        # /CENÁRIO E MAPA/
        #  pegando as imagens e colocando na altura e largura certa
        self.mapa = pygame.image.load("assets/graphics/cenario/mapa.png")
        self.mapa = pygame.transform.scale(self.mapa, (LARGURA, ALTURA))

        # Limites do mapa
        self.construcoes = [
            pygame.Rect(0, 0, LARGURA, 30),
            pygame.Rect(0, 0, 180, ALTURA),
            pygame.Rect(1000, 0, 280, ALTURA)
        ]

        # /SISTEMA DE COLETÁVEIS/
        # Lista de coletáveis possíveis seus pesos/ probalidade
        self.coletaveis = [
            ("lixo", 70),
            ("bota", 20),
            ("cracha", 10)
        ]

        # Carrega a imagem de cada tipo de coletável e guarda em um dicionário
        self.imagens_coletaveis = {
            "lixo": pygame.image.load("assets/graphics/itens/lixo.png"),
            "bota": pygame.image.load("assets/graphics/itens/bota.png"),
            "cracha": pygame.image.load("assets/graphics/itens/cracha.png"),
        }
        for nome in self.imagens_coletaveis:
            self.imagens_coletaveis[nome] = pygame.transform.scale(self.imagens_coletaveis[nome], (50, 50))
        self.lixeira_rect = pygame.Rect(LIXEIRA_RECT)

        self.lixos_no_chao = []
        self.tempo_ultimo_lixo = pygame.time.get_ticks()
        self.pontos = 0

        # contadores por tipo — usados no placar final do game over
        self.lixos_coletados = 0
        self.botas_coletadas = 0
        self.crachas_coletados = 0

        self.fonte = pygame.font.SysFont("Arial", 40, bold=True)

        # /CLIMA E OBSTÁCULOS/
        # Configuração dos Obstáculos Móveis (Retângulos Laranja)
        # [pygame.Rect(x, y, largura, altura), velocidade_y]
        self.obstaculos = [
            [pygame.Rect(550, 0, 40, 120), 4],
            [pygame.Rect(670, -200, 40, 120), 5],
            [pygame.Rect(790, -400, 40, 120), 3]
        ]

        self.gotas_chuva = []
        for _ in range(100):
            x = random.randint(0, LARGURA)
            y = random.randint(-ALTURA, ALTURA)
            velocidade = random.randint(10, 15)
            self.gotas_chuva.append([x, y, velocidade])

        # /ISTEMA DE INUNDAÇÃO/
        # A altura da água começa em 0 pixels (no fundo da tela)
        self.altura_agua = 0
        # Superfície especial necessária para desenhar formas transparentes (RGBA)
        self.superficie_agua = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

    # /ITENS COLETÁVEIS/
    def gerar_coletavel(self):
        nomes = [c[0] for c in self.coletaveis]
        pesos = [c[1] for c in self.coletaveis]
        return random.choices(nomes, weights=pesos)[0]

    def gerenciar_lixo_por_tempo(self):
        tempo_atual = pygame.time.get_ticks()

        if tempo_atual - self.tempo_ultimo_lixo > TEMPO_GERAR_LIXO:
            bueiro_escolhido = random.choice(POSICOES_BUEIROS)

            # gera variações para o lixo espalhar pelo bueiro (meio e bordas)
            variacao_x = random.randint(-40, 40)
            variacao_y = random.randint(-20, 20)

            posicao_x = bueiro_escolhido[0] - 15 + variacao_x
            posicao_y = bueiro_escolhido[1] - 15 + variacao_y

            tipo_coletavel = self.gerar_coletavel()
            novo_lixo = pygame.Rect(posicao_x, posicao_y, 30, 30)

            # add lixo na lista pra jogar essa lista como a quantidade de lixo
            self.lixos_no_chao.append([novo_lixo, tipo_coletavel])

            self.tempo_ultimo_lixo = tempo_atual

    # /INUNDAÇÃO/
    def gerenciar_inundacao(self):
        # quantidade de lixos atualmente no chão entupindo os canos
        quantidade_lixo = len(self.lixos_no_chao)

        if quantidade_lixo > 0:
            # quanto mais lixo acumulado, mais rápido a água sobe (0.1 é a taxa de subida por frame)
            self.altura_agua += quantidade_lixo * 0.1

        # limita a água para não ultrapassar o teto do mapa completamente
        if self.altura_agua > ALTURA:
            self.altura_agua = ALTURA

    def verificar_inundacao(self):
        # retorna True quando a água atingiu o limite máximo (derrota)
        return self.altura_agua >= ALTURA

    def obter_nivel_agua_y(self):
        # retorna a coordenada Y onde a linha d'água se encontra na tela (de cima para baixo)
        return ALTURA - self.altura_agua

    # /OBSTÁCULOS/
    def atualizar_obstaculos(self, player):
        for obs in self.obstaculos:
            rect = obs[0]
            velocidade = obs[1]
            rect.y += velocidade

            #  obstáculo passar completamente do limite de baixo, ele volta ao topo
            if rect.top > ALTURA:
                rect.y = -rect.height
                obs[1] = random.randint(3, 6)  # Sorteia uma nova velocidade

            # fisica de colisão
            if player.rect.colliderect(rect):
                player.voltar_posicao()

    # /CHUVA/
    def atualizar_chuva(self):
        for gota in self.gotas_chuva:
            gota[1] += gota[2]
            # Se a gota bateu no chão da tela, volta pro topo em um X aleatório
            if gota[1] > ALTURA:
                gota[1] = random.randint(-20, -5)
                gota[0] = random.randint(0, LARGURA)

    # /SISTEMA DE COLISÕES GERAIS E INTERAÇÃO/
    def checar_colisoes(self, player):
        # COLETAR ITENS NO CHÃO
        for item in self.lixos_no_chao[:]:
            rect_coletavel = item[0]
            tipo_coletavel = item[1]

            if player.rect.colliderect(rect_coletavel):
                deve_remover = False

                if tipo_coletavel == "lixo":
                    if not player.carregando_lixo:
                        player.coletar_lixo()
                        self.lixos_coletados += 1
                        deve_remover = True
                elif tipo_coletavel == "bota":
                    player.coletar_bota()
                    self.botas_coletadas += 1
                    deve_remover = True
                elif tipo_coletavel == "cracha":
                    print("PEGOU CRACHA")
                    player.coletar_cracha()
                    self.crachas_coletados += 1

                    if self.som_cracha:
                        print("TENTANDO TOCAR CRACHA")
                        canal = self.som_cracha.play()
                        print("CANAL:", canal)

                    deve_remover = True

                if deve_remover:
                    self.lixos_no_chao.remove(item)

        #  DESCARTAR LIXO NA LIXEIRA (Apertar ESPAÇO ou E)
        if player.rect.colliderect(self.lixeira_rect):
            player.voltar_posicao()

        area_interacao = player.rect.inflate(50, 50)

        # Verificamos se essa área maior está perto o suficiente da lixeira
        if area_interacao.colliderect(self.lixeira_rect):
            if player.carregando_lixo:
                teclas = pygame.key.get_pressed()
                if teclas[pygame.K_SPACE] or teclas[pygame.K_e]:
                    if player.descartar_lixo():
                        # recompensa por limpar: escoa 60 pixels de água acumulada
                        self.altura_agua = max(0, self.altura_agua - 60)

        # COLISÃO COM PAREDES/CONSTRUÇÕES
        for bloco in self.construcoes:
            if player.rect.colliderect(bloco):
                player.voltar_posicao()

    # /ATUALIZAÇÃO E DESENHO/
    def update(self, player):
        self.pontos = player.get_pontuacao_total()
        self.gerenciar_lixo_por_tempo()
        self.gerenciar_inundacao()
        self.atualizar_obstaculos(player)
        self.atualizar_chuva()
        self.checar_colisoes(player)

    def draw(self, superficie, player):
        # desenha o mapa de fundo
        superficie.blit(self.mapa, (0, 0))

        # desenha as gotas de chuva
        for gota in self.gotas_chuva:
            pygame.draw.line(superficie, COR_CHUVA, (gota[0], gota[1]), (gota[0], gota[1] + 12), 2)

        # desenha todos os lixos ativos espalhados pelo chão
        for item in self.lixos_no_chao:
            rect_coletavel = item[0]
            tipo_coletavel = item[1]
            imagem = self.imagens_coletaveis[tipo_coletavel]
            superficie.blit(imagem, (rect_coletavel.x, rect_coletavel.y))

        # desenha os retângulos obstáculos
        for obs in self.obstaculos:
            pygame.draw.rect(superficie, COR_OBSTACULO, obs[0])

        # desenha o mar de água azul transparente se houver inundação
        if self.altura_agua > 0:
            self.superficie_agua.fill((0, 0, 0, 0))  # Reseta frame anterior
            retangulo_agua = pygame.Rect(0, ALTURA - int(self.altura_agua), LARGURA, int(self.altura_agua))
            pygame.draw.rect(self.superficie_agua, COR_AGUA, retangulo_agua)
            superficie.blit(self.superficie_agua, (0, 0))

        # desenha a pontuação em PRETO no topo esquerdo (X=20, Y=20)
        texto_pontos = self.fonte.render(f"Pontos: {player.pontuacao}", True, COR_TEXTO)
        superficie.blit(texto_pontos, (20, 20))