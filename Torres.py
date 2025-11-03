# scripts/Torres.py

import pygame
import random
import math
from .Mecanicas import projetil 


class TorreBase:
    """ Classe base para todas as torres/plantas do jogo. """
    def __init__(self, jogo, tipo, pos, custo, vida_maxima):
        self.jogo = jogo
        self.tipo = tipo
        self.pos = list(pos)
        self.custo = custo
        self.vida_maxima = vida_maxima
        self.vida = vida_maxima
        
        try:
            self.img = jogo.assets["torre"][tipo]
        except KeyError:
             print(f"ERRO: Asset 'torre' do tipo '{tipo}' não encontrado. Usando placeholder.")
             self.img = pygame.Surface((40, 40))
             self.img.fill((0, 150, 0))
        
    def rect(self):
        return self.img.get_rect(topleft=self.pos)
    
    def update(self):
        # Retorna True se a torre deve ser removida
        return self.vida <= 0
        
    def draw(self, display):
        display.blit(self.img, (int(self.pos[0]), int(self.pos[1])))

    def receber_dano(self, dano):
        """ Aplica dano à torre. """
        self.vida -= dano
        

class Peashooter(TorreBase): 
    """Torre que atira projéteis nos inimigos."""

    CUSTO_ENERGIA = 100 
    
    def __init__(self, jogo, pos, grid_pos): 
        super().__init__(jogo, "peashooter", pos, self.CUSTO_ENERGIA, 6) 
        
        # Cooldown para atirar (começa pronto para atirar)
        self.cooldown = 0 
        self.grid_pos = grid_pos

    def update(self):
        """Atualiza a torre e verifica se deve atirar."""
        
        # Decrementa o cooldown
        if self.cooldown > 0:
            self.cooldown -= 1
        
        # Verifica se há inimigos na mesma linha
        alvo_encontrado = False
        
        # Pega a linha da torre
        torre_row = self.grid_pos[0]
        torre_center_y = self.jogo.get_cell_center(torre_row, self.grid_pos[1])[1]
        
        # Verifica se há algum inimigo na mesma linha (aproximadamente)
        for inimigo in self.jogo.inimigos:
            inimigo_center_y = inimigo.rect().centery
            
            # Tolerância de 40 pixels para detectar inimigos na mesma linha
            diferenca_y = abs(inimigo_center_y - torre_center_y)
            
            # Verifica se o inimigo está na frente (à direita) da torre
            if diferenca_y < 40 and inimigo.pos[0] > self.pos[0]:
                alvo_encontrado = True
                break
        
        # Se encontrou alvo e o cooldown acabou, atira
        if alvo_encontrado and self.cooldown <= 0:
            
            # Posição de spawn do projétil (na frente da torre)
            x_spawn = self.pos[0] + self.rect().width * 0.7 
            y_spawn = self.pos[1] + self.rect().height * 0.3
            
            # Cria partículas de disparo (opcional)
            self.jogo.criar_particulas(
                pos=(x_spawn, y_spawn),
                cor=(150, 255, 150),  # Verde claro
                num_particulas=5,
                velocidade_max=0.5,
                vida_max=15,
                gravidade=False,
                tamanho_min=1,
                tamanho_max=3
            )
            
            # Cria o projétil
            novo_projetil = projetil(
                jogo=self.jogo,
                tipo="proje", 
                pos=(x_spawn, y_spawn), 
                velocidade=[5, 0], 
                dano=1
            )
            self.jogo.projeteis.append(novo_projetil)
            
            # Reseta o cooldown para 84-90 frames (1.4s a 1.5s)
            self.cooldown = random.randint(84, 90)
        
        # Chama o update da classe base (verifica se morreu)
        return super().update()


class NozObstaculo(TorreBase): 
    """Torre obstáculo que apenas bloqueia inimigos."""
    
    CUSTO_ENERGIA = 50 
    
    def __init__(self, jogo, pos, grid_pos): 
        VIDA_MAXIMA_NOZ = 40 
        
        super().__init__(jogo, "noz", pos, self.CUSTO_ENERGIA, VIDA_MAXIMA_NOZ) 
        self.grid_pos = grid_pos
    
    def update(self):
        """Noz não ataca, apenas existe."""
        return super().update()


