import pygame
import random
import math
import time

WIDTH, HEIGHT = 800, 600
FPS = 60

BLACK = (0, 0, 0,)
SMOKE_COLORS = [(60, 60, 60), (80, 80, 80), (100, 100, 100), (120, 120, 120)]

# --- Smoke particles ---
class SmokeParticle:
    def __init__(self, pos, size=None, alpha=255, life=90):
        self.x, self.y = pos
        self.radius = size if size else random.randint(6, 16)
        self.life = life
        self.max_life = life
        self.color = random.choice(SMOKE_COLORS)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.3, 0.3)
        self.alpha = alpha

    def update(self):
        self.life -= 1
        self.x += self.vx
        self.y += self.vy
        self.radius += 0.75

    def draw(self, screen):
        fade = int(self.alpha * (self.life / self.max_life))
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, fade), (int(self.radius), int(self.radius)), int(self.radius))
        screen.blit(surf, (self.x - self.radius, self.y - self.radius))

# --- Flash Effect ---
class Flash:
    def __init__(self, pos):
        self.x, self.y = pos
        self.life = 12
        self.radius = 50

    def update(self):
        self.life -= 1
        self.radius += 3

    def draw(self, screen):
        alpha = int(255 * (self.life / 12))
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, alpha), (self.radius, self.radius), self.radius)
        screen.blit(surf, (self.x - self.radius, self.y - self.radius))

# --- Secondary Particle ---
class ChildParticle:
    def __init__(self, pos, color):
        self.x, self.y = pos
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.radius = 5
        self.spawn_time = time.time()
        self.exploded = False
        self.trail_timer = 0
    
    def update(self, smoke_list, flash_list):
        if not self.exploded:
            self.x += self.vx
            self.y += self.vy
            self.vx *= 0.98
            self.vy *= 0.98

            # Trail smoke -- smaller and more transparent
            self.trail_timer += 1
            if self.trail_timer % 4 == 0:
                smoke_list.append(SmokeParticle(
                    (self.x, self.y),
                    size=random.randint(2, 4),
                    alpha=100,
                    life=40
                ))

            # After time(2) in seconds, explode 
            if time.time() - self.spawn_time > 2:
                self.exploded = True
                flash_list.append(Flash((self.x, self.y)))

                # Main smoke puff
                smoke_list.append(SmokeParticle(
                    (self.x, self.y),
                    size=14,
                    alpha=200,
                    life=90
                ))

                # Dotted cloud busts
                for _ in range(6):
                    offset = (
                        self.x + random.uniform(-14, 14),
                        self.y + random.uniform(-14, 14),
                    )
                    smoke_list.append(SmokeParticle(
                        offset,
                        size=random.randint(4, 18),
                        alpha=random.randint(80, 150),
                        life=random.randint(60, 100)
                    ))

    def draw(self, screen):
        if not self.exploded:
            surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, 220), (self.radius, self.radius), self.radius)
            screen.blit(surf, (self.x - self.radius, self.y - self.radius))

# --- Grenade/Ball object ---
class GrenadeBall:
    def __init__(self, pos):
        self.x, self.y = pos
        self.color = [random.randint(150, 255) for _ in range(3)]
        self.radius = 16
        self.spawn_time = time.time()
        self.exploded = False

    def update(self, child_list):
        if time.time() - self.spawn_time > 3 and not self.exploded:
            self.exploded = True
            for _ in range (20):
                child_list.append(ChildParticle((self.x, self.y), self.color))

    def draw(self, screen):
        if not self.exploded:
            pulse = math.sin(time.time() * 4) * 2
            surf = pygame.Surface((self.radius * 2 + 4, self.radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, 200), (self.radius + 2, self.radius + 2), int(self.radius + pulse))
            screen.blit(surf, (self.x - self.radius - 2, self.y - self.radius - 2))

# --- Main Game Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Explosion Test")
    clock = pygame.time.Clock()

# Uncomment the two lines below to use a solid black background
    # background_img = pygame.Surface((WIDTH, HEIGHT))
    # background_img.fill(BLACK)

    # Comment out the two lines below if not using an image
    background_img = pygame.image.load("doll.png").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

    grenades = []
    children = []
    smoke = []
    flashes = []

    running =  True
    while running:
        clock.tick(FPS)
        screen.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                grenades.append(GrenadeBall(pygame.mouse.get_pos()))

        for g in grenades:
            g.update(children)
            g.draw(screen)

        for c in children[:]:
            c.update(smoke, flashes)
            c.draw(screen)
            if c.exploded:
                children.remove(c)

        for f in flashes[:]:
            f.update()
            f.draw(screen)
            if f.life <= 0:
                flashes.remove(f)

        for s in smoke[:]:
            s.update()
            s.draw(screen)
            if s.life <= 0:
                smoke.remove(s)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()