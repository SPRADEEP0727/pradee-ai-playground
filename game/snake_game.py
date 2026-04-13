import pygame
import random

# initialize pygame
pygame.init()

# screen size
width = 600
height = 400

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# colors
black = (0,0,0)
green = (0,255,0)
red = (255,0,0)

clock = pygame.time.Clock()

snake_block = 10
snake_speed = 15

x = width / 2
y = height / 2

x_change = 0
y_change = 0

snake_list = []
snake_length = 1

food_x = round(random.randrange(0, width - snake_block) / 10.0) * 10
food_y = round(random.randrange(0, height - snake_block) / 10.0) * 10

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x_change = -snake_block
                y_change = 0
            elif event.key == pygame.K_RIGHT:
                x_change = snake_block
                y_change = 0
            elif event.key == pygame.K_UP:
                y_change = -snake_block
                x_change = 0
            elif event.key == pygame.K_DOWN:
                y_change = snake_block
                x_change = 0

    x += x_change
    y += y_change

    screen.fill(black)

    pygame.draw.rect(screen, green, [food_x, food_y, snake_block, snake_block])

    snake_head = []
    snake_head.append(x)
    snake_head.append(y)
    snake_list.append(snake_head)

    if len(snake_list) > snake_length:
        del snake_list[0]

    for block in snake_list:
        pygame.draw.rect(screen, red, [block[0], block[1], snake_block, snake_block])

    pygame.display.update()

    if x == food_x and y == food_y:
        food_x = round(random.randrange(0, width - snake_block) / 10.0) * 10
        food_y = round(random.randrange(0, height - snake_block) / 10.0) * 10
        snake_length += 1

    clock.tick(snake_speed)

pygame.quit()