class Girassol(TorreBase):
    """Torre que gera energia periodicamente (baseada no Sunflower do PvZ)."""
    
    CUSTO_ENERGIA = 50
    ENERGIA_GERADA = 25  # Quantidade de energia gerada
    
    def __init__(self, jogo, pos, grid_pos):
        super().__init__(jogo, "girassol", pos, self.CUSTO_ENERGIA, 6)
        self.grid_pos = grid_pos
        
        # Cooldown para gerar energia
        # Primeira geração: 8 segundos (480 frames a 60 FPS)
        # Gerações seguintes: 20-24 segundos (1200-1440 frames)
        self.cooldown_geracao = 480  # 8 segundos para o primeiro sol
        self.cooldown_max = 1440  # 24 segundos
        self.primeira_geracao = True  # Flag para controlar o primeiro sol
        
    def update(self):
        """Atualiza a torre e gera energia periodicamente."""
        
        # Decrementa o cooldown
        if self.cooldown_geracao > 0:
            self.cooldown_geracao -= 1
        
        # Quando o cooldown chega a 0, gera energia
        if self.cooldown_geracao <= 0:
            # Posição onde a energia vai aparecer (em cima do girassol)
            moeda_x = self.rect().centerx - self.jogo.assets["Energia"].get_width() // 2
            moeda_y = self.rect().top - self.jogo.assets["Energia"].get_height()  # Acima do girassol
            
            # Cria o objeto Energia com "pulinho" (velocidade inicial para cima e para baixo)
            from .Mecanicas import Energia
            
            # Calcula onde a energia deve parar (posição mais natural e variada)
            # Pode cair em várias posições ao redor do girassol
            
            # Offset horizontal: -30 a +30 pixels do centro do girassol
            offset_x = random.randint(-30, 30)
            x_parada = self.rect().centerx + offset_x
            
            # Altura: entre o topo do girassol e um pouco abaixo (mais natural)
            y_min = self.rect().top + 10
            y_max = self.rect().bottom + 20
            y_parada_girassol = random.randint(y_min, y_max)
            
            # Velocidade horizontal aleatória (leve movimento lateral)
            vel_x = random.uniform(-0.5, 0.5)
            
            nova_energia = Energia(
                jogo=self.jogo,
                pos=(moeda_x, moeda_y),
                velocidade=[vel_x, -2],  # Velocidade inicial: sobe + movimento lateral leve
                valor=self.ENERGIA_GERADA,
                vida=480,  # Mesma duração das energias do céu
                onda=True  # Usa o efeito de onda para "cair" e parar
            )
            # Sobrescreve o y_parada para ficar perto do girassol (mais natural)
            nova_energia.y_parada = y_parada_girassol
            nova_energia.x_parada = x_parada  # Define onde deve parar horizontalmente
            
            self.jogo.energias_caindo.append(nova_energia)
            
            # Partículas douradas ao criar a energia
            self.jogo.criar_particulas(
                pos=self.rect().center,
                cor=(255, 215, 0),  # Dourado
                num_particulas=10,
                velocidade_max=1.0,
                vida_max=20,
                gravidade=False,
                tamanho_min=2,
                tamanho_max=4
            )
            
            # Mensagem de feedback
            print(f"Girassol produziu energia! Clique para coletar.")
            
            # Reseta o cooldown
            if self.primeira_geracao:
                # Após o primeiro sol, muda para geração padrão
                self.cooldown_geracao = random.randint(1200, 1440)  # 20-24 segundos
                self.primeira_geracao = False
            else:
                # Gerações subsequentes: 20-24 segundos
                self.cooldown_geracao = random.randint(1200, 1440)
        
        # Chama o update da classe base (verifica se morreu)
        return super().update()


