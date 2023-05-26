#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 25 21:01:13 2023

@author: Daniel
"""

# Example file showing a circle moving on screen
import pygame as pg
import time

# pygame setup
pg.init()
screen = pg.display.set_mode((1280, 720))
running = True

start_time = time.time()
duration = 2.0

# starting coordinates
start_y = 20
start_x = 200
# distance to move in x direction (positive or negative)
shift = 100
# size of rectangle
rect_size = (20,400)
rect_color = "white"

# x end position
end_x = start_x + shift

# Create the rectangle
rect = pg.Rect(start_x, start_y, *rect_size)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("grey")

    # Calculate the current time elapsed since the start of the animation
    t = (time.time() - start_time) / duration

    # If the animation is over, exit animation
    if t < 1.0:
        x = shift * t
        rect.move_ip(int(x), 0)
        start_time = time.time()

    # plot rectangle in current position
    pg.draw.rect(screen, rect_color, rect)

    # flip() the display to put your work on screen
    pg.display.flip()


pg.quit()
