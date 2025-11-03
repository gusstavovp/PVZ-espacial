import pygame
import sys
import random
# Importações de Mecanicas
from scripts.Mecanicas import projetil, particulas, Energia 
# Importações de Torres e Inimigos
from scripts.Inimigos import Inimigo
from scripts.Torres import TorreBase, Peashooter, NozObstaculo, Girassol, CerejaBomba


class Game:
    
    def get_cell_center(self, row, col):
        """ Retorna a posição central de uma célula (para posicionar sprites). """
        x = self.GRID_OFFSET_X + col * self.CELL_WIDTH + self.CELL_WIDTH // 2
        y = self.GRID_OFFSET_Y + row * self.CELL_HEIGHT + self.CELL_HEIGHT // 2
        return (x, y)

    def get_cell_coords(self, mouse_pos):
        """ Retorna a linha (row) e coluna (col) do grid a partir da posição do mouse (pixel). """
        mx, my = mouse_pos
        
        end_x = self.GRID_OFFSET_X + self.GRID_COLS * self.CELL_WIDTH
        end_y = self.GRID_OFFSET_Y + self.GRID_ROWS * self.CELL_HEIGHT
        
        if mx < self.GRID_OFFSET_X or mx >= end_x or my < self.GRID_OFFSET_Y or my >= end_y:
            return None, None # Fora da área
        
        col = (mx - self.GRID_OFFSET_X) // self.CELL_WIDTH
        row = (my - self.GRID_OFFSET_Y) // self.CELL_HEIGHT
        
        return int(row), int(col)

    def criar_particulas(self, pos, cor, num_particulas=10, velocidade_max=2, vida_max=30, gravidade=True, tamanho_min=2, tamanho_max=5):
        for _ in range(num_particulas):
            self.lista_particulas.append(
                particulas(
                    pos=list(pos), # Garante que seja uma lista
                    velocidade=[random.uniform(-velocidade_max, velocidade_max), random.uniform(-velocidade_max, velocidade_max)],
                    vida=random.randint(vida_max // 2, vida_max),
                    cor=cor,
                    tamanho=random.randint(tamanho_min, tamanho_max),
                    gravidade=gravidade
                )
            )

    def draw_grid(self):
        """ Desenha as linhas do grid para visualização. """
        LINE_COLOR = (50, 50, 50) 
        
        for row in range(self.GRID_ROWS + 1):
            start_pos = (self.GRID_OFFSET_X, self.GRID_OFFSET_Y + row * self.CELL_HEIGHT)
            end_pos = (self.GRID_OFFSET_X + self.GRID_COLS * self.CELL_WIDTH, self.GRID_OFFSET_Y + row * self.CELL_HEIGHT)
            pygame.draw.line(self.window, LINE_COLOR, start_pos, end_pos)
            
        for col in range(self.GRID_COLS + 1):
            start_pos = (self.GRID_OFFSET_X + col * self.CELL_WIDTH, self.GRID_OFFSET_Y)
            end_pos = (self.GRID_OFFSET_X + col * self.CELL_WIDTH, self.GRID_OFFSET_Y + self.GRID_ROWS * self.CELL_HEIGHT)
            pygame.draw.line(self.window, LINE_COLOR, start_pos, end_pos)

        OCCUPIED_COLOR = (0, 100, 0)
        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                if self.grid[row][col] is not None:
                    rect_x = self.GRID_OFFSET_X + col * self.CELL_WIDTH
                    rect_y = self.GRID_OFFSET_Y + row * self.CELL_HEIGHT
                    pygame.draw.rect(self.window, OCCUPIED_COLOR, (rect_x, rect_y, self.CELL_WIDTH, self.CELL_HEIGHT), 1) 
    
    def __init__(self):
        
        pygame.init()
        
        self.window = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("PROJETO INTEGRADO: Teste de Mecânicas")
        
        self.clock = pygame.time.Clock()
        
        self.assets = {
            "projetil": {
                "proje": pygame.image.load("data/images/projetil/proje.png")
            },
            "Energia": pygame.image.load("data/images/Energia.png"), 
            "torre": {
                "peashooter": pygame.image.load("data/images/torres/peashooter.png"),
                "noz": pygame.image.load("data/images/torres/noz.png"),
                "girassol": pygame.image.load("data/images/torres/girassol.png"),
                "cereja": pygame.image.load("data/images/torres/cereja.png")  # ADICIONE A IMAGEM
            },
            
            "inimigo": {
                "basico": pygame.image.load("data/images/inimigos/basico.png") 
            }
        }

        self.projeteis = []
        self.lista_particulas = []
        self.torres = [] 
        self.inimigos = []
        self.energias_caindo = [] 
        
        self.GRID_ROWS = 6  
        self.GRID_COLS = 9  
        self.CELL_WIDTH = 65  
        self.CELL_HEIGHT = 80 
        self.GRID_OFFSET_X = 50 
        self.GRID_OFFSET_Y = 100 

        self.grid = [[None for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]

        self.inimigo_spawn_timer = 180 
        self.energia_spawn_timer = 300 
        self.total_energia = 50  # CORRIGIDO: Inicia com 50 de energia
        
    def run(self):
        
        running = True
        
        while running:
            
            self.window.fill((0, 0, 0))
            
            # ------------------------------------
            # 1. SPAWN DE INIMIGOS
            # ------------------------------------
            self.inimigo_spawn_timer -= 1
            if self.inimigo_spawn_timer <= 0:
                self.inimigo_spawn_timer = random.randint(300, 540)
                
                row = random.randint(0, self.GRID_ROWS - 1)
                
                center_y = self.get_cell_center(row, self.GRID_COLS - 1)[1]
                
                spawn_x = self.window.get_width() + 20 
                inimigo_y = center_y - self.assets["inimigo"]["basico"].get_height() // 2
                
                novo_inimigo = Inimigo(
                    jogo=self, 
                    tipo="basico",
                    pos=(spawn_x, inimigo_y),
                    vida=10, 
                    velocidade=random.uniform(0.1, 0.4), 
                    dano=0.5
                )
                self.inimigos.append(novo_inimigo)
                
                particula_spawn_x = self.GRID_OFFSET_X + self.GRID_COLS * self.CELL_WIDTH - 10
                particula_spawn_y = center_y
                
                self.criar_particulas(
                    pos=(particula_spawn_x, particula_spawn_y), 
                    cor=(139, 69, 19),
                    num_particulas=15, 
                    velocidade_max=1.0, 
                    vida_max=40, 
                    gravidade=True
                )
                
            # ------------------------------------
            # 1B. SPAWN DE ENERGIA (MOEDA)
            # ------------------------------------
            self.energia_spawn_timer -= 1
            if self.energia_spawn_timer <= 0:
                self.energia_spawn_timer = random.randint(300, 450) 
                
                spawn_x = random.randint(self.GRID_OFFSET_X, self.GRID_OFFSET_X + self.GRID_COLS * self.CELL_WIDTH - 30)
                
                nova_energia = Energia(
                    jogo=self, 
                    pos=(spawn_x, 0), 
                    velocidade=[0, random.uniform(0.5, 1.0)], 
                    valor=25, 
                    vida=480 
                )
                self.energias_caindo.append(nova_energia)


            # ------------------------------------
            # 2. EVENTOS (COLOCAR TORRES E COLETAR ENERGIA)
            # ------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

                # PEASHOOTER - Botão Direito
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: 
                    mouse_pos = event.pos
                    row, col = self.get_cell_coords(mouse_pos)
                    
                    custo_torre = Peashooter.CUSTO_ENERGIA 
                    
                    if row is not None and col is not None:
                        if self.total_energia >= custo_torre:
                            if self.grid[row][col] is None:
                                
                                center_x, center_y = self.get_cell_center(row, col)
                                
                                torre_x = center_x - self.assets["torre"]["peashooter"].get_width() // 2
                                torre_y = center_y - self.assets["torre"]["peashooter"].get_height() // 2
                                
                                nova_torre = Peashooter(jogo=self, pos=(torre_x, torre_y), grid_pos=(row, col))
                                
                                self.total_energia -= custo_torre
                                self.torres.append(nova_torre)
                                self.grid[row][col] = nova_torre
                                
                                self.criar_particulas(
                                    pos=nova_torre.rect().center, 
                                    cor=(0, 200, 0), 
                                    num_particulas=15, 
                                    gravidade=False,
                                    vida_max=40
                                )
                            else:
                                print(f"Célula ({row}, {col}) já ocupada.")
                        else:
                             print(f"Energia insuficiente! Necessário: {custo_torre}, Atual: {self.total_energia}")
                    
                # NOZ - Botão do Meio
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                    mouse_pos = event.pos
                    row, col = self.get_cell_coords(mouse_pos)
                    
                    custo_torre = NozObstaculo.CUSTO_ENERGIA 
                    
                    if row is not None and col is not None:
                        if self.total_energia >= custo_torre:
                            if self.grid[row][col] is None:
                                
                                center_x, center_y = self.get_cell_center(row, col)
                                
                                torre_x = center_x - self.assets["torre"]["noz"].get_width() // 2
                                torre_y = center_y - self.assets["torre"]["noz"].get_height() // 2
                                
                                nova_torre = NozObstaculo(jogo=self, pos=(torre_x, torre_y), grid_pos=(row, col))
                                
                                self.total_energia -= custo_torre
                                self.torres.append(nova_torre)
                                self.grid[row][col] = nova_torre
                                
                                self.criar_particulas(
                                    pos=nova_torre.rect().center, 
                                    cor=(139, 69, 19),
                                    num_particulas=15, 
                                    gravidade=False,
                                    vida_max=40
                                )
                            else:
                                print(f"Célula ({row}, {col}) já ocupada.")
                        else:
                             print(f"Energia insuficiente! Necessário: {custo_torre}, Atual: {self.total_energia}")
                
                # GIRASSOL - Tecla 'G' ou Botão 4 (se tiver)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                    mouse_pos = pygame.mouse.get_pos()
                    row, col = self.get_cell_coords(mouse_pos)
                    
                    custo_torre = Girassol.CUSTO_ENERGIA 
                    
                    if row is not None and col is not None:
                        if self.total_energia >= custo_torre:
                            if self.grid[row][col] is None:
                                
                                center_x, center_y = self.get_cell_center(row, col)
                                
                                torre_x = center_x - self.assets["torre"]["girassol"].get_width() // 2
                                torre_y = center_y - self.assets["torre"]["girassol"].get_height() // 2
                                
                                nova_torre = Girassol(jogo=self, pos=(torre_x, torre_y), grid_pos=(row, col))
                                
                                self.total_energia -= custo_torre
                                self.torres.append(nova_torre)
                                self.grid[row][col] = nova_torre
                                
                                self.criar_particulas(
                                    pos=nova_torre.rect().center, 
                                    cor=(255, 215, 0),  # Dourado
                                    num_particulas=20, 
                                    gravidade=False,
                                    vida_max=40
                                )
                                print(f"Girassol plantado! Energia: {self.total_energia}")
                            else:
                                print(f"Célula ({row}, {col}) já ocupada.")
                        else:
                             print(f"Energia insuficiente! Necessário: {custo_torre}, Atual: {self.total_energia}")
                
                # CEREJA-BOMBA - Tecla 'C'
                if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                    mouse_pos = pygame.mouse.get_pos()
                    row, col = self.get_cell_coords(mouse_pos)
                    
                    custo_torre = CerejaBomba.CUSTO_ENERGIA 
                    
                    if row is not None and col is not None:
                        if self.total_energia >= custo_torre:
                            if self.grid[row][col] is None:
                                
                                center_x, center_y = self.get_cell_center(row, col)
                                
                                torre_x = center_x - self.assets["torre"]["cereja"].get_width() // 2
                                torre_y = center_y - self.assets["torre"]["cereja"].get_height() // 2
                                
                                nova_torre = CerejaBomba(jogo=self, pos=(torre_x, torre_y), grid_pos=(row, col))
                                
                                self.total_energia -= custo_torre
                                self.torres.append(nova_torre)
                                self.grid[row][col] = nova_torre
                                
                                self.criar_particulas(
                                    pos=nova_torre.rect().center, 
                                    cor=(255, 0, 0),  # Vermelho
                                    num_particulas=25, 
                                    gravidade=False,
                                    vida_max=40
                                )
                                print(f"💣 Cereja-Bomba plantada! Explode em 3 segundos! Energia: {self.total_energia}")
                            else:
                                print(f"Célula ({row}, {col}) já ocupada.")
                        else:
                             print(f"Energia insuficiente! Necessário: {custo_torre}, Atual: {self.total_energia}")
                            
                # COLETAR ENERGIA - Botão Esquerdo
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                    mouse_pos = event.pos
                    
                    for i in range(len(self.energias_caindo) - 1, -1, -1):
                        energia_obj = self.energias_caindo[i]
                        
                        if energia_obj.rect().collidepoint(mouse_pos):
                            self.total_energia += energia_obj.valor
                            
                            self.criar_particulas(
                                pos=energia_obj.pos, 
                                cor=(255, 255, 0),
                                num_particulas=20,
                                velocidade_max=1.5,
                                vida_max=40,
                                gravidade=True
                            )
                            
                            self.energias_caindo.pop(i)
                            print(f"Energia Coletada! Total: {self.total_energia}")
                            break 
                            
            # ------------------------------------
            # 3. UPDATE E DRAW
            # ------------------------------------

            self.draw_grid()
            
            # UPDATE DAS ENERGIAS (só atualiza, não desenha ainda)
            for i in range(len(self.energias_caindo) - 1, -1, -1):
                energia_obj = self.energias_caindo[i]
                morreu = energia_obj.update()
                
                if morreu:
                    self.energias_caindo.pop(i)

            
            # UPDATE E DRAW DOS INIMIGOS
            for i in range(len(self.inimigos) - 1, -1, -1):
                inimigo = self.inimigos[i]
                morreu_ou_passou = inimigo.update()
                
                if morreu_ou_passou: 
                    if inimigo.vida <= 0:
                        self.criar_particulas(
                            pos=inimigo.rect().center, 
                            cor=(255, 0, 0), 
                            num_particulas=30, 
                            velocidade_max=3,
                            vida_max=60
                        )
                    self.inimigos.pop(i)
                else:
                    inimigo.draw(self.window) 

            # UPDATE E DRAW DAS TORRES
            for i in range(len(self.torres) - 1, -1, -1):
                torre = self.torres[i]
                morreu = torre.update() 
                
                if morreu:
                    row, col = torre.grid_pos
                    self.grid[row][col] = None 
                    self.torres.pop(i)
                else:
                    torre.draw(self.window)
            
            
            # COLISÃO E UPDATE DE PROJÉTEIS
            for i in range(len(self.projeteis) - 1, -1, -1):
                p = self.projeteis[i]
                p.update()
                
                proj_rect = p.rect()
                colidiu = False
                
                if p.pode_colidir(): 
                    for j in range(len(self.inimigos) - 1, -1, -1):
                        inimigo = self.inimigos[j]
                        if proj_rect.colliderect(inimigo.rect()):
                            
                            self.criar_particulas(
                                pos=p.rect().center, 
                                cor=(100, 100, 100), 
                                num_particulas=5, 
                                velocidade_max=1,
                                vida_max=20
                            )

                            morte = inimigo.receber_dano(p.dano) 
                            
                            if morte:
                                pass 
                                
                            colidiu = True
                            break 

                if colidiu or p.pos[0] > 850:
                    self.projeteis.pop(i)
                else:
                    p.draw(self.window)
            
            
            # LOOP DE UPDATE E DRAW DAS PARTÍCULAS
            for p in self.lista_particulas:
                p.atualizar()
                p.draw(self.window)
                
            self.lista_particulas = [p for p in self.lista_particulas if p.vida > 0]
            
            # DRAW DAS ENERGIAS (POR ÚLTIMO - FICA POR CIMA DE TUDO)
            for energia_obj in self.energias_caindo:
                energia_obj.draw(self.window)

            # ------------------------------------
            # 4. UI
            # ------------------------------------
            font = pygame.font.Font(None, 30)
            
            energia_text = font.render(f"Energia: {self.total_energia}", True, (255, 255, 0))
            self.window.blit(energia_text, (50, 20))
            
            torre_text = font.render(f"Torres: {len(self.torres)}", True, (100, 255, 255))
            self.window.blit(torre_text, (50, 50))
            
            inimigo_text = font.render(f"Inimigos: {len(self.inimigos)}", True, (255, 100, 100))
            self.window.blit(inimigo_text, (50, 80))
            
            # INSTRUÇÕES
            info_font = pygame.font.Font(None, 20)
            instrucoes = [
                "Botao Direito: Peashooter (100)",
                "Botao Meio: Noz (50)",
                "Tecla G: Girassol (50)",
                "Tecla C: Cereja-Bomba (150)"
            ]
            
            for i, texto in enumerate(instrucoes):
                info_text = info_font.render(texto, True, (200, 200, 200))
                self.window.blit(info_text, (500, 20 + i * 25))
            
            # Atualiza tela
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()