import pygame

class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.width = width
        self.height = height
        self.zoom = 1.5

    def update(self, player):
        self.offset_x = player.x - (self.width / 2) / self.zoom
        self.offset_y = player.y - (self.height / 2) / self.zoom

    def apply(self, x, y):
        screen_x = (x - self.offset_x) * self.zoom
        screen_y = (y - self.offset_y) * self.zoom
        return screen_x, screen_y