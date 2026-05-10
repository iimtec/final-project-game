import pygame
import random
import math
from settings import TILE_SIZE, MAZE_WIDTH, MAZE_HEIGHT


class HintItem:
    """A collectible item that reveals the direction to the escape door."""
    def __init__(self, maze, size=25):
        self.size = size
        self.maze = maze
        player_start = (TILE_SIZE, TILE_SIZE)
        min_distance = TILE_SIZE * 3  # Place near walkable areas but away from spawn
        self.x, self.y = self.find_random_valid_position(min_distance, player_start)
        self.collected = False
    
    def find_random_valid_position(self, min_distance=0, player_start=None):
        """Find a random walkable position in the maze."""
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
        
        # fallback
        while True:
            grid_x = random.randint(1, MAZE_WIDTH - 2)
            grid_y = random.randint(1, MAZE_HEIGHT - 2)
            if self.maze.grid[grid_y][grid_x] == 0:
                return grid_x * TILE_SIZE, grid_y * TILE_SIZE
    
    def check_collision(self, player):
        """Check if player collides with this hint item."""
        if self.collected:
            return False
        
        player_left = player.x
        player_right = player.x + player.size
        player_top = player.y
        player_bottom = player.y + player.size
        
        item_left = self.x - self.size // 2
        item_right = self.x + self.size // 2
        item_top = self.y - self.size // 2
        item_bottom = self.y + self.size // 2
        
        if (player_right > item_left and player_left < item_right and
            player_bottom > item_top and player_top < item_bottom):
            self.collected = True
            return True
        
        return False


class ArrowEffect:
    """Displays an arrow pointing to the escape door."""
    def __init__(self, duration=300):  # 5 seconds at 60fps
        self.duration = duration
        self.max_duration = duration
        self.active = False
    
    def activate(self):
        """Activate the arrow effect."""
        self.active = True
        self.duration = self.max_duration
    
    def update(self):
        """Update the arrow effect."""
        if self.active:
            self.duration -= 1
            if self.duration <= 0:
                self.active = False
    
    def draw(self, surface, player, escape_door, camera):
        """Draw the arrow pointing to the escape door."""
        if not self.active or self.duration <= 0:
            return
        
        # Get screen center where player is drawn
        player_screen_x = surface.get_width() // 2
        player_screen_y = surface.get_height() // 2
        
        # Calculate direction to escape door
        dx = escape_door.x - player.x
        dy = escape_door.y - player.y
        distance = math.hypot(dx, dy)
        
        if distance < 1:
            return
        
        # Normalize direction
        dir_x = dx / distance
        dir_y = dy / distance
        
        # Arrow starts from player position and points towards escape door
        arrow_length = 80
        arrow_end_x = player_screen_x + dir_x * arrow_length
        arrow_end_y = player_screen_y + dir_y * arrow_length
        
        # Arrow tip
        tip_x = arrow_end_x
        tip_y = arrow_end_y
        
        # Arrow head points (perpendicular)
        arrow_head_size = 15
        perp_x = -dir_y
        perp_y = dir_x
        
        left_x = tip_x - arrow_head_size * dir_x - perp_x * arrow_head_size // 2
        left_y = tip_y - arrow_head_size * dir_y - perp_y * arrow_head_size // 2
        
        right_x = tip_x - arrow_head_size * dir_x + perp_x * arrow_head_size // 2
        right_y = tip_y - arrow_head_size * dir_y + perp_y * arrow_head_size // 2
        
        # Calculate fade effect based on remaining duration
        alpha = int(255 * (self.duration / self.max_duration))
        
        # Draw arrow line
        color = (0, 255, 0)  # Green arrow
        
        # Create a surface with alpha support for the arrow
        arrow_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        
        # Draw arrow shaft with glow
        for i in range(4, 0, -1):
            glow_color = (*color, max(0, alpha - i * 40))
            pygame.draw.line(arrow_surface, glow_color, 
                           (player_screen_x, player_screen_y),
                           (arrow_end_x, arrow_end_y), i + 2)
        
        # Draw main arrow shaft
        pygame.draw.line(arrow_surface, (*color, alpha),
                        (player_screen_x, player_screen_y),
                        (arrow_end_x, arrow_end_y), 3)
        
        # Draw arrow head (triangle)
        points = [(int(tip_x), int(tip_y)), 
                 (int(left_x), int(left_y)), 
                 (int(right_x), int(right_y))]
        pygame.draw.polygon(arrow_surface, (*color, alpha), points)
        
        # Add text indicator
        font = pygame.font.SysFont('arial', 20, bold=True)
        text = f"Exit: {int(distance // TILE_SIZE)} tiles away"
        text_surface = font.render(text, True, color)
        text_surface.set_alpha(alpha)
        text_x = player_screen_x - text_surface.get_width() // 2
        text_y = player_screen_y - 60
        arrow_surface.blit(text_surface, (text_x, text_y))
        
        # Blit the arrow surface to the main surface
        surface.blit(arrow_surface, (0, 0))
    
    def is_active(self):
        """Check if arrow effect is currently active."""
        return self.active and self.duration > 0
