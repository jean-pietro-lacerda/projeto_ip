import pygame
from src.settings import LARGURA, ALTURA, COR_JOGADOR

# --- CARREGAMENTO DOS SPRITES DO INVENTÁRIO ---
class Player:
    def __init__(self):
        self.raio = 20
        # so pro jogador ficar no centro da tela
        self.rect = pygame.Rect(LARGURA // 2, ALTURA // 2, self.raio * 2, self.raio * 2)
        self.velocidade_maxima = 6
        self.velocidade = 6

        # TAG False = mãos vazias | True = carregando lixo
        self.carregando_lixo = False
        self.tipo_coletavel_carregado = None
        # Guarda a posição do frame anterior para o sistema de colisão esbarrar
        self.pos_antiga_x = self.rect.x
        self.pos_antiga_y = self.rect.y

        # --- Atributos do Inventário integrados ---
        self.lixo = 0
        self.bota = 0
        self.cracha = 0
        self.pontuacao = 0

        #sprites dos itens coletaveis
        self.img_lixo = pygame.image.load("assets/graphics/itens/lixo.png").convert_alpha()
        self.img_bota = pygame.image.load("assets/graphics/itens/bota.png").convert_alpha()
        self.img_cracha = pygame.image.load("assets/graphics/itens/cracha.png").convert_alpha()

        self.img_lixo = pygame.transform.scale(self.img_lixo, (67, 67))
        self.img_bota = pygame.transform.scale(self.img_bota, (45, 45))
        self.img_cracha = pygame.transform.scale(self.img_cracha, (55, 55))

    def controle(self, nivel_agua, blocos_colisao):
        # Lógica da água (mantemos igual)
        if self.rect.bottom > nivel_agua:
            profundidade = self.rect.bottom - nivel_agua
            self.velocidade = max(2, self.velocidade_maxima - (profundidade / 100))
        else:
            self.velocidade = self.velocidade_maxima

        teclas = pygame.key.get_pressed()

        # Movimento e colisão no eixo X
        dx = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx = -self.velocidade
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx = self.velocidade
            
        self.rect.x += dx
        
        # Testa colisão horizontal com a lista de blocos
        for bloco in blocos_colisao:
            if self.rect.colliderect(bloco):
                # Se estava indo pra direita, gruda no lado esquerdo do bloco
                if dx > 0: 
                    self.rect.right = bloco.left
                # Se estava indo pra esquerda, gruda no lado direito do bloco
                elif dx < 0: 
                    self.rect.left = bloco.right

        # Movimento e colisao no eixo Y
        dy = 0
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            dy = -self.velocidade
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            dy = self.velocidade
            
        self.rect.y += dy
        
        # Testa colisão vertical com a lista de blocos
        for bloco in blocos_colisao:
            if self.rect.colliderect(bloco):
                # Se estava indo pra baixo, gruda no topo do bloco
                if dy > 0: 
                    self.rect.bottom = bloco.top
                # Se estava indo pra cima, gruda na base do bloco
                elif dy < 0: 
                    self.rect.top = bloco.bottom

    # somente pro jogador n sair da tela
    def limitar_tela(self):
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGURA: self.rect.right = LARGURA
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > ALTURA: self.rect.bottom = ALTURA

    def update(self, nivel_agua,blocos_colisao):
        self.controle(nivel_agua,blocos_colisao)
        self.limitar_tela()

    def draw(self, superficie):
        # desenhando o jogador
        pygame.draw.circle(superficie, COR_JOGADOR, self.rect.center, self.raio)

        # Se estiver carregando lixo, desenha uma bolinha verde em cima dele indicando o inventário cheio
        if self.carregando_lixo:
            pygame.draw.circle(superficie, (50, 255, 50), (self.rect.centerx, self.rect.top - 12), 6)

    def desenhar_hud(self, superficie, fonte):
        """Desenha o painel vertical de inventário fixo sobre o prédio esquerdo."""
        HUD_X = 22           
        HUD_Y = 110          
        LARGURA_HUD = 115    
        ALTURA_HUD = 290     
        TAMANHO_SLOT = 64    
        ESPACAMENTO = 16     

        # Fundo do HUD e Borda externa
        pygame.draw.rect(superficie, (220, 220, 220), (HUD_X, HUD_Y, LARGURA_HUD, ALTURA_HUD))
        pygame.draw.rect(superficie, (100, 100, 100), (HUD_X, HUD_Y, LARGURA_HUD, ALTURA_HUD), 2)

        # Lógica de exibição da Bota: 
        # Se pegou 0 ou 1, mostra 0 (some). Se pegou 2, mostra 1. Se pegou 3, mostra 2.
        qtd_bota_hud = self.bota - 1 if self.bota > 0 else 0

        # --- AJUSTADO AQUI: Agora usamos as imagens com self.img_ que carregamos no __init__ ---
        config_itens = [
            (self.lixo, self.img_lixo),      
            (qtd_bota_hud, self.img_bota),  
            (self.cracha, self.img_cracha)   
        ]
        posicao_y_atual = HUD_Y + ESPACAMENTO

        for qtd, sprite in config_itens:
            x_slot = HUD_X + (LARGURA_HUD - TAMANHO_SLOT) // 2
            rect_slot = pygame.Rect(x_slot, posicao_y_atual, TAMANHO_SLOT, TAMANHO_SLOT)
            
            # Desenha o quadrado do slot (sempre visível)
            pygame.draw.rect(superficie, (100, 100, 100), rect_slot, 2) 

            # Condição: O item e a quantidade só aparecem se forem coletados
            if qtd > 0:
                x_sprite = rect_slot.centerx - (sprite.get_width() // 2)
                y_sprite = rect_slot.centery - (sprite.get_height() // 2)
                superficie.blit(sprite, (x_sprite, y_sprite))

                # Texto da quantidade com a cor preta padrão
                texto_qtd = fonte.render(f"x{qtd}", True, (0, 0, 0))
                superficie.blit(texto_qtd, (rect_slot.right - 24, rect_slot.bottom - 18))

            posicao_y_atual += TAMANHO_SLOT + ESPACAMENTO
    # --- MÉTODOS DO INVENTÁRIO ---

    def coletar_lixo(self):
        """Coleta o lixo normalmente (1 por vez)."""
        self.lixo += 1
        self.carregando_lixo = True # Apenas o lixo ativa a bolinha verde

    def coletar_bota(self):
        """1ª Bota = Velocidade (invisível no HUD). 2ª em diante = Inventário + Pontos."""
        self.bota += 1
        if self.bota == 1:
            self.velocidade_maxima *= 1.2 # Fica mais rápido, mas não aparece no inventário
        else:
            # Entra no inventário e já dá pontos diretos (ex: +3 pontos.)
            self.pontuacao += 3
        
        return True # Sempre some do mapa ao passar por cima

    def coletar_cracha(self):
        """Aumenta o multiplicador de pontuação e aparece no inventário."""
        self.cracha += 1
        return True # Sempre some do mapa ao passar por cima

    def descartar_lixo(self):
        """Descarta o lixo na lixeira."""
        if self.lixo > 0:
            self.pontuacao += self.lixo
            self.lixo = 0
            self.carregando_lixo = False
            return True
        return False
        
    def get_pontuacao_total(self):
        """Calcula a pontuação real aplicando os multiplicadores dos crachás."""
        if self.cracha > 0:
            # Multiplica por 2 elevado à quantidade de crachás (ex: 2 crachás = x4)
            return self.pontuacao * (2 ** self.cracha)
        return self.pontuacao