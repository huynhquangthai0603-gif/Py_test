import pygame
import numpy as np
import random

class Ball:
    def __init__(self, position, velocity):
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(velocity, dtype=np.float32)
        self.color = (random.randint(0,255),
                      random.randint(0,255),
                      random.randint(0,255))
        self.radius = 20

def gravity(obj):
    obj.velocity[1] += g

def bounce_wall(obj):
    if obj.position[1] + obj.radius >= screen_height:
        obj.position[1] = screen_height - obj.radius
        touch_p = np.array([obj.position[0], screen_height], dtype=np.float32)
        d = touch_p - obj.position
        t = np.array([-d[1], d[0]], dtype=np.float32)
        v_to_t = (np.dot(obj.velocity, t) / np.dot(t, t)) * t
        obj.velocity = ((2 * v_to_t - obj.velocity) * 0.8)
        if abs(obj.velocity[1]) < 1:
            obj.position[1] = screen_height - obj.radius
            obj.velocity[1] = 0
    elif obj.position[0] + obj.radius >= screen_width:
        obj.position[0] = screen_width - obj.radius
        touch_p = np.array([screen_width, obj.position[1]], dtype=np.float32)
        d = touch_p - obj.position
        t = np.array([-d[1], d[0]], dtype=np.float32)
        v_to_t = (np.dot(obj.velocity, t) / np.dot(t, t)) * t
        obj.velocity = ((2 * v_to_t - obj.velocity) * 0.8)
    elif obj.position[0] - obj.radius <= 0:
        obj.position[0] = obj.radius
        touch_p = np.array([0, obj.position[1]], dtype=np.float32)
        d = touch_p - obj.position
        t = np.array([-d[1], d[0]], dtype=np.float32)
        v_to_t = (np.dot(obj.velocity, t) / np.dot(t, t)) * t
        obj.velocity = ((2 * v_to_t - obj.velocity) * 0.8)

'''def bounce_ball(obj):
    for i in range(len(balls)):
        for j in range(i+1, len(balls)):'''


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
        '''if event.type == pygame.VIDEORESIZE:
            resize_event = event
            #screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)'''
        if event.type == pygame.MOUSEBUTTONDOWN:
            balls.append(Ball(np.array(event.pos, dtype=np.float32),
                              np.array([random.randint(-10,10), -10.0], dtype=np.float32)))
    screen.fill((0,0,0))
    for ball in balls:
        bounce_wall(ball)
        gravity(ball)
        ball.position += ball.velocity
        pygame.draw.circle(screen, ball.color, ball.position.astype(int), ball.radius)
        if is_out(ball):
            balls.remove(ball)
            #balls.append(Ball([screen_width/2, screen_height/4],
             #                 [random.randint(-10,10), random.randint(-10, 10)]))
            '''balls.append(Ball([screen_width / 2, screen_height / 2 - 200],
                              [random.randint(-10, 10), random.randint(-10, 10)]))'''
    pygame.display.flip()
    clock.tick(60)
pygame.quit()








