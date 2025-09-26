import pygame
import numpy as np
import random

from typing_extensions import overload


class Ball:
    def __init__(self, position, velocity):
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(velocity, dtype=np.float32)
        self.color = (random.randint(0,255),
                      random.randint(0,255),
                      random.randint(0,255))
        self.radius = 20
        self.touched = False

def gravity(obj):
    obj.velocity[1] += g

def bounce_wall(obj):
    obj.touched = False
    #ground
    if obj.position[1] + obj.radius >= screen_height:
        obj.position[1] = screen_height - obj.radius
        touch_p = np.array([obj.position[0], screen_height], dtype=np.float32)
        obj.touched = True
    #right_sceen
    '''if obj.position[0] + obj.radius >= screen_width:
        obj.position[0] = screen_width - obj.radius
        touch_p = np.array([screen_width, obj.position[1]], dtype=np.float32)
        obj.touched = True
    #left_sceen
    if obj.position[0] - obj.radius <= 0:
        obj.position[0] = obj.radius
        touch_p = np.array([0, obj.position[1]], dtype=np.float32)
        obj.touched = True'''

    if obj.touched:
        d = touch_p - obj.position
        t = np.array([-d[1], d[0]], dtype=np.float32)
        v_to_t = (np.dot(obj.velocity, t) / np.dot(t, t)) * t
        obj.velocity = ((2 * v_to_t - obj.velocity) * 0.8)
        if abs(obj.velocity[1]) < 1:
            obj.velocity[1] = 0

def bounce_ball(obj, balls, index):
    obj.touched = False
    for i in range(index + 1, len(balls)):
        distant_vector = obj.position - balls[i].position
        distant = np.linalg.norm(distant_vector)
        if distant == 0:
            distant = 0.1
        d_unit_vector = distant_vector / distant
        if distant <= obj.radius + balls[i].radius:
            #reposition
            overlap = (obj.radius + balls[i].radius - distant) / 2
            obj.position += d_unit_vector * overlap
            balls[i].position -= d_unit_vector * overlap
            #bounce
            obj_to_d = np.dot(obj.velocity, d_unit_vector)
            balls_to_d = np.dot(balls[i].velocity, d_unit_vector)
            obj.velocity += (balls_to_d - obj_to_d) * d_unit_vector * 0.8
            balls[i].velocity += (obj_to_d -balls_to_d) * d_unit_vector * 0.8
            if np.linalg.norm(obj.velocity)  < 1:
                obj.velocity *= 0
            if np.linalg.norm(balls[i].velocity) < 1:
                balls[i].velocity *= 0
            obj.touched = True
            balls[i].touched = True

def is_out(obj):
    if obj.position[0] > screen_width + obj.radius or obj.position[0] < -obj.radius:
        return True
    elif obj.position[1] > screen_height + obj.radius:
        return True
    return False
pygame.init()
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
clock = pygame.time.Clock()
pygame.display.set_caption('Ball')
running = True
balls = []
balls = [ball for ball in balls if not is_out(ball)]
g = 0.5
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.w, event.h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        if event.type == pygame.MOUSEBUTTONDOWN:
            balls.append(Ball(np.array(event.pos, dtype=np.float32),
                              np.array([random.randint(-10,10), -10.0], dtype=np.float32)))
    screen.fill((0,0,0))
    for i, ball in enumerate(balls):
        bounce_wall(ball)
        bounce_ball(ball, balls, i)
        if not ball.touched:
            gravity(ball)
        ball.position += ball.velocity
        pygame.draw.circle(screen, ball.color, ball.position.astype(int), ball.radius)
        if is_out(ball):
            balls.remove(ball)
            balls.append(Ball([random.randint(0,screen_width), random.randint(0,screen_height)],
                              [random.randint(-10,10), random.randint(-10, 10)]))
            balls.append(Ball([random.randint(0,screen_width), random.randint(0,screen_height)],
                              [random.randint(-10, 10), random.randint(-10, 10)]))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()








