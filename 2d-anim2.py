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
start_x1 = 200
start_x2 = 1000
# distance to move in x direction (positive or negative)
x_coordinate1 = 100
x_coordinate2 = 700
# size of rectangle
rect_size = (20,400)
rect_color = (128, 128, 128)

# Create the rectangle
rect1 = pg.Rect(start_x1, start_y, *rect_size)
rect2 = pg.Rect(start_x2, start_y, *rect_size)

# Name of the text file to read the shift value from
shift_file_name = "shift.txt"

while running:
    # sleep for 1 millisecond to avoid 100% CPU usage
    time.sleep(0.001)
    
    # poll for events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # Check the text file for a new shift value
    try:
        with open(shift_file_name, 'r') as f:
            new_x_coordinate1 = int(f.read().strip()[1:-1].split(", ")[0])
            if new_x_coordinate1 != x_coordinate1:
                x_coordinate1 = new_x_coordinate1
                start_x1 = rect1.x
                # calculate the shift to get to the new x coordinate
                shift1 = x_coordinate1 - start_x1
                start_time1 = time.time()
    except (FileNotFoundError, ValueError):
        pass  # If the file doesn't exist or the content is not a number, ignore it

    try:
        with open(shift_file_name, 'r') as f:
            new_x_coordinate2 = int(f.read().strip()[1:-1].split(", ")[1])
            if new_x_coordinate2 != x_coordinate2:
                x_coordinate2 = new_x_coordinate2
                start_x2 = rect2.x
                # calculate the shift to get to the new x coordinate
                shift2 = x_coordinate2 - start_x2
                start_time2 = time.time()
    except (FileNotFoundError, ValueError):
        pass  # If the file doesn't exist or the content is not a number, ignore it

    # Calculate the current time elapsed since the start of the animation
    t1 = (time.time() - start_time1) / duration
    t2 = (time.time() - start_time2) / duration

    # If the animation is not over, move the rectangle
    if t1 < 1.0:
        move_x1 = int(shift1 * t1)
        old_rect1 = rect1.copy()  # Keep a copy of the old rectangle
        rect1.x = start_x1 + move_x1
        # Fill the old rectangle with the background color
        screen.fill((0, 0, 0))
        pg.draw.rect(screen, rect_color, old_rect1)
    else:
        pass
    
    if t2 < 1.0:
        move_x2 = int(shift2 * t2)
        old_rect2 = rect2.copy()  # Keep a copy of the old rectangle
        rect2.x = start_x2 + move_x2
        # Fill the old rectangle with the background color
        screen.fill((0, 0, 0))
        pg.draw.rect(screen, rect_color, old_rect2)
    else:
        pass

    # plot rectangle in current position
    pg.draw.rect(screen, rect_color, old_rect1)
    pg.draw.rect(screen, rect_color, old_rect2)

    # flip() the display to put your work on screen
    pg.display.flip()

pg.quit()
