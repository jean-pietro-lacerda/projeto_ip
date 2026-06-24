import pygame
import random
from src.settings import (POSICOES_BUEIROS, LIXEIRA_RECT, TEMPO_GERAR_LIXO,
                          LARGURA, ALTURA, COR_OBSTACULO, COR_TEXTO, COR_CHUVA, COR_AGUA)


# Lista de coletáveis possíveis e seus pesos (chance relativa de aparecer)
# "lixo" tem 70% de chance, "bota" 20%, "cracha" 10% (somando 100, mas não precisa ser exato)
COLETAVEIS = [
    ("lixo", 70),
    ("bota", 20),
    ("cracha", 10)
]


def gerar_coletavel():
    """Sorteia e retorna o nome de um coletável, respeitando os pesos definidos em COLETAVEIS."""
    nomes = [c[0] for c in COLETAVEIS]
    pesos = [c[1] for c in COLETAVEIS]
    return random.choices(nomes, weights=pesos)[0]


class World:
    def __init__(self):
        #  pegando as imagens e colocando na altura e largura certa
        self.mapa = pygame.image.load("assets/graphics/mapa.png")
        self.mapa = pygame.transform.scale(self.mapa, (LARGURA, ALTURA))

        # Carrega a imagem de cada tipo de coletável e guarda em um dicionário
        # assim fica fácil pegar a imagem certa na hora de desenhar: self.imagens_coletaveis["lixo"]
        self.imagens_coletaveis = {
            "lixo": pygame.image.load("assets/graphics/lixo.png"),
            "bota": pygame.image.load("assets/graphics/bota.png"),
            "cracha": pygame.image.load("assets/graphics/cracha.png"),
        }
        for nome in self.imagens_coletaveis:
            self.imagens_coletaveis[nome] = pygame.transform.scale(self.imagens_coletaveis[nome], (30, 30))

        self.lixeira_rect = pygame.Rect(LIXEIRA_RECT)

        # Cada item da lista agora é [rect, tipo] em vez de só o rect,
        # pra sabermos qual imagem desenhar e qual coletável foi pego
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

            # gera variações para o coletável espalhar pelo bueiro (meio e bordas)
            variacao_x = random.randint(-40, 40)
            variacao_y = random.randint(-20, 20)

            posicao_x = bueiro_escolhido[0] - 15 + variacao_x
            posicao_y = bueiro_escolhido[1] - 15 + variacao_y

            # sorteia qual tipo de coletável vai aparecer (lixo, bota ou cracha)
            tipo_coletavel = gerar_coletavel()

            novo_rect = pygame.Rect(posicao_x, posicao_y, 30, 30)
            # add coletável na lista junto com o tipo sorteado
            self.lixos_no_chao.append([novo_rect, tipo_coletavel])

            self.tempo_ultimo_lixo = tempo_atual

    def gerenciar_inundacao(self):
        # quantidade de coletáveis atualmente no chão entupindo os canos
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
            for item in self.lixos_no_chao[:]:
                rect, tipo = item
                if player.rect.colliderect(rect):
                    self.lixos_no_chao.remove(item)
                    player.carregando_lixo = True
                    # guarda qual tipo de coletável o player está carregando agora
                    player.tipo_coletavel_carregado = tipo
                    break

        # soltar coletável na lixeira Apertar ESPAÇO ou E
        if player.carregando_lixo:
            teclas = pygame.key.get_pressed()
            if player.rect.colliderect(self.lixeira_rect):
                if teclas[pygame.K_SPACE] or teclas[pygame.K_e]:
                    player.carregando_lixo = False
                    self.pontos += 1
                    # recompensa por limpar: escoa 60 pixels de água acumulada
                    self.altura_agua = max(0, self.altura_agua - 60)

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

        # desenha todos os coletáveis ativos espalhados pelo chão, usando a imagem certa pra cada tipo
        for rect, tipo in self.lixos_no_chao:
            imagem = self.imagens_coletaveis[tipo]
            superficie.blit(imagem, (rect.x, rect.y))

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
        texto_pontos = self.fonte.render(f"Pontos: {self.pontos}", True, COR_TEXTO)
        superficie.blit(texto_pontos, (20, 20))