class CerejaBomba(TorreBase):
    """Torre explosiva que detona após alguns segundos, matando todos os inimigos em área 3x3."""
    
    CUSTO_ENERGIA = 150
    
    def __init__(self, jogo, pos, grid_pos):
        super().__init__(jogo, "cereja", pos, self.CUSTO_ENERGIA, 999)  # Vida alta, não recebe dano
        self.grid_pos = grid_pos
        
        # Tempo até explodir: 3 segundos (180 frames a 60 FPS)
        self.tempo_explosao = 180
        self.explodiu = False
        
    def update(self):
        """Atualiza a cereja e explode quando o tempo acaba."""
        
        # Decrementa o tempo até a explosão
        if self.tempo_explosao > 0:
            self.tempo_explosao -= 1
            
            # Efeito visual de "piscada" nos últimos segundos (60 frames = 1 segundo)
            if self.tempo_explosao <= 60 and self.tempo_explosao % 10 == 0:
                # Partículas de aviso (pisca vermelho)
                self.jogo.criar_particulas(
                    pos=self.rect().center,
                    cor=(255, 100, 0),  # Laranja/Vermelho
                    num_particulas=5,
                    velocidade_max=0.5,
                    vida_max=10,
                    gravidade=False,
                    tamanho_min=2,
                    tamanho_max=4
                )
        
        # Quando o tempo chega a 0, EXPLODE!
        if self.tempo_explosao <= 0 and not self.explodiu:
            self.explodir()
            self.explodiu = True
            return True  # Remove a cereja após explodir
        
        return False  # Não remove ainda
    
    def explodir(self):
        """Causa a explosão em área 3x3."""
        
        print("💥 CEREJA-BOMBA EXPLODIU!")
        
        # Calcula a área de explosão (3x3 células ao redor)
        centro_row, centro_col = self.grid_pos
        
        # Define o raio de explosão em pixels
        raio_explosao_cells = 1  # 1 célula ao redor = área 3x3
        
        # Pega as dimensões das células
        cell_width = self.jogo.CELL_WIDTH
        cell_height = self.jogo.CELL_HEIGHT
        
        # Calcula o centro da explosão em pixels
        centro_x, centro_y = self.jogo.get_cell_center(centro_row, centro_col)
        
        # Raio de explosão em pixels (1.5 células = área 3x3)
        raio_pixels = int(1.5 * max(cell_width, cell_height))
        
        # EFEITO VISUAL MASSIVO
        # 1. Partículas de explosão (grande quantidade)
        self.jogo.criar_particulas(
            pos=(centro_x, centro_y),
            cor=(255, 100, 0),  # Laranja forte
            num_particulas=80,
            velocidade_max=6,
            vida_max=60,
            gravidade=True,
            tamanho_min=3,
            tamanho_max=8
        )
        
        # 2. Partículas vermelhas (fogo)
        self.jogo.criar_particulas(
            pos=(centro_x, centro_y),
            cor=(255, 50, 50),  # Vermelho
            num_particulas=60,
            velocidade_max=5,
            vida_max=50,
            gravidade=True,
            tamanho_min=2,
            tamanho_max=6
        )
        
        # 3. Partículas amarelas (luz)
        self.jogo.criar_particulas(
            pos=(centro_x, centro_y),
            cor=(255, 255, 100),  # Amarelo
            num_particulas=40,
            velocidade_max=4,
            vida_max=40,
            gravidade=False,
            tamanho_min=2,
            tamanho_max=5
        )
        
        # DANO AOS INIMIGOS
        inimigos_mortos = 0
        for i in range(len(self.jogo.inimigos) - 1, -1, -1):
            inimigo = self.jogo.inimigos[i]
            
            # Calcula a distância do inimigo ao centro da explosão
            distancia_x = abs(inimigo.rect().centerx - centro_x)
            distancia_y = abs(inimigo.rect().centery - centro_y)
            distancia = math.sqrt(distancia_x**2 + distancia_y**2)
            
            # Se o inimigo está dentro do raio, mata instantaneamente
            if distancia <= raio_pixels:
                # Partículas de morte do inimigo
                self.jogo.criar_particulas(
                    pos=inimigo.rect().center,
                    cor=(255, 0, 0),
                    num_particulas=30,
                    velocidade_max=4,
                    vida_max=50,
                    gravidade=True
                )
                
                self.jogo.inimigos.pop(i)
                inimigos_mortos += 1
        
        print(f"💀 Cereja-Bomba matou {inimigos_mortos} inimigos!")
    
    def draw(self, display):
        """Desenha a cereja com efeito de piscada quando próximo da explosão."""
        # Se está nos últimos 60 frames e em frame par, não desenha (efeito de piscar)
        if self.tempo_explosao <= 60 and (self.tempo_explosao // 5) % 2 == 0:
            return  # Não desenha (pisca)
        
        # Desenha normalmente
        super().draw(display)