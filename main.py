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
        pygame.display.set_caption("Cincharca")
        self.relogio = pygame.time.Clock()
        self.rodando = True

        #criando estados
        # 0 = menu
        # 1 = jogando
        # 2 = game over
        self.estado = 0

        self.player = Player()
        self.world = World()

        # fonte usada na tela de game over
        self.fonte_titulo = pygame.font.SysFont(None, 54)
        self.fonte_score = pygame.font.SysFont(None, 40)
        self.fonte_menu = pygame.font.SysFont(None, 48)

        #tela escura semi-transparente (reaproveitado o frame)
        self.overlay = pygame.Surface((LARGURA, ALTURA))
        self.overlay.set_alpha(190)  # 0 = invisível, 255 = opaco
        self.overlay.fill((0, 0, 0))
        #controla o piscar da mensagem "Pressione ESPAÇO", para da aquele inicio de jogo mais dinâmico.
        self.mostrar_texto = True
        # guarda o momento em que o texto piscou pela última vez
        self.tempo_piscar = pygame.time.get_ticks()

        # letreiro de Game Over — arquivo: assets/graphics/letreiro_game_over.png
        imagem_letreiro_raw = pygame.image.load("assets/graphics/tela-game-over/letreiro_game_over.png").convert_alpha()
        LW_orig, LH_orig = imagem_letreiro_raw.get_size()
        ESCALA = 0.50
        let_w = int(LW_orig * ESCALA)
        let_h = int(LH_orig * ESCALA)
        self.img_letreiro = pygame.transform.smoothscale(imagem_letreiro_raw, (let_w, let_h))

        # botões "jogar novamente" e "sair" lado a lado — arquivo: assets/graphics/botoes_sair_e_jgr_novamente.png
        imagem_botoes_raw = pygame.image.load("assets/graphics/tela-game-over/botoes_sair_e_jgr_novamente.png").convert_alpha()
        BW_orig, BH_orig = imagem_botoes_raw.get_size()
        bot_w = int(BW_orig * ESCALA)
        bot_h = int(BH_orig * ESCALA)
        self.img_botoes = pygame.transform.smoothscale(imagem_botoes_raw, (bot_w, bot_h))

        # espaço reservado para o placar entre o letreiro e os botões
        ESPACO_PLACAR = 130

        # bloco inteiro (letreiro + placar + botões) centralizado verticalmente na tela
        bloco_total_h = let_h + ESPACO_PLACAR + bot_h
        y_topo = (ALTURA - bloco_total_h) // 2

        self.img_x = (LARGURA - let_w) // 2
        self.img_y = y_topo

        self.placar_y_inicio = self.img_y + let_h + 10

        self.botoes_x = (LARGURA - bot_w) // 2
        self.botoes_y = self.placar_y_inicio + ESPACO_PLACAR - 20

        # overlay azul-escuro para o game over (separado do overlay do menu)
        self.overlay_game_over = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self.overlay_game_over.fill((5, 25, 50, 200))

        # rects de clique dos botoes (calculados a partir da posição final dos botões na tela)
        self.rect_jogar = pygame.Rect(341, 521, 383, 60)
        self.rect_sair  = pygame.Rect(753, 521, 184, 60)

    def rodar(self):
        while self.rodando:
            self.eventos()
            self.update()
            self.desenhar()
            self.relogio.tick(FPS)

        pygame.quit()
        sys.exit()

    def eventos(self):
        #percorre todos os eventos que aconteceram desde o último frame
        for evento in pygame.event.get():

            #se o jogador clicar no X da janela, fecha o jogo
            if evento.type == pygame.QUIT:
                self.rodando = False

            #verifica se alguma tecla foi pressionada
            if evento.type == pygame.KEYDOWN:

                #se estivermos na tela de menu...
                if self.estado == 0:

                    #...e a tecla pressionada for ESPAÇO,
                    #muda o estado para "jogando"
                    if evento.key == pygame.K_SPACE:
                        self.estado = 1

             # checa cliques apenas quando a tela de game over estiver ativa
            if self.estado == 2 and evento.type == pygame.MOUSEBUTTONDOWN:
                if self.rect_jogar.collidepoint(evento.pos):
                    self.resetar_jogo()
                elif self.rect_sair.collidepoint(evento.pos):
                    self.rodando = False

    def resetar_jogo(self):
    # recria player e world do zero (água, pontos e posição voltam ao início)
        self.player = Player()
        self.world  = World()
        self.estado = 1


    def update(self):

        #menu: aqui eu congelo o jogo.
        if self.estado == 0:
            return

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
        #self.world.draw(self.tela)
        # O jogador desenha a bolinha dele por cima de tudo para não ser "engolido" pelo fundo
        #self.player.draw(self.tela)
        if self.estado == 0:
            self.desenhar_menu()
            pygame.display.flip()
            return

        self.world.draw(self.tela, self.player)
        self.player.draw(self.tela)

        if self.estado == 2:
            self.desenhar_game_over()

        pygame.display.flip()

    def desenhar_game_over(self):
        # overlay azul-escuro cobre o jogo por baixo
        self.tela.blit(self.overlay_game_over, (0, 0))

        # letreiro (imagem centralizada, com fundo transparente)
        self.tela.blit(self.img_letreiro, (self.img_x, self.img_y))

        # placar detalhado — exibido entre o letreiro e os botões
        w = self.world
        linhas = [
            f"Lixos coletados: {w.lixos_coletados}",
            f"Botas coletadas: {w.botas_coletadas}",
            f"Crachás coletados: {w.crachas_coletados}",
            f"Pontuação final: {self.player.get_pontuacao_total()}",
        ]

        for i, linha in enumerate(linhas):
            y = self.placar_y_inicio + i * 30 + (10 if i == 3 else 0)  # espaço extra antes da pontuação
            cor = (255, 255, 100) if i == 3 else (255, 255, 255)  # amarelo para pontuação final

            texto = self.fonte_score.render(linha, True, cor)
            rect = texto.get_rect(center=(LARGURA // 2, y))
            self.tela.blit(texto, rect)

        # botões "jogar novamente" e "sair" lado a lado, abaixo do placar
        self.tela.blit(self.img_botoes, (self.botoes_x, self.botoes_y))

    def desenhar_menu(self):
        #utilizei o selg.world.mapa pq o world já carrega o mapa na memória. Então, não precisa carregar o mapa novamente.
        #desenha apenas o mapa
        self.tela.blit(self.world.mapa, (0, 0))

        #escurece um pouco o fundo
        self.tela.blit(self.overlay, (0, 0))

        #TÍTULO DO MENU
        #Cria a sombra do título.
        #A ideia é desenhar exatamente o mesmo texto, porém alguns pixels
        #deslocado para a direita e para baixo. Isso cria um efeito de profundidade.
        titulo_sombra = self.fonte_titulo.render(
            "Cincharca",
            True,
            (0, 0, 0)
        )

        #primeiro posicionamos a sombra exatamente onde ficará o título.
        rect_sombra = titulo_sombra.get_rect(
            center=(LARGURA // 2, ALTURA // 2 - 90)
        )

        #depois deslocamos 3 pixels para a direita e 3 pixels para baixo.
        #o método move_ip() altera o próprio retângulo ("in place").
        rect_sombra.move_ip(3, 3)

        #desenha a sombra.
        self.tela.blit(titulo_sombra, rect_sombra)

        #agora desenhamos o título principal exatamente na posição correta.
        titulo = self.fonte_titulo.render(
            "Cincharca",
            True,
            (255, 255, 255)
        )

        rect_titulo = titulo.get_rect(
            center=(LARGURA // 2, ALTURA // 2 - 90)
        )

        #O título branco fica por cima da sombra.
        self.tela.blit(titulo, rect_titulo)
        #DEIXO ABAIXO COMO ESTAVA ANTES, CASO QUEIRA VOLTAR. MAS ACHO QUE FICOU MELHOR COM A SOMBRA.
        # """#título
        # titulo = self.fonte_titulo.render(
        #     "Cincharca",
        #     True,
        #     (255, 255, 255)
        # )

        # rect_titulo = titulo.get_rect(
        #     center=(LARGURA // 2, ALTURA // 2 - 90)
        # )

        # self.tela.blit(titulo, rect_titulo)"""

        #aqui faz o texto piscar a cada 500 milissegundos.
        tempo_atual = pygame.time.get_ticks()

        if tempo_atual - self.tempo_piscar > 500:
            self.mostrar_texto = not self.mostrar_texto
            self.tempo_piscar = tempo_atual

        #MENSAGEM PARA INICIAR
        # A variável self.mostrar_texto é alternada entre True e False a cada 500 ms.
        # Assim, a mensagem aparece e desaparece, criando o clássico efeito de "piscar" utilizado em menus.
        if self.mostrar_texto:
            texto = self.fonte_menu.render(
                "Pressione ESPAÇO para iniciar",
                True,
                (255, 255, 255)
            )

            rect = texto.get_rect(
                center=(LARGURA // 2, ALTURA // 2 + 10)
            )

            self.tela.blit(texto, rect)


if __name__ == "__main__":
    jogo = Jogo()
    jogo.rodar()