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

    def teleport_player(self, player, portals_to_avoid=None, escape_door=None):
        """Teleport player to random location away from other portals"""
        min_distance = TILE_SIZE * 5  # Keep teleported player away from other portals
        
        # Keep trying to find a position far from other portals
        for attempt in range(100):
            new_x, new_y = self.find_random_valid_position(min_distance=0)
            
            # Check distance from all portals to avoid
            too_close = False
            if portals_to_avoid:
                for other_portal in portals_to_avoid:
                    if other_portal is not self:
                        dx = new_x - other_portal.x
                        dy = new_y - other_portal.y
                        distance = math.hypot(dx, dy)
                        if distance < min_distance:
                            too_close = True
                            break
            
            # Also check escape door
            if not too_close and escape_door:
                dx = new_x - escape_door.x
                dy = new_y - escape_door.y
                distance = math.hypot(dx, dy)
                if distance < min_distance:
                    too_close = True
            
            # If position is valid, use it
            if not too_close:
                player.x, player.y = new_x, new_y
                return
        
        # Fallback: just teleport to any valid position
        player.x, player.y = self.find_random_valid_position()
