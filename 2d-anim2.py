#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 25 21:01:13 2023

@author: Daniel
"""

# Example file showing a rectangle moving on screen
import pygame as pg
import time

from screeninfo import get_monitors
for m in get_monitors():
    print(str(m))
screen_resol = get_monitors()

def make_new_coordinate_list(new_car_width, old_coordinate_list, n_car):
    print("old_coordinate_list: ", old_coordinate_list)
    print("ncar: ", n_car)
    try:
        addval = new_car_width - old_coordinate_list[n_car] + (old_coordinate_list[n_car - 1] if n_car > 0 else 0)
        new_coordinate_list = old_coordinate_list[:n_car] + [x + addval for x in old_coordinate_list[n_car:]]
    except IndexError:
        new_coordinate_list = old_coordinate_list
    return new_coordinate_list


# pygame setup
pg.init()
screen = pg.display.set_mode((screen_resol[0].width, screen_resol[0].height))
running = True

start_time = time.time()
duration = 2.0
old_time = None

# left and right border line
left_border_x = 0
right_border_x = 1260

# starting coordinates
start_y = 20

startcos = [315, 630, 945]
# distance to move in x direction (positive or negative)

colist = startcos.copy()
# size of rectangle
rect_size = (20,400)
rect_color = (255, 255, 255)
bg_color = (128, 128, 128)


# Create the rectangle
#rect1 = pg.Rect(start_x1, start_y, *rect_size)
#rect2 = pg.Rect(start_x2, start_y, *rect_size)
rectangles = []
for rectangle_coordinates in colist:
    rectangles.append(pg.Rect(rectangle_coordinates, start_y, *rect_size))

# borders
left_border = pg.Rect(left_border_x, start_y, *rect_size)
right_border = pg.Rect(right_border_x, start_y, *rect_size)

# Name of the text file to read the shift value from
shift_file_name = "shift.txt"
start_coords = startcos.copy()
shifts = [0] * len(rectangles)
start_times = [time.time()] * len(rectangles)
car_counter = 0
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
            txt_input = f.read().split(", ")
            if old_time != txt_input[1]:
                #
                old_time = txt_input[1]
                new_x_coordinate_list = make_new_coordinate_list(int(txt_input[0]), colist, car_counter)
                car_counter += 1
                # TODO add a timestamp and only make new clist if a new car comes
                for c, coord in enumerate(new_x_coordinate_list):
                    if new_x_coordinate_list[c] != colist[c]:
                        colist[c] = coord
                        start_coords[c] = rectangles[c].x
                        shifts[c] = colist[c] - start_coords[c]
                        start_times[c] = time.time()
    except (FileNotFoundError, ValueError, IndexError):
        print("An Error occured while reading the shift file")
        pass  # If the file doesn't exist or the content is not a number, ignore it


    # Calculate the current time elapsed since the start of the animation
    tn = [0 if start_times[c] is None else time.time() - start_times[c] for c in range(len(rectangles))]


    # If the animation is not over, move the rectangle
    old_rects = [None] * len(rectangles)
    for c, t in enumerate(tn):
        if t < 1.0:
            move_x1 = round(shifts[c] * t)
            old_rects[c] = rectangles[c].copy()
            rectangles[c].x = start_coords[c] + move_x1
            # Fill the old rectangle with the background color
            screen.fill(bg_color)
            pg.draw.rect(screen, rect_color, old_rects[c])
        else:
            pass

    # plot rectangle in current position
    # plot rectangle in current position
    for rectangle in rectangles:
        pg.draw.rect(screen, rect_color, rectangle)

    # plot border lines
    pg.draw.rect(screen, rect_color, left_border)
    pg.draw.rect(screen, rect_color, right_border)

    # flip() the display to put your work on screen
    pg.display.flip()

pg.quit()
