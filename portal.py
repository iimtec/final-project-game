import pygame
import random
import math
from settings import TILE_SIZE, MAZE_WIDTH, MAZE_HEIGHT


class Portal:
    def __init__(self, maze, size=30, portal_type='normal'):
        self.size = size
        self.maze = maze
        self.type = portal_type
        player_start = (TILE_SIZE, TILE_SIZE)
        if self.type == 'escape':
            min_distance = TILE_SIZE * 6
        else:
            min_distance = TILE_SIZE * 5  # Keep portals away from player spawn
        self.x, self.y = self.find_random_valid_position(min_distance, player_start)
        self.respawn_timer = 0
        self.respawn_interval = 300  # respawn every 5 seconds (300 frames at 60fps)

    def find_random_valid_position(self, min_distance=0, player_start=None):
        """Find a random walkable position in the maze, optionally far from the player start."""
        attempts = 0
        while attempts < 1000:
            grid_x = random.randint(1, MAZE_WIDTH - 2)
            grid_y = random.randint(1, MAZE_HEIGHT - 2)
            if self.maze.grid[grid_y][grid_x] == 0:  # walkable
                x = grid_x * TILE_SIZE
                y = grid_y * TILE_SIZE
                if min_distance > 0 and player_start is not None:
                    dx = x - player_start[0]
                    dy = y - player_start[1]
                    if math.hypot(dx, dy) < min_distance:
                        attempts += 1
                        continue
                return x, y
            attempts += 1

        # fallback if no position found after many attempts
        while True:
            grid_x = random.randint(1, MAZE_WIDTH - 2)
            grid_y = random.randint(1, MAZE_HEIGHT - 2)
            if self.maze.grid[grid_y][grid_x] == 0:
                return grid_x * TILE_SIZE, grid_y * TILE_SIZE

    def check_collision(self, player):
        """Check if player collides with portal"""
        player_left = player.x
        player_right = player.x + player.size
        player_top = player.y
        player_bottom = player.y + player.size

        portal_left = self.x
        portal_right = self.x + self.size
        portal_top = self.y
        portal_bottom = self.y + self.size

        return (
            player_right > portal_left
            and player_left < portal_right
            and player_bottom > portal_top
            and player_top < portal_bottom
        )

    def teleport_player(self, player):
        """Teleport player to random location"""
        player.x, player.y = self.find_random_valid_position()
