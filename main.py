import pygame
import sys
from src.settings import LARGURA, ALTURA, FPS
from src.player import Player
from src.world import World


class Jogo:
    def __init__(self):
        pygame.init()
        # define o tamanho correto da janela (1280x720)
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Eco-Gincana: Limpando os Bueiros")
        self.relogio = pygame.time.Clock()
        self.rodando = True

        #criando estados
        # 1 = jogando ; 2 = game over
        self.estado = 1

        self.player = Player()
        self.world = World()

        # fonte usada na tela de game over
        self.fonte_titulo = pygame.font.SysFont(None, 64)
        self.fonte_score = pygame.font.SysFont(None, 40)

        #tela escura semi-transparente (reaproveitado o frame)
        self.overlay = pygame.Surface((LARGURA, ALTURA))
        self.overlay.set_alpha(160)  # 0 = invisível, 255 = opaco
        self.overlay.fill((0, 0, 0))

    def rodar(self):
        while self.rodando:
            self.eventos()
            self.update()
            self.desenhar()
            self.relogio.tick(FPS)

        pygame.quit()
        sys.exit()

    def eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False

    def update(self):
        # se já é game over, trava os comandos: não atualiza mais nada
        if self.estado == 2:
            return

        # pede ao mundo a linha Y de onde a água se encontra no momento
        nivel_agua = self.world.obter_nivel_agua_y()

        # atualiza o jogador passando a água para ele regular sua velocidade
        self.player.update(nivel_agua)

        # atualiza o mundo (bueiros, lixos, obstáculos e chuva)
        self.world.update(self.player)

        print(f"altura_agua={self.world.altura_agua:.1f} / ALTURA={ALTURA} / inundou={self.world.verificar_inundacao()}")  # DEBUG

         # checa o exato momento em que a inundação atinge o limite
        if self.world.verificar_inundacao():
            self.estado = 2  # muda para game Over

    def desenhar(self):
        # O world.draw desenha primeiro o mapa de fundo, chuva, lixos, obstáculos e o mar de água
        self.world.draw(self.tela)

        # O jogador desenha a bolinha dele por cima de tudo para não ser "engolido" pelo fundo
        self.player.draw(self.tela)

        if self.estado == 2:
            self.desenhar_game_over()

        pygame.display.flip()

    def desenhar_game_over(self):
        # escurece a tela
        self.tela.blit(self.overlay, (0, 0))

        # mensagem principal
        texto_titulo = self.fonte_titulo.render(
            "Game Over: O CIn Inundou!", True, (255, 255, 255)
        )
        rect_titulo = texto_titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 40))
        self.tela.blit(texto_titulo, rect_titulo)

        # placar final
        texto_score = self.fonte_score.render(
            f"Lixos recolhidos: {self.world.pontos}", True, (255, 255, 255)
        )
        rect_score = texto_score.get_rect(center=(LARGURA // 2, ALTURA // 2 + 20))
        self.tela.blit(texto_score, rect_score)

if __name__ == "__main__":
    jogo = Jogo()
    jogo.rodar()