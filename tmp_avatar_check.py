import pygame
import os
import sys
sys.path.insert(0, os.getcwd())
from player import Player
pygame.init()
p = Player()
print('type', type(p.images))
if p.images:
    print('keys', list(p.images.keys()))
    print('front', len(p.images.get('front', [])))
    print('back', len(p.images.get('back', [])))
    print('idle', len(p.images.get('idle', [])))
else:
    print('no images loaded')
