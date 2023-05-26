import numpy as np
import tofpipe
import matplotlib.pyplot as plt
import time
from scipy.ndimage import gaussian_filter
import queue
from skimage.measure import label
from scipy import ndimage

import numpy as np
import ctypes
import abc
from sys import platform
import conn_tcp
import math
from pynput import keyboard
from datetime import datetime
import scipy
import keyboard

conn = conn_tcp.TCPSocket
model = conn(address="192.168.1.13", port=5000, conn_type='zmq')
model.open()
phase_img_clean, intensity_img_clean, phase_meta_clean, intensity_meta_clean = model.get_image()
print('Get a clean plate')
for i in range(10):
    keyboard.wait("ö")
    print('Got a key')
    phase_img, intensity_img, phase_meta, intensity_meta = model.get_image()
    plt.imsave('phase_img.png', phase_img)

    axis_scales = [.004, .002] # The angle spanned by one pixel in each dimension.
    alphas = np.zeros_like(phase_img_clean)
    for i in range(alphas.shape[0]):
        for j in range(alphas.shape[1]):
            alphas[i, j] = (axis_scales[0]**2 * (i - alphas.shape[0] / 2)**2 + axis_scales[1]**2 * (j - alphas.shape[1] / 2)**2)**0.5
    def preprocess_image(image):
        image = np.nan_to_num(image)
        image = np.clip(image, 0, 0.5)
        image = gaussian_filter(image, 1)
        return image
    def getLargestCC(segmentation):
        labels = label(segmentation)
        assert( labels.max() != 0 ) # assume at least 1 CC
        largestCC = labels == np.argmax(np.bincount(labels.flat)[1:])+1
        return largestCC

    test = preprocess_image(phase_img) - preprocess_image(phase_img_clean)
    test = scipy.signal.wiener(test, mysize=(5, 5))
    test *= 2 / (alphas + 1)**2
    test = np.abs(test)
    car_cutoff = 0.02
    car_silhouette = test > car_cutoff
    #car_silhouette = scipy.ndimage.percentile_filter(car_silhouette, 0.7, size=5)
    is_there_a_car = False
    if np.sum(car_silhouette) > 0:
        car_silhouette = getLargestCC(car_silhouette)
        if np.sum(car_silhouette) > 1000:
            is_there_a_car = True

    if is_there_a_car:
        car_silhouette_where = np.where(car_silhouette == 1)
        min_width = np.min(car_silhouette_where[0])
        max_width = np.max(car_silhouette_where[0])
        min_depth = np.min(car_silhouette_where[1])
        max_depth = np.max(car_silhouette_where[1])
        print("Width: ", max_width - min_width)
        print("Depth: ", max_depth - min_depth)
        
        n_pixels = 40
        left_pixels = (car_silhouette_where[0][-n_pixels:], car_silhouette_where[1][-n_pixels:])
        right_pixels = (car_silhouette_where[0][:n_pixels], car_silhouette_where[1][:n_pixels])
        phase_img_filtered = scipy.signal.wiener(preprocess_image(phase_img))
        phase_img_filtered = scipy.signal.medfilt(phase_img_filtered, 3)
        def get_mean_x_displacement(pixel_locations):
            distances = phase_img_filtered[pixel_locations[0], pixel_locations[1]]
            print(np.mean(distances))
            return distances * np.sin(axis_scales[0] * (pixel_locations[0] - alphas.shape[0] / 2))
        proper_width = np.mean(get_mean_x_displacement(left_pixels) - get_mean_x_displacement(right_pixels))
        print("Proper width (m): ", proper_width)
        # Check if proper width is somehow nan or inf
        if np.isnan(proper_width) or np.isinf(proper_width):
            print("Result wasn't a proper number")
            continue
        plt.imsave('car_silhouette.png', car_silhouette)
        with open('shift.txt', 'w') as f:
            x = str(100 * proper_width) + ', ' + datetime.now().strftime("%H:%M:%S")
            print(x)
            f.write(x)
            f.close()
    
model.close()