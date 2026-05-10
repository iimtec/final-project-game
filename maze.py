import random
import pygame
from settings import TILE_SIZE, MAZE_WIDTH, MAZE_HEIGHT

class Maze:
    def __init__(self):
        self.grid = [[1 for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        self.generate_maze(1, 1)
        self.add_loops(0.1)

    def regenerate(self):
        """Regenerate the maze with a new layout"""
        self.grid = [[1 for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        self.generate_maze(1, 1)
        self.add_loops(0.1)

    # DFS Maze Generation
    def generate_maze(self, x, y):
        self.grid[y][x] = 0

        directions = [(2,0), (-2,0), (0,2), (0,-2)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx = x + dx
            ny = y + dy

            if 0 < nx < MAZE_WIDTH and 0 < ny < MAZE_HEIGHT and self.grid[ny][nx] == 1:
                self.grid[y + dy//2][x + dx//2] = 0
                self.generate_maze(nx, ny)

    # Add randomness
    def add_loops(self, chance=0.1):
        for y in range(1, len(self.grid) - 1):
            for x in range(1, len(self.grid[0]) - 1):
                if self.grid[y][x] == 1:
                    if random.random() < chance:
                        self.grid[y][x] = 0

    # Draw Maze with enhanced visuals
    def draw(self, screen, camera):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == 1:  # wall
                    world_x = x * TILE_SIZE
                    world_y = y * TILE_SIZE

                    draw_x, draw_y = camera.apply(world_x, world_y)
                    tile_size = int(TILE_SIZE * camera.zoom)

                    # Draw wall with 3D effect using layers
                    # Shadow/depth layer
                    pygame.draw.rect(
                        screen,
                        (40, 40, 60),
                        (draw_x + 2, draw_y + 2, tile_size, tile_size)
                    )
                    
                    # Main wall color with gradient effect
                    pygame.draw.rect(
                        screen,
                        (180, 180, 200),
                        (draw_x, draw_y, tile_size, tile_size)
                    )
                    
                    # Border for depth
                    pygame.draw.rect(
                        screen,
                        (100, 100, 130),
                        (draw_x, draw_y, tile_size, tile_size),
                        2
                    )
                    
                    # Highlight for 3D effect
                    pygame.draw.line(
                        screen,
                        (220, 220, 240),
                        (draw_x + 2, draw_y + 2),
                        (draw_x + tile_size - 2, draw_y + 2),
                        1
                    )
                    pygame.draw.line(
                        screen,
                        (220, 220, 240),
                        (draw_x + 2, draw_y + 2),
                        (draw_x + 2, draw_y + tile_size - 2),
                        1
                    )

    # Collision Check
    def is_wall(self, x, y):
        grid_x = int(x // TILE_SIZE)
        grid_y = int(y // TILE_SIZE)

        if 0 <= grid_x < MAZE_WIDTH and 0 <= grid_y < MAZE_HEIGHT:
            return self.grid[grid_y][grid_x] == 1

        return True  # outside map = wall