import pygame
import random
import math
import time
from settings import *
from player import Player
from camera import Camera
from maze import Maze
from enemy import Enemy
from portal import Portal
from stats_manager import StatsManager
from visualizer import StatsVisualizer
from visual_effects import (GlowEffect, ScreenShake, 
                           FloatingTextManager, LightEffect, ShadowEffect)

pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Load sounds
try:
    heartbeat_sound = pygame.mixer.Sound('heartbeat.wav')  # Add heartbeat.wav file
    teleport_sound = pygame.mixer.Sound('teleport.wav')  # Add teleport.wav file
    game_over_music = pygame.mixer.Sound('game_over.wav')  # Add game_over.wav file
except:
    heartbeat_sound = scream_sound = teleport_sound = game_over_music = None

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Runner - Escape the Maze!")
clock = pygame.time.Clock()

# Enhanced visual effects
screen_shake = ScreenShake()
floating_text_manager = FloatingTextManager()
portal_glow = GlowEffect(base_alpha=120, pulse_range=100, pulse_speed=0.08)
escape_glow = GlowEffect(base_alpha=150, pulse_range=80, pulse_speed=0.1)

# Message display system
message_text = ""
message_timer = 0
message_duration = 0

def set_message(text, duration=120):  # duration in frames
    global message_text, message_timer, message_duration
    message_text = text
    message_timer = duration
    message_duration = duration

# Define buttons for game over screen
retry_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 80, 40)
quit_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 20, 80, 40)

player = Player()
maze = Maze()
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
stats_manager = StatsManager()
stats_visualizer = StatsVisualizer()

