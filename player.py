import pygame
import os
import re
import math
from settings import PLAYER_SPEED
from settings import TILE_SIZE
from settings import PLAYER_SIZE

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Image
        self.x = TILE_SIZE
        self.y = TILE_SIZE
        self.size = PLAYER_SIZE
        self.collision_size = max(self.size - 40, 16)
        self.draw_size = max(self.size * 2, 64)
        self.speed = 3
        self.direction = 'idle'
        self.previous_direction = 'idle'
        self.moving = False
        self.frame_index = 0
        self.frame_timer = 0
        self.animation_speed = 7
        self.images = self.load_avatar_images('player_avatar')
    
    def load_avatar_images(self, folder):
        images = {}
        try:
            folder_path = os.path.join(os.path.dirname(__file__), folder)
            if not os.path.isdir(folder_path):
                return None
            for file_name in os.listdir(folder_path):
                name, ext = os.path.splitext(file_name)
                if ext.lower() not in ('.png', '.jpg', '.jpeg'):
                    continue
                key = self.get_avatar_key(name.lower())
                if not key:
                    continue
                image = pygame.image.load(os.path.join(folder_path, file_name)).convert_alpha()
                image = pygame.transform.scale(image, (self.draw_size, self.draw_size))
                frame_number = self.get_avatar_frame_number(name.lower())
                images.setdefault(key, []).append((frame_number, image))
            for key, frames in images.items():
                frames.sort(key=lambda item: item[0])
                images[key] = [frame for _, frame in frames]
            return images if images else None
        except Exception:
            return None

    def get_avatar_key(self, name):
        if name.startswith('player_'):
            name = name[len('player_'):]
        if 'front' in name:
            return 'front'
        if 'back' in name or 'rear' in name:
            return 'back'
        if 'left' in name:
            return 'left'
        if 'right' in name:
            return 'right'
        if 'idle' in name or 'stand' in name or 'still' in name:
            return 'idle'
        return None

    def get_avatar_frame_number(self, name):
        match = re.search(r'(\d+)', name)
        if match:
            return int(match.group(1))
        return 0

    def handle_input(self,keys,maze):
        dx, dy = 0, 0
        moved = False

        if keys[pygame.K_w]:
            dy = -self.speed
            self.direction = 'back'
            moved = True
        if keys[pygame.K_s]:
            dy = self.speed
            self.direction = 'front'
            moved = True
        if keys[pygame.K_a]:
            dx = -self.speed
            self.direction = 'left'
            moved = True
        if keys[pygame.K_d]:
            dx = self.speed
            self.direction = 'right'
            moved = True

        if not moved:
            self.direction = 'idle'

        self.previous_direction = self.direction if self.direction != 'idle' else self.previous_direction
        self.moving = False

        start_x, start_y = self.x, self.y

        if dx != 0:
            step = int(math.copysign(1, dx))
            for _ in range(abs(dx)):
                if not self.collides(self.x + step, self.y, maze):
                    self.x += step
                else:
                    break

        if dy != 0:
            step = int(math.copysign(1, dy))
            for _ in range(abs(dy)):
                if not self.collides(self.x, self.y + step, maze):
                    self.y += step
                else:
                    break

        self.moving = (self.x != start_x or self.y != start_y)

    def update(self):
        if not self.images:
            return

        if self.direction != self.previous_direction:
            self.frame_index = 0
            self.frame_timer = 0
            self.previous_direction = self.direction

        current_frames = self.images.get(self.direction) or self.images.get('idle')
        if not current_frames:
            return

        if self.moving and len(current_frames) > 1:
            self.frame_timer += 1
            if self.frame_timer >= self.animation_speed:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(current_frames)
        else:
            self.frame_timer = 0
            self.frame_index = 0

    # Check collision before moving
    def collides(self, x, y, maze):
        offset = (self.size - self.collision_size) / 2
        return (
            maze.is_wall(x + offset, y + offset) or
            maze.is_wall(x + offset + self.collision_size, y + offset) or
            maze.is_wall(x + offset, y + offset + self.collision_size) or
            maze.is_wall(x + offset + self.collision_size, y + offset + self.collision_size)
        )

    def get_rect(self):
        offset = (self.size - self.collision_size) / 2
        return pygame.Rect(self.x + offset, self.y + offset, self.collision_size, self.collision_size)