import pygame, math, random

class projetil:

    def __init__(self, jogo, tipo, pos, velocidade=[0, 0], dano=1):
        self.jogo = jogo
        self.tipo = tipo
        self.pos = list(pos)
        self.velocidade = list(velocidade)
        self.dano = dano
        self.img = jogo.assets["projetil"][tipo]
        # Período de graça de 3 frames antes de poder colidir
        self.vida_util = 3 
        
    def rect(self):
        return pygame.Rect(self.pos, self.img.get_size())
    
    def update(self):
        # Decrementa o período de graça
        if self.vida_util > 0:
            self.vida_util -= 1
            
        self.pos[0] += self.velocidade[0]
        self.pos[1] += self.velocidade[1]
        
    def draw(self, display):
        display.blit(self.img, (int(self.pos[0]), int(self.pos[1])))
        
    def pode_colidir(self):
        """Verifica se o projétil já pode colidir (após o grace period)."""
        return self.vida_util <= 0

# ===================================================
# CLASSE ENERGIA (Com efeito de "pulinho")
# ===================================================
class Energia:
    
    def __init__ (self, jogo, pos, velocidade=[0, 0], valor=25, vida=480, onda=True):
        
        self.jogo = jogo
        self.pos = list(pos)
        self.velocidade = list(velocidade)
        self.valor = valor
        
        self.vida_maxima = vida
        self.vida = vida 
        
        self.onda = onda 
        self.img = jogo.assets["Energia"]
        
        self.tempo_parada_max = 60 
        self.tempo_parada_atual = 0
        
        # Gravidade para o efeito de "pulinho" (só para energia do girassol)
        self.usa_gravidade = (velocidade[1] < 0)  # Se começa subindo, usa gravidade
        self.gravidade = 0.15 if self.usa_gravidade else 0  # Aceleração da gravidade

        y_min = jogo.GRID_OFFSET_Y + jogo.CELL_HEIGHT * 0.5 
        y_max = jogo.GRID_OFFSET_Y + jogo.GRID_ROWS * jogo.CELL_HEIGHT - self.img.get_height()
        
        self.y_parada = random.uniform(y_min, y_max)
        self.x_parada = None  # Posição X onde deve parar (usado para energia do girassol)
        
    def rect(self):
        return pygame.Rect(self.pos, self.img.get_size())
    
    def update(self):
        self.vida -= 1
        
        if self.onda:
            # Aplica a velocidade horizontal e vertical
            self.pos[0] += self.velocidade[0]
            self.pos[1] += self.velocidade[1]
            
            # Aplica gravidade APENAS se for energia do girassol (que começa subindo)
            if self.usa_gravidade:
                self.velocidade[1] += self.gravidade

            # Verifica se chegou na posição de parada
            if self.pos[1] >= self.y_parada and self.velocidade[1] > 0:
                self.pos[1] = self.y_parada
                self.velocidade[1] = 0
                self.velocidade[0] = 0
                self.onda = False 
        
        if not self.onda:
            pass

        return self.vida <= 0
            
    def draw(self, display):
        display.blit(self.img, (int(self.pos[0]), int(self.pos[1])))
        
# ===================================================
# CLASSE PARTICULAS
# ===================================================
class particulas:
    
    def __init__(self, pos, velocidade, vida, cor, tamanho=1, encolher_particula=True, gravidade=False):
        
        self.pos = list(pos)
        self.velocidade = list(velocidade)
        self.vida = vida
        self.cor = cor
        self.tamanho = tamanho
        self.encolher_particula = encolher_particula
        self.gravidade = gravidade
        
        self.vida_max = self.vida
        self.tamanho_max = self.tamanho
        
    def atualizar(self): 
        
        self.vida -= 1
        
        if self.gravidade:
            self.velocidade[1] += 0.05 
            
        self.pos[0] += self.velocidade[0]
        self.pos[1] += self.velocidade[1]
        
        if self.encolher_particula:
            life_percent = max(self.vida, 0) / self.vida_max
            self.tamanho = math.ceil(life_percent * self.tamanho_max)
            
    def draw(self, display):
        if self.vida > 0 and self.tamanho > 0:
            pygame.draw.circle(display, self.cor, (int(self.pos[0]), int(self.pos[1])), int(self.tamanho))