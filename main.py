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
                           FloatingTextManager)
from hint_item import HintItem, ArrowEffect

# Log file for debugging
log_file = open('game_debug.log', 'w', encoding='utf-8')
def log(msg):
    print(msg, file=log_file)
    log_file.flush()

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)  # Better mixer initialization

log("Mixer initialized")

# Load sounds
heartbeat_sound = None
scream_sound = None
teleport_sound = None
escape_sound = None
ambient_music_path = None

# Set up sound channels
log("Setting up sound channels...")
pygame.mixer.set_num_channels(8)
log("Sound channels configured")

try:
    heartbeat_sound = pygame.mixer.Sound('soundeffect/heartbeat.mp3')
    heartbeat_sound.set_volume(0.7)
    log("[OK] Heartbeat sound loaded")
except Exception as e:
    log(f"[ERROR] Error loading heartbeat: {e}")

try:
    scream_sound = pygame.mixer.Sound('soundeffect/scream.mp3')
    scream_sound.set_volume(0.8)
    log("[OK] Scream sound loaded")
except Exception as e:
    log(f"[ERROR] Error loading scream: {e}")

try:
    teleport_sound = pygame.mixer.Sound('soundeffect/teleport.mp3')
    teleport_sound.set_volume(0.6)
    log("[OK] Teleport sound loaded")
except Exception as e:
    log(f"[ERROR] Error loading teleport: {e}")

try:
    escape_sound = pygame.mixer.Sound('soundeffect/escape.mp3')
    escape_sound.set_volume(0.7)
    log("[OK] Escape sound loaded")
except Exception as e:
    log(f"[ERROR] Error loading escape: {e}")

# Load ambient music using pygame.mixer.music instead of Sound
try:
    ambient_music_path = 'soundeffect/(Free) Horror Ambiance - Ominous Background Music.mp3'
    log("[OK] Ambient music ready")
except Exception as e:
    log(f"[ERROR] Error loading ambient music: {e}")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Runner - Escape the Maze!")
clock = pygame.time.Clock()

# Enhanced visual effects
screen_shake = ScreenShake()
floating_text_manager = FloatingTextManager()
portal_glow = GlowEffect(base_alpha=120, pulse_range=100, pulse_speed=0.08)
escape_glow = GlowEffect(base_alpha=150, pulse_range=80, pulse_speed=0.1)
arrow_effect = ArrowEffect()  # Arrow hint effect

# Message display system
message_text = ""
message_timer = 0
message_duration = 0

def set_message(text, duration=120):  # duration in frames
    global message_text, message_timer, message_duration
    message_text = text
    message_timer = duration
    message_duration = duration

# Define game states
game_state = "menu"  # "menu", "playing", "game_over", "game_won"

# Define buttons for main menu
start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, 200, 60)
stats_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 60)

# Define buttons for game over screen
retry_button = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT - 80, 100, 50)
menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 80, 100, 50)
quit_button = pygame.Rect(SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT - 80, 100, 50)

player = Player()
maze = Maze()
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
stats_manager = StatsManager()
stats_visualizer = StatsVisualizer()

