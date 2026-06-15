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

        self.player = Player()
        self.world = World()

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
        # pede ao mundo a linha Y de onde a água se encontra no momento
        nivel_agua = self.world.obter_nivel_agua_y()

        # atualiza o jogador passando a água para ele regular sua velocidade
        self.player.update(nivel_agua)

        # atualiza o mundo (bueiros, lixos, obstáculos e chuva)
        self.world.update(self.player)

    def desenhar(self):
        # O world.draw desenha primeiro o mapa de fundo, chuva, lixos, obstáculos e o mar de água
        self.world.draw(self.tela)

        # O player desenha a bolinha dele por cima de tudo para não ser "engolido" pelo fundo
        self.player.draw(self.tela)

        pygame.display.flip()


if __name__ == "__main__":
    jogo = Jogo()
    jogo.rodar()