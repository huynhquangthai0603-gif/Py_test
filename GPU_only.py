import pygame
import torch
import random
import numpy as np

# --- Device setup ---
if torch.backends.mps.is_available():  # Mac M1 GPU
    device = torch.device("mps")
else:
    device = torch.device("cpu")


# --- Window setup ---
screen_width = 800
screen_height = 800
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ball GPU Physics")
clock = pygame.time.Clock()

# --- Simulation parameters ---
N = 12000  # số bóng
radius = 15
g = 0.5  # trọng lực
restitution = 0.8  # hệ số nảy

# --- Tạo tensors GPU ---
# positions: (N,2), velocities: (N,2)
positions = torch.zeros((N, 2), dtype=torch.float32, device=device)
velocities = torch.zeros((N, 2), dtype=torch.float32, device=device)

# Khởi tạo vị trí ngẫu nhiên (trên nửa màn hình trên) và vận tốc
positions[:, 0] = torch.rand(N, device=device) * screen_width
positions[:, 1] = torch.rand(N, device=device) * (screen_height / 2)

velocities[:, 0] = (torch.rand(N, device=device) - 0.5) * 20
velocities[:, 1] = -torch.rand(N, device=device) * 10

# Màu sắc và radius cho render trên CPU
colors = [(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)) for _ in range(N)]

# --- Main loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Thêm bóng khi click chuột
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = torch.tensor([event.pos[0], event.pos[1]], device=device)
            vel = torch.tensor([(random.random() - 0.5) * 20, -10.0], device=device)
            # Thêm vào vị trí & vận tốc đầu danh sách
            positions = torch.cat([positions, pos.unsqueeze(0)], dim=0)
            velocities = torch.cat([velocities, vel.unsqueeze(0)], dim=0)
            colors.append((random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)))

    # --- Physics vectorized trên GPU ---
    velocities[:, 1] += g  # gravity
    positions += velocities  # update position

    # Bounce với floor
    mask_floor = positions[:, 1] + radius >= screen_height
    if mask_floor.any():
        positions[mask_floor, 1] = screen_height - radius
        velocities[mask_floor, 1] = -velocities[mask_floor, 1] * restitution
        # small velocities damping
        small_mask = mask_floor & (torch.abs(velocities[:, 1]) < 1.0)
        velocities[small_mask, 1] = 0.0

    # Bounce với walls
    mask_left = positions[:, 0] - radius <= 0
    if mask_left.any():
        positions[mask_left, 0] = radius
        velocities[mask_left, 0] = -velocities[mask_left, 0] * restitution

    mask_right = positions[:, 0] + radius >= screen_width
    if mask_right.any():
        positions[mask_right, 0] = screen_width - radius
        velocities[mask_right, 0] = -velocities[mask_right, 0] * restitution

    # --- Render trên CPU ---
    screen.fill((135, 205, 222))
    pos_cpu = positions.to("cpu").numpy()  # truyền vị trí về CPU 1 lần/frame
    for i in range(len(pos_cpu)):
        pygame.draw.circle(screen, colors[i], pos_cpu[i].astype(int), radius)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()