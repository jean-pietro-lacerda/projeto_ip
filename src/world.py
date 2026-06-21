import pygame
import random
from src.settings import (POSICOES_BUEIROS, LIXEIRA_RECT, TEMPO_GERAR_LIXO,
                          LARGURA, ALTURA, COR_OBSTACULO, COR_TEXTO, COR_CHUVA, COR_AGUA)


class World:
    def __init__(self):
        #  pegando as imagens e colocando na altura e largura certa
        self.mapa = pygame.image.load("assets/graphics/mapa.png")
        self.mapa = pygame.transform.scale(self.mapa, (LARGURA, ALTURA))
        self.imagem_lixo = pygame.image.load("assets/graphics/lixo.png")
        self.imagem_lixo = pygame.transform.scale(self.imagem_lixo, (30, 30))

        self.lixeira_rect = pygame.Rect(LIXEIRA_RECT)

        self.lixos_no_chao = []
        self.tempo_ultimo_lixo = pygame.time.get_ticks()
        self.pontos = 0

        # Fonte em Negrito para os pontos ficarem bem visíveis em preto na calçada clara
        self.fonte = pygame.font.SysFont("Arial", 40, bold=True)

        # Configuração dos Obstáculos Móveis (Retângulos Laranja)
        # [pygame.Rect(x, y, largura, altura), velocidade_y]
        self.obstaculos = [
            [pygame.Rect(550, 0, 40, 120), 4],
            [pygame.Rect(670, -200, 40, 120), 5],
            [pygame.Rect(790, -400, 40, 120), 3]
        ]

        self.construcoes = [
            pygame.Rect(0, 0, 388, 189),
            pygame.Rect(0, 189, 338, 176),
            pygame.Rect(0, 365, 294, 451),
            pygame.Rect(0, 816, 39, 105),
            pygame.Rect(1245, 0, 136, 189),
            pygame.Rect(1298, 289, 83, 22),
            pygame.Rect(1245, 311, 136, 129),
            pygame.Rect(1216, 440, 165, 198),
            pygame.Rect(1245, 638, 136, 230),
            pygame.Rect(1298, 868, 83, 53),
            pygame.Rect(346, 403, 137, 214),
            pygame.Rect(388, 0, 857, 13),
            pygame.Rect(1053, 126, 117, 117),
            pygame.Rect(1054, 301, 115, 115),
            pygame.Rect(1034, 448, 155, 155),
            pygame.Rect(1053, 677, 117, 117)
        ]

        self.gotas_chuva = []
        for _ in range(100):
            x = random.randint(0, LARGURA)
            y = random.randint(-ALTURA, ALTURA)
            velocidade = random.randint(10, 15)
            self.gotas_chuva.append([x, y, velocidade])

        # A altura da água começa em 0 pixels (no fundo da tela)
        self.altura_agua = 0
        # Superfície especial necessária para desenhar formas transparentes (RGBA)
        self.superficie_agua = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

    def gerenciar_lixo_por_tempo(self):
        tempo_atual = pygame.time.get_ticks()

        if tempo_atual - self.tempo_ultimo_lixo > TEMPO_GERAR_LIXO:
            bueiro_escolhido = random.choice(POSICOES_BUEIROS)

            # gera variações para o lixo espalhar pelo bueiro (meio e bordas)
            variacao_x = random.randint(-40, 40)
            variacao_y = random.randint(-20, 20)

            posicao_x = bueiro_escolhido[0] - 15 + variacao_x
            posicao_y = bueiro_escolhido[1] - 15 + variacao_y

            novo_lixo = pygame.Rect(posicao_x, posicao_y, 30, 30)
            # add lixo na lista pra jogar essa lista como a quantidade de lixo
            self.lixos_no_chao.append(novo_lixo)

            self.tempo_ultimo_lixo = tempo_atual

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

    def atualizar_chuva(self):
        for gota in self.gotas_chuva:
            gota[1] += gota[2]
            # Se a gota bateu no chão da tela, volta pro topo em um X aleatório
            if gota[1] > ALTURA:
                gota[1] = random.randint(-20, -5)
                gota[0] = random.randint(0, LARGURA)

    def checar_colisoes(self, player):
        if not player.carregando_lixo:
            for lixo in self.lixos_no_chao[:]:
                if player.rect.colliderect(lixo):
                    self.lixos_no_chao.remove(lixo)
                    player.carregando_lixo = True
                    break

        # soltar lixp na lixeira Apertar ESPAÇO ou E
        if player.carregando_lixo:
            teclas = pygame.key.get_pressed()
            if player.rect.colliderect(self.lixeira_rect):
                if teclas[pygame.K_SPACE] or teclas[pygame.K_e]:
                    player.carregando_lixo = False
                    self.pontos += 1
                    # recompensa por limpar: escoa 60 pixels de água acumulada
                    self.altura_agua = max(0, self.altura_agua - 60)

        for bloco in self.construcoes:
            if player.rect.colliderect(bloco):
                player.voltar_posicao()

    def update(self, player):
        self.gerenciar_lixo_por_tempo()
        self.gerenciar_inundacao()
        self.atualizar_obstaculos(player)
        self.atualizar_chuva()
        self.checar_colisoes(player)

    def draw(self, superficie):
        # desenha o mapa de fundo
        superficie.blit(self.mapa, (0, 0))

        # desenha as gotas de chuva
        for gota in self.gotas_chuva:
            pygame.draw.line(superficie, COR_CHUVA, (gota[0], gota[1]), (gota[0], gota[1] + 12), 2)

        # desenha todos os lixos ativos espalhados pelo chão
        for lixo in self.lixos_no_chao:
            superficie.blit(self.imagem_lixo, (lixo.x, lixo.y))

        # desenha os retângulos obstáculos
        for obs in self.obstaculos:
            pygame.draw.rect(superficie, COR_OBSTACULO, obs[0])

        # desenha o mar de água azul transparente se houver inundação
        if self.altura_agua > 0:
            self.superficie_agua.fill((0, 0, 0, 0))  # Reseta frame anterior
            retangulo_agua = pygame.Rect(0, ALTURA - int(self.altura_agua), LARGURA, int(self.altura_agua))
            pygame.draw.rect(self.superficie_agua, COR_AGUA, retangulo_agua)
            superficie.blit(self.superficie_agua, (0, 0))

        # desenha a pontuação em preto no topo esquerdo (X=20, Y=20)
        texto_pontos = self.fonte.render(f"Pontos: {self.pontos}", True, COR_TEXTO)
        superficie.blit(texto_pontos, (20, 20))
