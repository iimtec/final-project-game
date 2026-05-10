import pygame
import math
import random

class ParticleEffect:
    """A single particle with position, velocity, lifetime, and color."""
    def __init__(self, x, y, vx, vy, lifetime, color, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.gravity = 0.1
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
    
    def draw(self, surface, offset_x=0, offset_y=0):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
            pygame.draw.circle(surface, self.color, 
                             (int(self.x + offset_x), int(self.y + offset_y)), size)
    
    def is_alive(self):
        return self.lifetime > 0


class ParticleEmitter:
    """Manages a group of particles."""
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, count, vx_range=(-2, 2), vy_range=(-2, 2), 
             lifetime=30, color=(255, 255, 255), size=3):
        for _ in range(count):
            vx = random.uniform(vx_range[0], vx_range[1])
            vy = random.uniform(vy_range[0], vy_range[1])
            particle = ParticleEffect(x, y, vx, vy, lifetime, color, size)
            self.particles.append(particle)
    
    def update(self):
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
    
    def draw(self, surface, offset_x=0, offset_y=0):
        for particle in self.particles:
            particle.draw(surface, offset_x, offset_y)
    
    def clear(self):
        self.particles.clear()


class GlowEffect:
    """Creates a pulsing glow effect."""
    def __init__(self, base_alpha=100, pulse_range=80, pulse_speed=0.08):
        self.base_alpha = base_alpha
        self.pulse_range = pulse_range
        self.pulse_speed = pulse_speed
        self.timer = 0
    
    def get_alpha(self):
        self.timer += self.pulse_speed
        alpha = self.base_alpha + self.pulse_range * math.sin(self.timer)
        return max(0, min(255, int(alpha)))
    
    def reset(self):
        self.timer = 0


# class ShadowEffect:
#     """Creates a drop shadow effect."""
#     @staticmethod
#     def draw_shadow(surface, x, y, width, height, offset_x=3, offset_y=3, 
#                    color=(0, 0, 0), alpha=100):
#         shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
#         shadow_surface.fill((color[0], color[1], color[2], alpha))
#         surface.blit(shadow_surface, (x + offset_x, y + offset_y))


# class LightEffect:
#     """Creates a dynamic light/illumination effect."""
#     def __init__(self, x, y, radius, color=(255, 255, 255), intensity=200):
#         self.x = x
#         self.y = y
#         self.radius = radius
#         self.color = color
#         self.intensity = intensity
#         self.flicker_timer = 0
#         self.flicker = False
    
#     def update(self, new_x, new_y):
#         self.x = new_x
#         self.y = new_y
#         self.flicker_timer += 1
#         if self.flicker_timer % 15 == 0:
#             self.flicker = random.random() > 0.7
    
#     def draw(self, surface, offset_x=0, offset_y=0):
#         if not self.flicker or random.random() > 0.3:
#             draw_x = int(self.x + offset_x)
#             draw_y = int(self.y + offset_y)
            
#             # Draw multiple circles for a soft glow
#             for i in range(3):
#                 radius = self.radius - (i * self.radius // 3)
#                 alpha = int(self.intensity * (1 - i / 3) * 0.6)
#                 glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
#                 pygame.draw.circle(glow_surface, 
#                                  (*self.color, alpha),
#                                  (radius, radius), radius)
#                 surface.blit(glow_surface, 
#                            (draw_x - radius, draw_y - radius))


class ScreenShake:
    """Screen shake effect with decay."""
    def __init__(self):
        self.intensity = 0
        self.duration = 0
    
    def start(self, intensity=5, duration=10):
        self.intensity = intensity
        self.duration = duration
    
    def stop(self):
        """Immediately stop the screen shake effect."""
        self.intensity = 0
        self.duration = 0
    
    def update(self):
        if self.duration > 0:
            self.duration -= 1
            self.intensity = max(0, self.intensity * 0.95)
    
    def get_offset(self):
        if self.duration > 0:
            offset_x = random.randint(-int(self.intensity), int(self.intensity))
            offset_y = random.randint(-int(self.intensity), int(self.intensity))
            return offset_x, offset_y
        return 0, 0
    
    def is_active(self):
        return self.duration > 0


class FloatingText:
    """Floating damage/healing/score text."""
    def __init__(self, x, y, text, color=(255, 255, 255), duration=60, font_size=24):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.max_duration = duration
        self.font = pygame.font.SysFont('arial', font_size, bold=True)
        self.vy = -1  # Upward velocity
    
    def update(self):
        self.y += self.vy
        self.duration -= 1
    
    def draw(self, surface, offset_x=0, offset_y=0):
        if self.duration > 0:
            alpha = int(255 * (self.duration / self.max_duration))
            # Create text with alpha
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(alpha)
            surface.blit(text_surface, 
                        (int(self.x + offset_x), int(self.y + offset_y)))
    
    def is_alive(self):
        return self.duration > 0


class FloatingTextManager:
    """Manages multiple floating text effects."""
    def __init__(self):
        self.texts = []
    
    def add(self, x, y, text, color=(255, 255, 255), duration=60, font_size=24):
        self.texts.append(FloatingText(x, y, text, color, duration, font_size))
    
    def update(self):
        self.texts = [t for t in self.texts if t.is_alive()]
        for text in self.texts:
            text.update()
    
    def draw(self, surface, offset_x=0, offset_y=0):
        for text in self.texts:
            text.draw(surface, offset_x, offset_y)
