import pygame
from src.settings import LARGURA, ALTURA, COR_JOGADOR

class Player:
    def __init__(self):
        self.raio = 20
        # so pro jogador ficar no centro da tela
        self.rect = pygame.Rect(LARGURA // 2, ALTURA // 2, self.raio * 2, self.raio * 2)
        self.velocidade_maxima = 6
        self.velocidade = 6

        # TAG False = mãos vazias | True = carregando lixo
        self.carregando_lixo = False

        # Guarda a posição do frame anterior para o sistema de colisão esbarrar
        self.pos_antiga_x = self.rect.x
        self.pos_antiga_y = self.rect.y

        # --- Atributos do Inventário integrados ---
        self.lixo = 0
        self.bota = 0
        self.cracha = 0
        self.pontuacao = 0

    def controle(self, nivel_agua):
        # salva a posição antes de aplicar o movimento do teclado
        self.pos_antiga_x = self.rect.x
        self.pos_antiga_y = self.rect.y

        # se a água subir além da posição Y atual do jogador, ele reduz a velocidade proporcionalmente
        if self.rect.bottom > nivel_agua:
            # Quanto mais fundo mais lento
            profundidade = self.rect.bottom - nivel_agua
            # a menor velocidade possivel é dois pra não tarvar totalemnte o personagemm
            self.velocidade = max(2, self.velocidade_maxima - (profundidade / 100))
        else:
            self.velocidade = self.velocidade_maxima

        teclas = pygame.key.get_pressed()

        # movimentação baica ou wasd ou setas
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.rect.x -= self.velocidade
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.rect.x += self.velocidade
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.rect.y -= self.velocidade
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.rect.y += self.velocidade

    def voltar_posicao(self):
        # colidiu volta o movimento e para ele
        self.rect.x = self.pos_antiga_x
        self.rect.y = self.pos_antiga_y

    # somente pro jogador n sair da tela
    def limitar_tela(self):
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGURA: self.rect.right = LARGURA
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > ALTURA: self.rect.bottom = ALTURA

    def update(self, nivel_agua):
        self.controle(nivel_agua)
        self.limitar_tela()

    def draw(self, superficie):
        # desenhando o jogador
        pygame.draw.circle(superficie, COR_JOGADOR, self.rect.center, self.raio)

        # Se estiver carregando lixo, desenha uma bolinha verde em cima dele indicando o inventário cheio
        if self.carregando_lixo:
            pygame.draw.circle(superficie, (50, 255, 50), (self.rect.centerx, self.rect.top - 12), 6)


    # ==========================================
    # --- MÉTODOS DO INVENTÁRIO INTEGRADOS ---
    # ==========================================

    def coletar_lixo(self):
        """O crachá define se pega 1 ou 2 lixos por vez."""
        if self.cracha == 1:
            self.lixo += 2
        else:
            self.lixo += 1
            
        self.carregando_lixo = True # Atualiza a bolinha verde automaticamente

    def coletar_bota(self):
        """Se for a 1ª bota, aumenta a velocidade máxima."""
        if self.bota == 0:
            self.bota = 1
            self.velocidade_maxima *= 1.2 # Deixa o jogador mais rápido!
            return True 
        else:
            # Se já tem a bota, converte a nova bota em 3 lixos automaticamente
            self.lixo += 3
            self.carregando_lixo = True
            return False

    def coletar_cracha(self):
        """Se for o 1º crachá, libera a coleta dupla."""
        if self.cracha == 0:
            self.cracha = 1
            return True
        else:
            # Se já tem o crachá, converte o novo em 5 lixos automaticamente
            self.lixo += 5
            self.carregando_lixo = True
            return False

    def descartar_lixo(self):
        """Chame quando o jogador encostar na lixeira."""
        if self.lixo > 0:
            self.pontuacao += self.lixo
            self.lixo = 0 # Zera o lixo da mão do jogador
            self.carregando_lixo = False # Tira a bolinha verde automaticamente
            return True
        return False

    def pegar_texto_hud(self):
        """Retorna os dados no formato certinho para a tela."""
        return f"Lixos na Mão: {self.lixo} | Bota: {self.bota}/1 | Crachá: {self.cracha}/1 | Pontos: {self.pontuacao}"