import pygame
import numpy as np
import random
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionAll, kCGNullWindowID

# --- Ball class ---
class Ball:
    def __init__(self, position, velocity):
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(velocity, dtype=np.float32)
        self.radius = 20
        self.color = (random.randint(50,255), random.randint(50,255), random.randint(50,255))

# --- Physics ---
def gravity(ball):
    ball.velocity[1] += g

def bounce(ball, width, height):
    if ball.position[1] + ball.radius >= height:
        ball.position[1] = height - ball.radius
        ball.velocity[1] *= -0.8
    if ball.position[1] - ball.radius <= 0:
        ball.position[1] = ball.radius
        ball.velocity[1] *= -0.8
    if ball.position[0] + ball.radius >= width:
        ball.position[0] = width - ball.radius
        ball.velocity[0] *= -0.8
    if ball.position[0] - ball.radius <= 0:
        ball.position[0] = ball.radius
        ball.velocity[0] *= -0.8

# --- Get absolute window position on macOS ---
def get_window_position(title="Ball Test"):
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    for w in windows:
        owner = w.get('kCGWindowOwnerName', '')
        name = w.get('kCGWindowName', '')
        if owner == "Python" and name == title:
            bounds = w.get('kCGWindowBounds', {})
            x = bounds.get('X', 0)
            y = bounds.get('Y', 0)
            return x, y
    return 0, 0

# --- Init Pygame ---
pygame.init()
screen_width, screen_height = 800, 800
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Ball Test")
clock = pygame.time.Clock()

# --- Simulation ---
g = 0.5
balls = [Ball([random.randint(50,750), random.randint(50,750)],
              [random.randint(-5,5), -5.0]) for _ in range(10)]

resize_event = None
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            resize_event = event
        elif event.type == pygame.MOUSEBUTTONDOWN:
            balls.append(Ball(np.array(event.pos, dtype=np.float32),
                              np.array([random.randint(-5,5), -5.0])))

    # --- Handle resize / “shake” ---
    if resize_event:
        new_w, new_h = resize_event.w, resize_event.h
        delta_w = new_w - screen_width
        delta_h = new_h - screen_height

        # Apply small “shake” to all balls based on resize
        for ball in balls:
            ball.velocity[0] += random.uniform(-delta_w*0.05, delta_w*0.05)
            ball.velocity[1] += random.uniform(-delta_h*0.05, delta_h*0.05)

        screen_width, screen_height = new_w, new_h
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        resize_event = None

    # --- Update physics ---
    screen.fill((30,30,30))
    window_x, window_y = get_window_position("Ball Test")

    for ball in balls:
        gravity(ball)
        bounce(ball, screen_width, screen_height)
        ball.position += ball.velocity

        # Absolute coordinates (for reference)
        absolute_x = window_x + ball.position[0]
        absolute_y = window_y + ball.position[1]
        # print(f"Absolute: {absolute_x}, {absolute_y}")

        pygame.draw.circle(screen, ball.color, ball.position.astype(int), ball.radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()