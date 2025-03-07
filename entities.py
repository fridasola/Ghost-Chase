# entities.py
import pygame
import math
import random

class Entity:
    def __init__(self, x, y, speed, points_de_vie, type):
        self.x = x
        self.y = y  # Fixed: was using x instead of y
        self.speed = speed
        self.points_de_vie = points_de_vie
        self.type = type
        self.alive = True  # Added alive property for all entities

class Chasseur(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, speed=2, points_de_vie=100, type='chasseur')
        self.lampe_on = False
        self.batterie_lampe = 100
        
    def use_light(self):
        if self.batterie_lampe > 0:
            self.batterie_lampe -= 0.5  # Drain battery gradually
            return True
        else:
            self.lampe_on = False
            return False

class Fantome(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1, points_de_vie=10, type='fantome')
        self.visible = False  # Add visibility property

    def take_damage(self, amount):
        self.points_de_vie -= amount
        if self.points_de_vie <= 0:
            self.alive = False

class BatteryRecharge:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 15000  # Increased duration to 15 seconds