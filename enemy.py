import pygame
import os
import re
import random
from collections import deque
from settings import TILE_SIZE, ENEMY_DETECTION_RANGE

class Enemy:
    def __init__(self, x, y, size=45, speed=1.5):
        self.x = x
        self.y = y
        self.size = size
        self.draw_size = max(self.size * 2, 64)
        self.speed = speed
        self.path = []
        self.recalc_timer = 0
        self.roam_target = None
        self.is_chasing = False
        self.direction = 'front'
        self.previous_direction = 'front'
        self.frame_index = 0
        self.frame_timer = 0
        self.animation_speed = 8
        self.images = self.load_avatar_images('enemy_avatar')

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
        if name.startswith('enemy_'):
            name = name[len('enemy_'):]
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

    def set_direction(self, dx, dy):
        if abs(dx) > abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'front' if dy > 0 else 'back'

    def get_current_image(self):
        if not self.images:
            return None
        frames = self.images.get(self.direction) or self.images.get('idle')
        if not frames:
            return None
        if self.direction != self.previous_direction:
            self.previous_direction = self.direction
            self.frame_index = 0
            self.frame_timer = 0
        if self.frame_index >= len(frames):
            self.frame_index = 0
        if len(frames) == 1:
            return frames[0]
        self.frame_timer += 1
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)
        return frames[self.frame_index]

    def distance_to_player(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        return (dx**2 + dy**2) ** 0.5

    def bfs_path(self, start_grid, goal_grid, maze):
        queue = deque([(start_grid, [start_grid])])
        visited = {start_grid}

        while queue:
            (gx, gy), current_path = queue.popleft()

            if (gx, gy) == goal_grid:
                return current_path[1:]

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = gx + dx, gy + dy

                if (nx, ny) in visited:
                    continue
                if ny < 0 or ny >= len(maze.grid) or nx < 0 or nx >= len(maze.grid[0]):
                    continue
                if maze.grid[ny][nx] == 1:
                    continue

                visited.add((nx, ny))
                queue.append(((nx, ny), current_path + [(nx, ny)]))

        return []

    def find_path_to_player(self, player, maze):
        start_grid = (int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))
        goal_grid = (int(player.x // TILE_SIZE), int(player.y // TILE_SIZE))

        if start_grid == goal_grid:
            self.path = []
            return

        self.path = self.bfs_path(start_grid, goal_grid, maze)

    def path_is_to_player(self, player):
        if not self.path:
            return False
        return self.path[-1] == (int(player.x // TILE_SIZE), int(player.y // TILE_SIZE))

    def find_roam_target(self, maze):
        width = len(maze.grid[0])
        height = len(maze.grid)

        for _ in range(100):
            gx = random.randint(1, width - 2)
            gy = random.randint(1, height - 2)
            if maze.grid[gy][gx] == 0:
                return gx, gy

        return (int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))

    def update(self, player, maze):
        distance = self.distance_to_player(player)
        self.recalc_timer += 1

        if distance <= ENEMY_DETECTION_RANGE:
            self.is_chasing = True
            if self.recalc_timer >= 30 or not self.path or not self.path_is_to_player(player):
                self.find_path_to_player(player, maze)
                self.recalc_timer = 0
        else:
            self.is_chasing = False
            if not self.path:
                self.roam_target = self.find_roam_target(maze)
                self.path = self.bfs_path(
                    (int(self.x // TILE_SIZE), int(self.y // TILE_SIZE)),
                    self.roam_target,
                    maze
                )
                self.recalc_timer = 0

        if self.path:
            next_grid = self.path[0]
            target_x = next_grid[0] * TILE_SIZE + TILE_SIZE // 2
            target_y = next_grid[1] * TILE_SIZE + TILE_SIZE // 2

            dx = target_x - self.x
            dy = target_y - self.y
            distance_to_next = (dx**2 + dy**2) ** 0.5

            if distance_to_next < self.speed:
                self.x = target_x
                self.y = target_y
                self.path.pop(0)
                if not self.path and not self.is_chasing:
                    self.roam_target = None
            else:
                self.x += (dx / distance_to_next) * self.speed
                self.y += (dy / distance_to_next) * self.speed
            self.set_direction(dx, dy)
        elif self.is_chasing:
            # If we're in the same grid as the player or the path is empty,
            # move directly toward the player's actual position so we can catch them.
            dx = player.x - self.x
            dy = player.y - self.y
            distance_to_player = (dx**2 + dy**2) ** 0.5
            if distance_to_player > 0:
                self.set_direction(dx, dy)
                if distance_to_player <= self.speed:
                    self.x += dx
                    self.y += dy
                else:
                    self.x += (dx / distance_to_player) * self.speed
                    self.y += (dy / distance_to_player) * self.speed

    def collides_with_player(self, player):
        """Check collision with player"""
        enemy_left = self.x
        enemy_right = self.x + self.size
        enemy_top = self.y
        enemy_bottom = self.y + self.size

        player_left = player.x
        player_right = player.x + player.size
        player_top = player.y
        player_bottom = player.y + player.size

        return (
            enemy_right >= player_left
            and enemy_left <= player_right
            and enemy_bottom >= player_top
            and enemy_top <= player_bottom
        )