level = 1
score = 0
visible_radius = 250
game_state = "menu"  # "menu", "playing", "game_over", "game_won"
show_stats = False  # Toggle stats view with 'S' key
steps_count = 0
enemies_encountered_count = 0
encountered_enemies = set()  # Track which enemies have been encountered
game_start_time = 0
game_end_time = 0  # Add this line
previous_player_pos = (TILE_SIZE, TILE_SIZE)
previous_player_grid = (TILE_SIZE // TILE_SIZE, TILE_SIZE // TILE_SIZE)
levels_completed = 0

# Heartbeat effect variables
heartbeat_timer = 0
heartbeat_interval = 90  # Frames between heartbeats

# Ambient music variable
ambient_playing = False

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
    global enemies, portals, escape_door, hint_items
    # Calculate difficulty based on level
    if level >= 5:
        enemy_count = 3  # Only 3 enemies in final level
    else:
        enemy_count = 0
    portal_count = max(3 - level, 1)
    enemy_speed = 1.5 + level * 0.06

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
        escape_min_distance = TILE_SIZE * 12  # Much farther for level 3+
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
    
    # Create hint items (1-4 per level)
    hint_item_count = min(1 + level // 3, 3)
    hint_items = [HintItem(maze) for _ in range(hint_item_count)]

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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Handle stats menu clicks (priority over everything else)
            if show_stats:
                stats_visualizer.handle_click(mouse_x, mouse_y)
            # Handle main menu clicks
            elif game_state == "menu":
                if start_button.collidepoint(mouse_x, mouse_y):
                    game_state = "playing"
                    game_start_time = time.time()
                    maze.regenerate()
                    player.x = TILE_SIZE
                    player.y = TILE_SIZE
                    level = 1
                    score = 0
                    visible_radius = 260
                    steps_count = 0
                    enemies_encountered_count = 0
                    encountered_enemies = set()
                    levels_completed = 0
                    previous_player_grid = (1, 1)
                    arrow_effect = ArrowEffect()
                    spawn_entities()
                    # Start ambient music
                    try:
                        pygame.mixer.music.load(ambient_music_path)
                        pygame.mixer.music.set_volume(0.5)  # 50% volume for ambience
                        pygame.mixer.music.play(-1)  # -1 for infinite loop
                        ambient_playing = True
                        log("[OK] Ambient music playing")
                    except Exception as e:
                        log(f"[ERROR] Error playing ambient music: {e}")
                elif stats_button.collidepoint(mouse_x, mouse_y):
                    show_stats = True
            # Handle game over/won clicks
            elif game_state == "game_over" or game_state == "game_won":
                if retry_button.collidepoint(mouse_x, mouse_y):
                    # Reset game
                    game_state = "playing"
                    level = 1
                    score = 0
                    visible_radius = 280
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
                    arrow_effect = ArrowEffect()  # Reset arrow effect
                    spawn_entities()
                    # Restart ambient music
                    try:
                        pygame.mixer.music.load(ambient_music_path)
                        pygame.mixer.music.set_volume(0.5)
                        pygame.mixer.music.play(-1)
                        ambient_playing = True
                    except Exception as e:
                        log(f"[ERROR] Error playing ambient music on retry: {e}")
                elif menu_button.collidepoint(mouse_x, mouse_y):
                    # Return to main menu
                    game_state = "menu"
                    # Stop ambient music
                    pygame.mixer.music.stop()
                    ambient_playing = False
                elif quit_button.collidepoint(mouse_x, mouse_y):
                    running = False

    if game_state == "playing":
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
                portal.teleport_player(player, portals_to_avoid=portals, escape_door=escape_door)
                set_message("You been teleported!", 120)
                if teleport_sound:
                    teleport_sound.play()

        # Check hint item collision
        for hint_item in hint_items:
            if hint_item.check_collision(player):
                arrow_effect.activate()
                set_message("Arrow shows the way!", 120)
                floating_text_manager.add(player.x, player.y, "Hint: Exit revealed!", 
                                        color=(0, 255, 0), duration=60, font_size=20)

        # check escape door collision
        if escape_door.check_collision(player) and game_state == "playing":
            # Play escape sound effect
            if escape_sound:
                escape_sound.play()
            
            if level >= 5:  # Player has reached final level
                if game_state != "game_won":  # Only record once per game
                    game_state = "game_won"
                    game_end_time = time.time()
                    # Stop ambient music
                    pygame.mixer.music.stop()
                    ambient_playing = False
                    score += 200  # Bonus points for winning
                    elapsed_time = int(game_end_time - game_start_time)
                    stats_manager.record_game(steps_count, elapsed_time, enemies_encountered_count, score, 'Win', levels_completed)
                    stats_visualizer.refresh_data()  # Update stats visualization immediately
            else:
                level += 1
                levels_completed += 1
                score += 100
                set_message(f"You've escaped level {level - 1}!", 120)
                if level % 3 == 0:
                    visible_radius = max(100, visible_radius - 50)
                encountered_enemies = set()  # Reset enemy encounters for new level
                arrow_effect = ArrowEffect()  # Reset arrow effect for new level
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
        arrow_effect.update()  # Update arrow effect

        # check enemy collision with player
        enemy_nearby = False
        min_enemy_distance = float('inf')
        for enemy in enemies:
            distance = enemy.distance_to_player(player)
            if distance < min_enemy_distance:
                min_enemy_distance = distance
            
            if enemy.collides_with_player(player):
                if game_state != "game_over":  # Only record once per game
                    game_state = "game_over"
                    game_end_time = time.time()  # Store the exact time of death
                    # Play scream sound when caught
                    if scream_sound:
                        scream_sound.play()
                    # Stop ambient music
                    pygame.mixer.music.stop()
                    ambient_playing = False
                    # Add dramatic particle effect
                    floating_text_manager.add(player.x, player.y, "CAUGHT!", 
                                            color=(255, 0, 0), duration=60, font_size=36)
                    elapsed_time = int(game_end_time - game_start_time)  # Calculate once
                    stats_manager.record_game(steps_count, elapsed_time, enemies_encountered_count, score, 'Loss', levels_completed)
                    stats_visualizer.refresh_data()  # Update stats visualization immediately
                    screen_shake.start(8, 20)  # Intense shake on death
                    screen_shake.stop()  # Stop shake immediately for game over screen
                break
            
            # Track enemy encounters when they detect the player
            if distance < 300:  # Detection range
                enemy_nearby = True
                # Check if this is a new enemy encounter
                enemy_id = id(enemy)  # Use object id to uniquely identify each enemy
                if enemy_id not in encountered_enemies:
                    encountered_enemies.add(enemy_id)
                    enemies_encountered_count += 1
                    # Show visual feedback for new enemy encounter
                    floating_text_manager.add(player.x, player.y, "Enemy!", 
                                            color=(255, 100, 0), duration=30, font_size=20)

        # Heartbeat effect - speed up as enemies get closer
        if enemy_nearby and game_state == "playing":
            # Adjust heartbeat interval based on enemy distance (closer = faster)
            if min_enemy_distance < 150:
                heartbeat_interval = 25  # Very fast
            elif min_enemy_distance < 200:
                heartbeat_interval = 40  # Fast
            else:
                heartbeat_interval = 60  # Normal
            
            heartbeat_timer += 1
            if heartbeat_timer >= heartbeat_interval:
                if heartbeat_sound:
                    heartbeat_sound.play()
                heartbeat_timer = 0
            screen_shake.start(2, 5)  # Subtle shake when detected
        else:
            heartbeat_timer = 0  # Reset when no enemies nearby
    
    # Only draw game world when actually playing
    if game_state == "playing":
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
    
        # Different appearance for level 5 - looks like an actual exit door
        if level >= 5:
            # Draw exit door as rectangular door with red/ominous glow
            door_width, door_height = 50, 70
        
            # Render red glow layers for final level
            for layer in range(3, 0, -1):
                layer_size = max(door_width, door_height) + (layer * 15)
                layer_alpha = max(40, escape_alpha - (layer * 25))
                glow_surface = pygame.Surface((layer_size, layer_size), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 100, 100, layer_alpha), 
                                 (layer_size // 2, layer_size // 2), layer_size // 2)
                screen.blit(glow_surface, (escape_draw_x - layer_size // 2, 
                                          escape_draw_y - layer_size // 2))
        
            # Draw door frame (dark red/brown)
            pygame.draw.rect(screen, (150, 30, 30), 
                            (escape_draw_x - door_width // 2, escape_draw_y - door_height // 2, door_width, door_height))
            pygame.draw.rect(screen, (200, 100, 100), 
                            (escape_draw_x - door_width // 2, escape_draw_y - door_height // 2, door_width, door_height), 3)
        
            # Draw door details (handle, hinges)
            pygame.draw.circle(screen, (255, 200, 0), 
                              (escape_draw_x + door_width // 4, escape_draw_y), 4)
        
            # Add inner glow
            pygame.draw.rect(screen, (255, 150, 100), 
                            (escape_draw_x - door_width // 2 + 5, escape_draw_y - door_height // 2 + 10, 
                             door_width - 10, door_height - 20), 2)
        else:
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

        # Draw hint items
        for hint_item in hint_items:
            if not hint_item.collected:
                hint_draw_x, hint_draw_y = camera.apply(hint_item.x, hint_item.y)
            
                # Draw hint item as a shining diamond shape
                # Draw glow
                glow_size = 35
                pygame.draw.circle(screen, (200, 50, 200, 100), (hint_draw_x, hint_draw_y), glow_size)
            
                # Draw main item
                item_size = 15
                points = [
                    (hint_draw_x, hint_draw_y - item_size),  # top
                    (hint_draw_x + item_size, hint_draw_y),  # right
                    (hint_draw_x, hint_draw_y + item_size),  # bottom
                    (hint_draw_x - item_size, hint_draw_y),  # left
                ]
                pygame.draw.polygon(screen, (200, 50, 200), points)
                pygame.draw.polygon(screen, (150, 30, 150), points, 2)
            
                # Draw inner glow
                pygame.draw.circle(screen, (255, 150, 255), (hint_draw_x, hint_draw_y), 5)

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

        # Draw arrow hint effect pointing to escape door
        arrow_effect.draw(screen, player, escape_door, camera)

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
        for i in range(int(visible_radius), 0, -30):
            alpha = int(200 * (1 - i / visible_radius))
            pygame.draw.circle(fog_surface, (0, 0, 0, alpha), (center_x, center_y), i)
    
        # Add slight fog texture
        fog_surface.fill((0, 0, 0,230))
        pygame.draw.circle(fog_surface, (0, 0, 0, 0), (center_x, center_y), visible_radius)
        screen.blit(fog_surface, (0, 0))
    
        # Draw visibility ring indicator
        pygame.draw.circle(screen, (100, 100, 150, 100), (center_x, center_y), visible_radius, 2)

        # Draw level text with enhanced HUD (after fog effect so it's visible)
        font = pygame.font.SysFont('arial', 24, bold=True)
        if game_state == "game_over" or game_state == "game_won":
            elapsed_time = int(game_end_time - game_start_time)  # Use stored end time
        else:
            elapsed_time = int(time.time() - game_start_time)  # Live update while playing
    
        # Special message for level 5
        if level >= 5 and game_state == "playing":
            level_text = font.render("Level 5: FIND THE EXIT DOOR", True, (255, 100, 100))
        else:
            level_text = font.render(f"Level: {level}  Score: {score}  Steps: {steps_count}  Time: {elapsed_time}s", True, (255, 255, 255))
    
        # Add background to HUD for better readability
        hud_bg = pygame.Surface((SCREEN_WIDTH - 20, 40), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 100))
        screen.blit(hud_bg, (10, 5))
        pygame.draw.rect(screen, (100, 200, 255), (10, 5, SCREEN_WIDTH - 20, 40), 2)
        screen.blit(level_text, (15, 12))

        # Add dark red atmosphere for level 5
        if level >= 5 and game_state == "playing":
            red_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            red_overlay.fill((139, 20, 20, 80))  # Dark red tint
            screen.blit(red_overlay, (0, 0))

    if game_state == "game_over":
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
        
        stat_y = SCREEN_HEIGHT // 2 + 30
        for stat in stats_data:
            stat_text = stats_font.render(stat, True, (200, 200, 200))
            stat_x = SCREEN_WIDTH // 2 - stat_text.get_width() // 2
            screen.blit(stat_text, (stat_x, stat_y))
            stat_y += 35

        # Enhanced buttons
        button_font = pygame.font.SysFont('arial', 32, bold=True)
        retry_text = button_font.render("Retry", True, (0, 0, 0))
        menu_text = button_font.render("Menu", True, (0, 0, 0))
        quit_text = button_font.render("Quit", True, (0, 0, 0))

        # Draw button backgrounds with glow
        for button, text_surface, color in [(retry_button, retry_text, (0, 255, 0)), 
                                            (menu_button, menu_text, (100, 200, 255)),
                                            (quit_button, quit_text, (255, 0, 0))]:
            # Glow effect
            glow_color = (100, 255, 100, 80) if button == retry_button else (100, 180, 255, 80) if button == menu_button else (255, 100, 100, 80)
            glow_surface = pygame.Surface((button.width + 6, button.height + 6), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, button.width + 6, button.height + 6), border_radius=8)
            screen.blit(glow_surface, (button.x - 3, button.y - 3))
            
            # Button
            pygame.draw.rect(screen, color, button, border_radius=8)
            border_color = (100, 255, 100) if button == retry_button else (150, 220, 255) if button == menu_button else (255, 100, 100)
            pygame.draw.rect(screen, border_color, button, 3, border_radius=8)
            
            # Text
            text_x = button.x + (button.width - text_surface.get_width()) // 2
            text_y = button.y + (button.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))

    if game_state == "game_won":
        # Enhanced winning screen with dark red atmosphere
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((139, 20, 20, 180))  # Dark red overlay
        screen.blit(overlay, (0, 0))
        
        # Winning text with glow
        font = pygame.font.SysFont('arial', 72, bold=True)
        win_text = font.render("YOU HAVE ESCAPED", True, (255, 200, 100))
        text_x = SCREEN_WIDTH // 2 - win_text.get_width() // 2
        text_y = SCREEN_HEIGHT // 2 - 200
        
        # Draw glowing effect for winning text
        for i in range(5, 0, -1):
            glow_text = font.render("YOU HAVE ESCAPED", True, (255, 150, 0))
            glow_text.set_alpha(50 - i * 10)
            screen.blit(glow_text, (text_x + i, text_y + i))
        
        screen.blit(win_text, (text_x, text_y))

        # Score and stats
        score_font = pygame.font.SysFont('arial', 40, bold=True)
        score_text = score_font.render(f"Final Score: {score}", True, (255, 200, 100))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

        # Display game stats
        stats_font = pygame.font.SysFont('arial', 24)
        elapsed_time = int(game_end_time - game_start_time)
        
        stats_data = [
            f"Levels Completed: {levels_completed}",
            f"Steps: {steps_count}",
            f"Time: {elapsed_time}s",
            f"Enemies Encountered: {enemies_encountered_count}"
        ]
        
        stat_y = SCREEN_HEIGHT // 2 + 15
        for stat in stats_data:
            stat_text = stats_font.render(stat, True, (200, 200, 200))
            stat_x = SCREEN_WIDTH // 2 - stat_text.get_width() // 2
            screen.blit(stat_text, (stat_x, stat_y))
            stat_y += 35

        # Enhanced buttons
        button_font = pygame.font.SysFont('arial', 32, bold=True)
        retry_text = button_font.render("Retry", True, (0, 0, 0))
        menu_text = button_font.render("Menu", True, (0, 0, 0))
        quit_text = button_font.render("Quit", True, (0, 0, 0))

        # Draw button backgrounds with glow
        for button, text_surface, color in [(retry_button, retry_text, (255, 150, 0)), 
                                            (menu_button, menu_text, (100, 200, 255)),
                                            (quit_button, quit_text, (255, 0, 0))]:
            # Glow effect
            glow_color = (255, 180, 100, 80) if button == retry_button else (100, 180, 255, 80) if button == menu_button else (255, 100, 100, 80)
            glow_surface = pygame.Surface((button.width + 6, button.height + 6), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, button.width + 6, button.height + 6), border_radius=8)
            screen.blit(glow_surface, (button.x - 3, button.y - 3))
            
            # Button
            pygame.draw.rect(screen, color, button, border_radius=8)
            border_color = (255, 200, 100) if button == retry_button else (150, 220, 255) if button == menu_button else (255, 100, 100)
            pygame.draw.rect(screen, border_color, button, 3, border_radius=8)
            
            # Text
            text_x = button.x + (button.width - text_surface.get_width()) // 2
            text_y = button.y + (button.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))

    # Draw main menu if in menu state
    if game_state == "menu":
        # Dark background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        # Title text with glow
        title_font = pygame.font.SysFont('arial', 72, bold=True)
        title_text = title_font.render("HORROR MAZE ESCAPE", True, (0, 255, 150))
        title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
        title_y = SCREEN_HEIGHT // 2 - 150
        
        # Draw glowing effect for title
        for i in range(5, 0, -1):
            glow_text = title_font.render("HORROR MAZE ESCAPE", True, (0, 200, 150))
            glow_text.set_alpha(50 - i * 10)
            screen.blit(glow_text, (title_x + i, title_y + i))
        
        screen.blit(title_text, (title_x, title_y))
        
        # Subtitle
        subtitle_font = pygame.font.SysFont('arial', 28)
        subtitle_text = subtitle_font.render("Escape the Maze!", True, (100, 255, 200))
        subtitle_x = SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2
        screen.blit(subtitle_text, (subtitle_x, title_y + 90))
        
        # Instructions
        instruction_font = pygame.font.SysFont('arial', 15)
        instructions = [
            "Use WASD to move",
            "Avoid the killer enemies",
            "Find the yellow portal to escape",
            "Press Z to view stats"
        ]
        
        instr_y = SCREEN_HEIGHT // 2 + 150
        for instruction in instructions:
            instr_text = instruction_font.render(instruction, True, (150, 200, 255))
            instr_x = SCREEN_WIDTH // 2 - instr_text.get_width() // 2
            screen.blit(instr_text, (instr_x, instr_y))
            instr_y += 20
        
        # Draw start button with glow
        button_font = pygame.font.SysFont('arial', 28, bold=True)
        start_text = button_font.render("START GAME", True, (0, 0, 0))
        
        # Glow effect
        glow_surface = pygame.Surface((start_button.width + 6, start_button.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (100, 255, 150, 100), (0, 0, start_button.width + 6, start_button.height + 6), border_radius=10)
        screen.blit(glow_surface, (start_button.x - 3, start_button.y - 3))
        
        # Button
        pygame.draw.rect(screen, (0, 255, 100), start_button, border_radius=10)
        pygame.draw.rect(screen, (100, 255, 150), start_button, 4, border_radius=10)
        
        # Text
        text_x = start_button.x + (start_button.width - start_text.get_width()) // 2
        text_y = start_button.y + (start_button.height - start_text.get_height()) // 2
        screen.blit(start_text, (text_x, text_y))
        
        # Draw stats button with glow
        stats_text = button_font.render("VIEW STATS", True, (0, 0, 0))
        
        # Glow effect
        glow_surface = pygame.Surface((stats_button.width + 6, stats_button.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (100, 150, 255, 100), (0, 0, stats_button.width + 6, stats_button.height + 6), border_radius=10)
        screen.blit(glow_surface, (stats_button.x - 3, stats_button.y - 3))
        
        # Button
        pygame.draw.rect(screen, (0, 150, 255), stats_button, border_radius=10)
        pygame.draw.rect(screen, (100, 180, 255), stats_button, 4, border_radius=10)
        
        # Text
        text_x = stats_button.x + (stats_button.width - stats_text.get_width()) // 2
        text_y = stats_button.y + (stats_button.height - stats_text.get_height()) // 2
        screen.blit(stats_text, (text_x, text_y))

    # Draw stats visualization if toggle is on (draw on top of everything)
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