level = 1
score = 0
visible_radius = 300
game_over = False
show_stats = False  # Toggle stats view with 'S' key
steps_count = 0
enemies_encountered_count = 0
encountered_enemies = set()  # Track which enemies have been encountered
game_start_time = 0
game_end_time = 0  # Add this line
previous_player_pos = (TILE_SIZE, TILE_SIZE)
previous_player_grid = (TILE_SIZE // TILE_SIZE, TILE_SIZE // TILE_SIZE)
levels_completed = 0

def find_random_valid_position(maze, min_distance=0, player_start=None):
    """Find a random walkable position in the maze, optionally far from the player start."""
    attempts = 0
    while attempts < 1000:
        grid_x = random.randint(1, MAZE_WIDTH - 2)
        grid_y = random.randint(1, MAZE_HEIGHT - 2)
        if maze.grid[grid_y][grid_x] == 0:  # walkable
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
        if maze.grid[grid_y][grid_x] == 0:
            return grid_x * TILE_SIZE, grid_y * TILE_SIZE

def spawn_entities():
    global enemies, portals, escape_door
    # Calculate difficulty based on level
    enemy_count = min(0 + level, 8)
    portal_count = max(3 - level, 1)
    enemy_speed = 1.5 + level * 0.15

    # Spawn enemies
    enemies = []
    player_start = (TILE_SIZE, TILE_SIZE)
    min_distance = TILE_SIZE * 5  # Keep enemies away from player spawn
    for i in range(enemy_count):
        x, y = find_random_valid_position(maze, min_distance, player_start)
        enemy = Enemy(x, y, speed=enemy_speed)
        enemies.append(enemy)

    # Create random portals
    portals = [Portal(maze) for _ in range(portal_count)]

    # Create escape door - spawn farther away at higher levels
    if level >= 3:
        escape_min_distance = TILE_SIZE * 15  # Much farther for level 3+
    else:
        escape_min_distance = TILE_SIZE * 8   # Normal distance for levels 1-2
    
    escape_door = Portal(maze, portal_type='escape')
    # Keep regenerating escape door position until it's far enough
    while True:
        escape_door = Portal(maze, portal_type='escape')
        dx = escape_door.x - player_start[0]
        dy = escape_door.y - player_start[1]
        if math.hypot(dx, dy) >= escape_min_distance:
            break

# Initial spawn
spawn_entities()
game_start_time = time.time()

running = True
while running:
    # Enhanced background with gradient-like effect
    screen.fill((15, 10, 25))  # Deep purple-blue
    
    # Add atmospheric overlay
    for y in range(0, SCREEN_HEIGHT, 20):
        alpha = int(10 * (y / SCREEN_HEIGHT))
        overlay = pygame.Surface((SCREEN_WIDTH, 20))
        overlay.set_alpha(alpha)
        overlay.fill((0, 20, 40))
        screen.blit(overlay, (0, y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                show_stats = not show_stats  # Toggle stats view
        elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
            mouse_x, mouse_y = event.pos
            if retry_button.collidepoint(mouse_x, mouse_y):
                # Reset game
                game_over = False
                level = 1
                score = 0
                visible_radius = 400
                steps_count = 0
                enemies_encountered_count = 0
                encountered_enemies = set()  # Reset encountered enemies
                levels_completed = 0
                previous_player_grid = (1, 1)
                game_start_time = time.time()
                game_end_time = 0  # Reset end time
                maze.regenerate()  # Generate a new maze layout
                player.x = TILE_SIZE
                player.y = TILE_SIZE
                spawn_entities()
                if game_over_music:
                    game_over_music.stop()
            elif quit_button.collidepoint(mouse_x, mouse_y):
                running = False

    if not game_over:
        keys = pygame.key.get_pressed()

        player.handle_input(keys, maze)
        player.update()
        
        # Track steps (increment when player moves to a new tile)
        current_grid = (int(player.x // TILE_SIZE), int(player.y // TILE_SIZE))
        if current_grid != previous_player_grid:
            steps_count += 1
            previous_player_grid = current_grid

    # check portal collision and teleport (skip escape door)
    for portal in portals:
        if portal.check_collision(player) and portal.type != 'escape':
            portal.teleport_player(player)
            set_message("You been teleported!", 120)
            if teleport_sound:
                teleport_sound.play()

    # check escape door collision
    if escape_door.check_collision(player):
        level += 1
        levels_completed += 1
        score += 100
        set_message(f"You've escaped level {level - 1}!", 120)
        if level % 3 == 0:
            visible_radius = max(100, visible_radius - 50)
        encountered_enemies = set()  # Reset enemy encounters for new level
        maze.regenerate()  # Generate a new maze layout
        player.x = TILE_SIZE  # reset to start
        player.y = TILE_SIZE
        spawn_entities()  # respawn with new difficulty

    # update enemies
    for enemy in enemies:
        enemy.update(player, maze)

    # update camera to follow player
    camera.update(player)
    
    # Update all visual effects
    screen_shake.update()
    floating_text_manager.update()
    portal_glow.get_alpha()
    escape_glow.get_alpha()

    # check enemy collision with player
    enemy_nearby = False
    for enemy in enemies:
        if enemy.collides_with_player(player):
            if not game_over:  # Only record once per game
                game_over = True
                game_end_time = time.time()  # Store the exact time of death
                # Add dramatic particle effect
                floating_text_manager.add(player.x, player.y, "CAUGHT!", 
                                        color=(255, 0, 0), duration=60, font_size=36)
                elapsed_time = int(game_end_time - game_start_time)  # Calculate once
                stats_manager.record_game(steps_count, elapsed_time, enemies_encountered_count, score, 'Loss', levels_completed)
                screen_shake.start(8, 20)  # Intense shake on death
            break
        
        # Track enemy encounters when they detect the player
        if enemy.distance_to_player(player) < 300:  # Detection range
            enemy_nearby = True
            # Check if this is a new enemy encounter
            enemy_id = id(enemy)  # Use object id to uniquely identify each enemy
            if enemy_id not in encountered_enemies:
                encountered_enemies.add(enemy_id)
                enemies_encountered_count += 1
                # Show visual feedback for new enemy encounter
                floating_text_manager.add(player.x, player.y, "Enemy!", 
                                        color=(255, 100, 0), duration=30, font_size=20)

    # Start screen shake when enemies detect player
    if enemy_nearby and not game_over:
        screen_shake.start(2, 5)  # Subtle shake when detected
    # draw world (grid)
    maze.draw(screen, camera)

    # draw portals with enhanced pulsing glow and particles
    for portal in portals:
        portal_size = 45
        portal_draw_x, portal_draw_y = camera.apply(portal.x, portal.y)
        
        # Get pulsing glow alpha
        glow_alpha = portal_glow.get_alpha()
        
        # Render multiple glow layers for depth
        for layer in range(3, 0, -1):
            layer_size = portal_size + (layer * 15)
            layer_alpha = max(30, glow_alpha - (layer * 30))
            glow_surface = pygame.Surface((layer_size, layer_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (0, 200, 255, layer_alpha), 
                             (layer_size // 2, layer_size // 2), layer_size // 2)
            screen.blit(glow_surface, (portal_draw_x - layer_size // 2, 
                                      portal_draw_y - layer_size // 2))
        
        # Draw portal core with gradient effect
        pygame.draw.circle(screen, (0, 255, 255), 
                          (portal_draw_x, portal_draw_y), portal_size // 2)
        pygame.draw.circle(screen, (100, 255, 255), 
                          (portal_draw_x, portal_draw_y), portal_size // 2, 3)
        
        # Add inner glow
        inner_size = portal_size // 3
        pygame.draw.circle(screen, (150, 255, 255), 
                          (portal_draw_x, portal_draw_y), inner_size)
    
    # draw escape door with enhanced pulsing glow and particles
    escape_size = 45
    escape_draw_x, escape_draw_y = camera.apply(escape_door.x, escape_door.y)
    escape_alpha = escape_glow.get_alpha()
    
    # Render multiple glow layers
    for layer in range(3, 0, -1):
        layer_size = escape_size + (layer * 15)
        layer_alpha = max(40, escape_alpha - (layer * 25))
        glow_surface = pygame.Surface((layer_size, layer_size), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 200, 0, layer_alpha), 
                         (layer_size // 2, layer_size // 2), layer_size // 2)
        screen.blit(glow_surface, (escape_draw_x - layer_size // 2, 
                                  escape_draw_y - layer_size // 2))
    
    # Draw escape door core
    pygame.draw.circle(screen, (255, 255, 100), 
                      (escape_draw_x, escape_draw_y), escape_size // 2)
    pygame.draw.circle(screen, (255, 255, 0), 
                      (escape_draw_x, escape_draw_y), escape_size // 2, 3)
    
    # Add inner glow to escape door
    inner_size = escape_size // 3
    pygame.draw.circle(screen, (255, 255, 150), 
                      (escape_draw_x, escape_draw_y), inner_size)

    # draw enemies
    for enemy in enemies:
        enemy_draw_x, enemy_draw_y = camera.apply(enemy.x, enemy.y)
        enemy_image = None
        if hasattr(enemy, 'get_current_image'):
            enemy_image = enemy.get_current_image()
        if enemy_image:
            screen.blit(
                enemy_image,
                (enemy_draw_x - (enemy_image.get_width() - enemy.size) // 2,
                 enemy_draw_y - (enemy_image.get_height() - enemy.size) // 2)
            )
        else:
            enemy_size = 45
            pygame.draw.rect(
                screen,
                (255, 0, 0),  # red
                (enemy_draw_x, enemy_draw_y, enemy_size, enemy_size)
            )

    # draw player avatar
    player_image = None
    if player.images:
        frames = player.images.get(player.direction) or player.images.get('idle')
        if isinstance(frames, list) and frames:
            player_image = frames[player.frame_index % len(frames)]
        else:
            player_image = frames
    if player_image:
        screen.blit(
            player_image,
            (SCREEN_WIDTH // 2 - player_image.get_width() // 2, SCREEN_HEIGHT // 2 - player_image.get_height() // 2)
        )
    else:
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            (SCREEN_WIDTH // 2 - player.size // 2, SCREEN_HEIGHT // 2 - player.size // 2, player.size, player.size)
        )

    # draw level text with enhanced HUD
    font = pygame.font.SysFont('arial', 24, bold=True)
    if game_over:
        elapsed_time = int(game_end_time - game_start_time)  # Use stored end time
    else:
        elapsed_time = int(time.time() - game_start_time)  # Live update while playing
    level_text = font.render(f"Level: {level}  Score: {score}  Steps: {steps_count}  Time: {elapsed_time}s", True, (255, 255, 255))
    
    # Add background to HUD for better readability
    hud_bg = pygame.Surface((SCREEN_WIDTH - 20, 40), pygame.SRCALPHA)
    hud_bg.fill((0, 0, 0, 100))
    screen.blit(hud_bg, (10, 5))
    pygame.draw.rect(screen, (100, 200, 255), (10, 5, SCREEN_WIDTH - 20, 40), 2)
    screen.blit(level_text, (15, 12))

    # draw message text with enhanced styling
    if message_timer > 0:
        message_timer -= 1
        # Calculate alpha based on timer (fade out effect)
        alpha = int(255 * (message_timer / message_duration)) if message_duration > 0 else 255
        message_font = pygame.font.SysFont('arial', 36, bold=True)
        message_surface = message_font.render(message_text, True, (255, 200, 50))
        message_surface.set_alpha(alpha)
        
        # Add glow effect to message
        msg_x = SCREEN_WIDTH // 2 - 150
        msg_y = SCREEN_HEIGHT // 2 - 50
        
        # Draw message shadow
        shadow_surface = message_font.render(message_text, True, (0, 0, 0))
        shadow_surface.set_alpha(alpha // 2)
        screen.blit(shadow_surface, (msg_x + 2, msg_y + 2))
        
        # Draw main message
        screen.blit(message_surface, (msg_x, msg_y))
        
        # Add floating effect
        floating_text_manager.draw(screen, -150, -50)

    # draw fog of war with enhanced effect
    fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    # Create vignette effect
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    for i in range(int(visible_radius), 0, -20):
        alpha = int(200 * (1 - i / visible_radius))
        pygame.draw.circle(fog_surface, (0, 0, 0, alpha), (center_x, center_y), i)
    
    # Add slight fog texture
    fog_surface.fill((0, 0, 0, 180))
    pygame.draw.circle(fog_surface, (0, 0, 0, 0), (center_x, center_y), visible_radius)
    screen.blit(fog_surface, (0, 0))
    
    # Draw visibility ring indicator
    pygame.draw.circle(screen, (100, 100, 150, 100), (center_x, center_y), visible_radius, 2)

    if game_over:
        # Enhanced game over screen with background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Game over text with glow
        font = pygame.font.SysFont('arial', 56, bold=True)
        game_over_text = font.render("Game Over", True, (255, 50, 50))
        text_x = SCREEN_WIDTH // 2 - game_over_text.get_width() // 2
        text_y = SCREEN_HEIGHT // 2 - 200
        
        # Draw glowing effect
        for i in range(5, 0, -1):
            glow_text = font.render("Game Over", True, (255, 0, 0))
            glow_text.set_alpha(50 - i * 10)
            screen.blit(glow_text, (text_x + i, text_y + i))
        
        screen.blit(game_over_text, (text_x, text_y))

        # Score and stats
        score_font = pygame.font.SysFont('arial', 40, bold=True)
        score_text = score_font.render(f"Final Score: {score}", True, (255, 200, 100))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

        # Display game stats with better formatting
        stats_font = pygame.font.SysFont('arial', 24)
        final_elapsed_time = int(game_end_time - game_start_time)  # Use stored time on game over screen
        
        stats_data = [
            f"Steps: {steps_count}",
            f"Time: {final_elapsed_time}s",  # Changed from elapsed_time
            f"Enemies Encountered: {enemies_encountered_count}",
            f"Levels Completed: {levels_completed}"
        ]
        
        stat_y = SCREEN_HEIGHT // 2 + 20
        for stat in stats_data:
            stat_text = stats_font.render(stat, True, (200, 200, 200))
            stat_x = SCREEN_WIDTH // 2 - stat_text.get_width() // 2
            screen.blit(stat_text, (stat_x, stat_y))
            stat_y += 35

        # Enhanced buttons
        button_font = pygame.font.SysFont('arial', 32, bold=True)
        retry_text = button_font.render("Retry", True, (0, 0, 0))
        quit_text = button_font.render("Quit", True, (0, 0, 0))

        # Draw button backgrounds with glow
        for button, text_surface in [(retry_button, retry_text), (quit_button, quit_text)]:
            # Glow effect
            glow_surface = pygame.Surface((button.width + 6, button.height + 6), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (100, 255, 100, 80), (0, 0, button.width + 6, button.height + 6), border_radius=8)
            screen.blit(glow_surface, (button.x - 3, button.y - 3))
            
            # Button
            pygame.draw.rect(screen, (0, 255, 0) if button == retry_button else (255, 0, 0), button, border_radius=8)
            pygame.draw.rect(screen, (100, 255, 100) if button == retry_button else (255, 100, 100), button, 3, border_radius=8)
            
            # Text
            text_x = button.x + (button.width - text_surface.get_width()) // 2
            text_y = button.y + (button.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))

    # Draw stats visualization if toggle is on
    if show_stats:
        stats_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        stats_screen.fill((20, 20, 30))
        stats_visualizer.draw_all_stats(stats_screen)
        
        # Draw instruction text
        instruction_font = pygame.font.SysFont(None, 18)
        instruction_text = instruction_font.render("Press Z to close stats", True, (200, 200, 200))
        stats_screen.blit(instruction_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 30))
        
        screen.blit(stats_screen, (0, 0))

    # Apply screen shake
    shake_x, shake_y = screen_shake.get_offset()
    screen_copy = screen.copy()
    screen.fill((15, 10, 25))  # Match background color
    screen.blit(screen_copy, (shake_x, shake_y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()