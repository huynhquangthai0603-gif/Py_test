# file: gpu_cpu_parallel.py
# Chạy: python gpu_cpu_parallel.py
# Yêu cầu: pip install torch pygame

import time
import threading
import random
import pygame
import torch
import numpy as np

# --- Device setup ---
if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
print("Using device:", device)

# --- Simulation params ---
N = 3000
screen_w, screen_h = 1000, 700
radius = 3.5
physics_fps = 120.0   # physics runs at higher rate
render_fps = 60.0
g = 1200.0
restitution = 0.85

# initialize on device
pos = torch.empty((N,2), device=device).uniform_(radius, min(screen_w, screen_h)-radius)
vel = torch.empty((N,2), device=device).uniform_(-250.0, 250.0)
vel[:,1] -= 200.0

r_t = torch.tensor(radius, device=device)
sw_t = torch.tensor(screen_w, device=device)
sh_t = torch.tensor(screen_h, device=device)
g_vec = torch.tensor([0.0, g], device=device)

colors = [(random.randint(40,255), random.randint(40,255), random.randint(40,255)) for _ in range(N)]

# Shared buffer and lock
shared_positions = np.zeros((N,2), dtype=np.float32)
pos_lock = threading.Lock()
running = True

def physics_loop():
    global pos, vel, shared_positions, running
    dt = 1.0 / physics_fps
    sync_interval = 1.0 / 30.0  # gửi snapshot về CPU 30 lần/giây
    last_sync = time.time()
    while running:
        # physics step on device
        vel += g_vec * dt
        pos = pos + vel * dt

        # collisions floor
        mask_floor = pos[:,1] + r_t >= sh_t
        if mask_floor.any():
            pos[mask_floor,1] = sh_t - r_t
            vel[mask_floor,1] = -vel[mask_floor,1] * restitution
            small = mask_floor & (torch.abs(vel[:,1]) < 25.0)
            vel[small,1] = 0.0

        # walls
        left_mask = pos[:,0] - r_t <= 0
        if left_mask.any():
            pos[left_mask,0] = r_t
            vel[left_mask,0] = -vel[left_mask,0] * restitution
        right_mask = pos[:,0] + r_t >= sw_t
        if right_mask.any():
            pos[right_mask,0] = sw_t - r_t
            vel[right_mask,0] = -vel[right_mask,0] * restitution

        # friction
        on_floor = (pos[:,1] + r_t >= sh_t - 1.0)
        vel[on_floor,0] *= 0.996

        # sync positions occasionally (avoid every physics step to reduce copies)
        now = time.time()
        if now - last_sync >= sync_interval:
            last_sync = now
            pos_cpu = pos.to("cpu").numpy().astype(np.float32, copy=False)
            with pos_lock:
                shared_positions[:, :] = pos_cpu[:, :]

        # sleep to maintain physics fps (coarse)
        time.sleep(max(0.0, dt * 0.9))

# Start physics thread
phy_thread = threading.Thread(target=physics_loop, daemon=True)
phy_thread.start()

# Pygame render loop (main thread)
pygame.init()
screen = pygame.display.set_mode((screen_w, screen_h))
clock = pygame.time.Clock()

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                raise KeyboardInterrupt

        # draw snapshot
        with pos_lock:
            snapshot = shared_positions.copy()

        screen.fill((10,10,20))
        for i in range(N):
            x, y = snapshot[i]
            pygame.draw.circle(screen, colors[i], (int(x), int(y)), int(radius))
        pygame.display.flip()
        clock.tick(render_fps)
except KeyboardInterrupt:
    pass
finally:
    running = False
    phy_thread.join(timeout=1.0)
    pygame.quit()