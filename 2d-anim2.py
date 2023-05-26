#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 25 21:01:13 2023

@author: Daniel
"""

# Example file showing a rectangle moving on screen
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
x_coordinate = 100
# size of rectangle
rect_size = (20,400)
rect_color = (128, 128, 128)

# Create the rectangle
rect = pg.Rect(start_x, start_y, *rect_size)

# Name of the text file to read the shift value from
shift_file_name = "shift.txt"

while running:
    # poll for events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # Check the text file for a new shift value
    try:
        with open(shift_file_name, 'r') as f:
            new_x_coordinate = int(f.read().strip())
            if new_x_coordinate != x_coordinate:
                x_coordinate = new_x_coordinate
                start_x = rect.x
                # calculate the shift to get to the new x coordinate
                shift = x_coordinate - start_x
                start_time = time.time()
    except (FileNotFoundError, ValueError):
        pass  # If the file doesn't exist or the content is not a number, ignore it

    # Calculate the current time elapsed since the start of the animation
    t = (time.time() - start_time) / duration

    # If the animation is not over, move the rectangle
    if t < 1.0:
        move_x = int(shift * t)
        old_rect = rect.copy()  # Keep a copy of the old rectangle
        rect.x = start_x + move_x
        # Fill the old rectangle with the background color
        screen.fill((0, 0, 0))
        pg.draw.rect(screen, rect_color, old_rect)
    else:
        # Reset the animation if it's over
        #start_time = time.time()
        pass
    # plot rectangle in current position
    #pg.draw.rect(screen, rect_color, rect)

    # flip() the display to put your work on screen
    pg.display.flip()

pg.quit()
