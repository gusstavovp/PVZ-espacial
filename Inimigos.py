# scripts/Inimigos.py

import pygame
import random
import math
from .Torres import TorreBase

class Inimigo:
    """Classe para inimigos que atacam as torres."""

    def __init__(self, jogo, tipo, pos, vida=10, velocidade=0.007, dano=1): 
        self.jogo = jogo
        self.tipo = tipo
        self.pos = list(pos)
        
        # Carrega a imagem do inimigo
        try:
            self.img = jogo.assets["inimigo"][tipo]
        except KeyError:
            print(f"ERRO: Asset 'inimigo' do tipo '{tipo}' não encontrado. Usando placeholder.")
            self.img = pygame.Surface((40, 40))
            self.img.fill((255, 0, 0))  # Vermelho para inimigos
             
        self.velocidade_base = velocidade
        self.velocidade_atual = velocidade
        self.movendo = True
        self.vida = vida 
        self.vida_maxima = vida  # Para barra de vida
        self.dano_ataque = 1.0  # Dano fixo de 1.0
        
        # Cooldown para ataque (60 frames = 1 segundo, se o FPS for 60)
        self.cooldown_ataque_max = 60
        self.cooldown_ataque_atual = 0 
        
    def rect(self):
        """Retorna o retângulo de colisão do inimigo."""
        return self.img.get_rect(topleft=self.pos).inflate(-10, -10) 
        
    def receber_dano(self, dano):
        """Aplica dano ao inimigo e retorna True se morreu."""
        self.vida -= dano
        return self.vida <= 0
        
    def update(self):
        """Atualiza o estado do inimigo (movimento, colisão, ataque)."""
        
        self.movendo = True
        
        # 1. Lógica de Colisão com Torres
        colidiu_com_torre = False
        for torre in self.jogo.torres:
            if self.rect().colliderect(torre.rect()):
                self.movendo = False
                colidiu_com_torre = True
                
                # Lógica de Cooldown de Ataque
                if self.cooldown_ataque_atual <= 0:
                    torre.receber_dano(self.dano_ataque)  # Aplica 1 de dano
                    self.cooldown_ataque_atual = self.cooldown_ataque_max
                    
                break
        
        # Atualiza o cooldown se colidiu, mas não ataca se for 0
        if colidiu_com_torre and self.cooldown_ataque_atual > 0:
            self.cooldown_ataque_atual -= 1 

        # 2. Movimento
        if self.movendo:
            self.pos[0] -= self.velocidade_atual
            
        # 3. Condição de Morte ou Game Over
        if self.vida <= 0:
            return True 
        if self.pos[0] < -50:
            print("Inimigo atravessou! Game Over ou perda de vida do jogador.")
            return True  # Remove o inimigo que passou
            
        return False
    
    def draw(self, display):
        """Desenha o inimigo e sua barra de vida na tela."""
        # Desenha a imagem do inimigo
        display.blit(self.img, (int(self.pos[0]), int(self.pos[1])))
        
        # Desenha a barra de vida
        if self.vida < self.vida_maxima:  # Só mostra se tiver dano
            barra_largura = 40
            barra_altura = 5
            barra_x = int(self.pos[0])
            barra_y = int(self.pos[1]) - 10
            
            # Fundo da barra (vermelho)
            pygame.draw.rect(display, (255, 0, 0), 
                           (barra_x, barra_y, barra_largura, barra_altura))
            
            # Barra de vida atual (verde)
            vida_percent = max(0, self.vida / self.vida_maxima)
            largura_vida = int(barra_largura * vida_percent)
            pygame.draw.rect(display, (0, 255, 0), 
                           (barra_x, barra_y, largura_vida, barra_altura))