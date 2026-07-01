import os
import pygame
import sys
from src.settings import LARGURA, ALTURA, FPS
from src.player import Player
from src.world import World


class Jogo:
    def __init__(self):
        pygame.init()

        ## SONS DO JOGO
        pygame.mixer.init()
        print("mixer init:", pygame.mixer.get_init())

        self.caminho_audio = os.path.join("assets", "audio")

        self.musica_normal = os.path.join(self.caminho_audio, "fundo do jogo normal.mp3")
        self.som_derrota_arquivo = os.path.join(self.caminho_audio, "derrota.wav")
        self.som_cracha_arquivo = os.path.join(self.caminho_audio, "pegou-o-cracha-som-.wav")

        self.som_derrota = pygame.mixer.Sound(self.som_derrota_arquivo)
        self.som_cracha = pygame.mixer.Sound(self.som_cracha_arquivo)

        self.som_derrota.set_volume(0.8)
        self.som_cracha.set_volume(0.8)

        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Cincharca")
        self.relogio = pygame.time.Clock()
        self.rodando = True

        #criando estados
        # 0 = menu
        # 1 = jogando
        # 2 = game over
        # 3 = como jogar
        # 4 = descrição
        self.estado = 0

        self.player = Player()
        self.world = World(self.som_cracha)

        # fonte usada na tela de game over e menu
        self.fonte_titulo = pygame.font.SysFont(None, 54)
        self.fonte_score = pygame.font.SysFont(None, 40)
        self.fonte_menu = pygame.font.SysFont("Arial", 42, bold=True)

        # Fonte para o inventário
        self.fonte_hud = pygame.font.SysFont(None, 30)

        #Imagem do titulo top carregada.
        imagem_titulo_raw = pygame.image.load("assets/graphics/tela-menu/layout_titulo.png").convert_alpha()
        T_W_orig, T_H_orig = imagem_titulo_raw.get_size()
        ESCALA_TITULO = 0.5
        novo_w = int(T_W_orig * ESCALA_TITULO)
        novo_h = int(T_H_orig * ESCALA_TITULO)
        self.img_titulo = pygame.transform.smoothscale(imagem_titulo_raw, (novo_w, novo_h))

        #definição das posições e tamanhos dos retângulos dos botões do menu
        largura_botao = 300
        altura_botao = 55
        centro_x = LARGURA // 2 - (largura_botao // 2)

        self.rect_opcao_jogar = pygame.Rect(centro_x, ALTURA // 2 + 10, largura_botao, altura_botao)
        self.rect_opcao_como_jogar = pygame.Rect(centro_x, ALTURA // 2 + 85, largura_botao, altura_botao)
        self.rect_opcao_descricao = pygame.Rect(centro_x, ALTURA // 2 + 160, largura_botao, altura_botao)

        #guarda qual opção o mouse está em cima para fazer um efeito visual
        self.opcao_selecionada = -1

        #tela escura semi-transparente (reaproveitado o frame)
        self.overlay = pygame.Surface((LARGURA, ALTURA))
        self.overlay.set_alpha(190)
        self.overlay.fill((0, 0, 0))

        self.mostrar_texto = True
        self.tempo_piscar = pygame.time.get_ticks()

        # letreiro de Game Over
        imagem_letreiro_raw = pygame.image.load("assets/graphics/tela-game-over/letreiro_game_over.png").convert_alpha()
        LW_orig, LH_orig = imagem_letreiro_raw.get_size()
        ESCALA = 0.50
        let_w = int(LW_orig * ESCALA)
        let_h = int(LH_orig * ESCALA)
        self.img_letreiro = pygame.transform.smoothscale(imagem_letreiro_raw, (let_w, let_h))

        # botões "jogar novamente" e "sair" lado a lado
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

        #carrega as imagens das telas secundárias
        self.img_descricao = pygame.image.load("assets/graphics/tela-menu/DESCRIÇÃO.png").convert_alpha()
        self.img_como_jogar = pygame.image.load("assets/graphics/tela-menu/COMO_JOGAR.png").convert_alpha()

        # rects de clique dos botoes de game over
        self.rect_jogar = pygame.Rect(341, 521, 383, 60)
        self.rect_sair = pygame.Rect(753, 521, 184, 60)

    def rodar(self):
        while self.rodando:
            self.eventos()
            self.update()
            self.desenhar()
            self.relogio.tick(FPS)

        pygame.quit()
        sys.exit()

    def iniciar_partida(self):
        self.estado = 1
        pygame.mixer.music.load(self.musica_normal)
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)

    def eventos(self):
        pos_mouse = pygame.mouse.get_pos()

        if self.estado == 0:
            if self.rect_opcao_jogar.collidepoint(pos_mouse):
                self.opcao_selecionada = 0
            elif self.rect_opcao_como_jogar.collidepoint(pos_mouse):
                self.opcao_selecionada = 1
            elif self.rect_opcao_descricao.collidepoint(pos_mouse):
                self.opcao_selecionada = 2
            else:
                self.opcao_selecionada = -1

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                self.rodando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.estado == 0:
                    if self.rect_opcao_jogar.collidepoint(evento.pos):
                        self.iniciar_partida()
                    elif self.rect_opcao_como_jogar.collidepoint(evento.pos):
                        self.estado = 3
                    elif self.rect_opcao_descricao.collidepoint(evento.pos):
                        self.estado = 4
                elif self.estado in (3, 4):
                    self.estado = 0
                elif self.estado == 2:
                    if self.rect_jogar.collidepoint(evento.pos):
                        self.resetar_jogo()
                    elif self.rect_sair.collidepoint(evento.pos):
                        self.rodando = False

            if evento.type == pygame.KEYDOWN:
                if self.estado == 0:
                    if evento.key == pygame.K_SPACE:
                        self.iniciar_partida()
                elif self.estado in (3, 4):
                    if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_SPACE:
                        self.estado = 0

    def resetar_jogo(self):
        self.som_derrota.stop()
        pygame.mixer.music.stop()

        self.player = Player()
        self.world = World(self.som_cracha)

        self.iniciar_partida()

    def montar_blocos_colisao(self):
        blocos = []
        blocos.extend(self.world.construcoes)
        blocos.append(self.world.lixeira_rect)
        for obs in self.world.obstaculos:
            blocos.append(obs[0])
        return blocos

    def update(self):
        if self.estado in (0, 2, 3, 4):
            return

        nivel_agua = self.world.obter_nivel_agua_y()

        blocos_colisao = self.montar_blocos_colisao()
        self.player.update(nivel_agua, blocos_colisao)

        self.world.update(self.player)

        print(f"altura_agua={self.world.altura_agua:.1f} / ALTURA={ALTURA} / inundou={self.world.verificar_inundacao()}")  #DEBUG

        if self.world.verificar_inundacao():
            pygame.mixer.music.stop()
            self.som_derrota.stop()
            self.som_derrota.play()
            self.estado = 2

    def desenhar(self):
        if self.estado == 0:
            self.desenhar_menu()
            pygame.display.flip()
            return
        elif self.estado == 3:
            self.desenhar_como_jogar()
            pygame.display.flip()
            return
        elif self.estado == 4:
            self.desenhar_descricao()
            pygame.display.flip()
            return

        self.world.draw(self.tela, self.player)
        self.player.draw(self.tela)
        self.player.desenhar_hud(self.tela, self.fonte_hud)

        if self.estado == 2:
            self.desenhar_game_over()

        pygame.display.flip()

    def desenhar_game_over(self):
        self.tela.blit(self.overlay_game_over, (0, 0))

        self.tela.blit(self.img_letreiro, (self.img_x, self.img_y))

        w = self.world
        linhas = [
            f"Lixos coletados: {w.lixos_coletados}",
            f"Botas coletadas: {w.botas_coletadas}",
            f"Crachás coletados: {w.crachas_coletados}",
            f"Pontuação final: {self.player.get_pontuacao_total()}",
        ]

        for i, linha in enumerate(linhas):
            y = self.placar_y_inicio + i * 30 + (10 if i == 3 else 0)
            cor = (255, 255, 100) if i == 3 else (255, 255, 255)

            texto = self.fonte_score.render(linha, True, cor)
            rect = texto.get_rect(center=(LARGURA // 2, y))
            self.tela.blit(texto, rect)

        self.tela.blit(self.img_botoes, (self.botoes_x, self.botoes_y))

    def desenhar_menu(self):
        self.tela.blit(self.world.mapa, (0, 0))

        self.tela.blit(self.overlay, (0, 0))

        rect_titulo = self.img_titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 120))
        self.tela.blit(self.img_titulo, rect_titulo)

        opcoes = ["JOGAR", "COMO JOGAR", "DESCRIÇÃO"]
        retangulos = [self.rect_opcao_jogar, self.rect_opcao_como_jogar, self.rect_opcao_descricao]

        cor_ciano = (0, 240, 255)

        for idx, texto_opcao in enumerate(opcoes):
            rect = retangulos[idx]

            pygame.draw.rect(self.tela, (0, 0, 0), rect)
            pygame.draw.rect(self.tela, cor_ciano, rect, 3)

            cor_texto = cor_ciano if self.opcao_selecionada == idx else (255, 255, 255)

            texto_surface = self.fonte_menu.render(texto_opcao, True, cor_texto)
            texto_rect = texto_surface.get_rect(center=rect.center)

            self.tela.blit(texto_surface, texto_rect)

    def desenhar_como_jogar(self):
        self.tela.blit(self.img_como_jogar, (0, 0))

    def desenhar_descricao(self):
        self.tela.blit(self.img_descricao, (0, 0))


if __name__ == "__main__":
    jogo = Jogo()
    jogo.rodar()