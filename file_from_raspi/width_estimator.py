import numpy as np
import tofpipe
import matplotlib.pyplot as plt
import time
from scipy.ndimage import gaussian_filter
import queue
from skimage.measure import label

import numpy as np
import ctypes
import abc
from sys import platform



FREQ0 = 80320000
temp0 = 20
FREQ1 = 60240000
temp1 = 20

# The amount of pixels for a single image
# the library also defines two constants:
#  tofpipe.HVGA and tofpipe.VGA

FRAME_LEN = tofpipe.HVGA

# only needs to be constructed once with params
pipeline_2 = tofpipe.SingleAlgorithm(FREQ0, frame_len=FRAME_LEN)

# use the follwing for 2 frequency (8 phase) algorithm:
# pipeline = tofpipe.DualAlgorithm(FREQ0, FREQ1, frame_len=FRAME_LEN)

# Setup Camera

start_time = time.time()
camera = tofpipe.Camera()
camera.open()
camera.current_usecase = camera.usecases[0] #4 frames, 80.32MHz

print('Ready to take clean plate')
# Ask for user input
input()
# Get raw frames
camera.start()
clean_plate = camera.grab_raw()
camera.stop()

def preprocess_image(image):
    image = gaussian_filter(image, 1)
    dtfloat = tofpipe.default_dtype()
    xout = np.ones((image.shape[0]*2,image.shape[1]), dtype=dtfloat)
    image = tofpipe.interpolate_mean(image, xout)
    return xout

def getLargestCC(segmentation):
    labels = label(segmentation)
    assert( labels.max() != 0 ) # assume at least 1 CC
    largestCC = labels == np.argmax(np.bincount(labels.flat)[1:])+1
    return largestCC

while True:
    print("Taking image")
    # Get raw frames
    camera.start()
    raw_frames_2 = camera.grab_raw()
    camera.stop()

    pipeline = tofpipe.SingleAlgorithm(FREQ0, frame_len=FRAME_LEN)
    pipeline.run(clean_plate[1:, 1:, :].reshape(4,-1))
    amplitude_1 = pipeline.amplitude.reshape(240,640)
    amplitude_1 = preprocess_image(amplitude_1)
    phase_1 = pipeline.phase.reshape(240,640)
    phase_1 = preprocess_image(phase_1)
    pipeline = tofpipe.SingleAlgorithm(FREQ0, frame_len=FRAME_LEN)
    pipeline.run(raw_frames_2[1:, 1:, :].reshape(4,-1))
    amplitude = pipeline.amplitude.reshape(240,640)
    amplitude = preprocess_image(amplitude)
    phase = pipeline.phase.reshape(240,640)
    phase = preprocess_image(phase)
    print('min phase', np.min(phase))
    print('max phase', np.max(phase))

    car_cutoff = 0.015
    phase_difference = np.abs(gaussian_filter(phase_1 - phase,3))
    plt.imsave("phase_difference.png", phase_difference)
    car_silhouette = phase_difference > car_cutoff
    if np.sum(car_silhouette) > 0:
        car_silhouette = getLargestCC(car_silhouette)
    plt.imsave("car_silhouette.png", car_silhouette, vmin=0, vmax=1)
    plt.imsave("car_silhouette_phase.png", car_silhouette * phase)
    plt.imsave("car_amplitude.png", amplitude)
    plt.imsave("car_phase.png", phase)
    # Save silhoutte
    

    # Calculate the width and height of the silhouette
    # minimum index of a 1
    if np.sum(car_silhouette) > 0:
        
        # Get the dimension of the bounding box of the silhoutte
        min_width = np.min(np.where(car_silhouette == 1)[1])
        max_width = np.max(np.where(car_silhouette == 1)[1])
        min_height = np.min(np.where(car_silhouette == 1)[0])
        max_height = np.max(np.where(car_silhouette == 1)[0])
        width = max_width - min_width
        height = max_height - min_height
        print("Width: {}, Height: {}".format(width, height))
        
        # Get the average distance for the outermost couple of pixels to the left and right.
        n_pixels = min(10, np.sum(car_silhouette))
        car_silhouette = np.transpose(car_silhouette)
        phase = np.transpose(phase)
        average_left_phase = np.mean(phase[np.where(car_silhouette == 1)[0][:n_pixels], np.where(car_silhouette == 1)[1][:n_pixels]])
        average_right_phase = np.mean(phase[np.where(car_silhouette == 1)[0][-n_pixels:], np.where(car_silhouette == 1)[1][-n_pixels:]])
        print('average_left_phase', average_left_phase)
        print('average_right_phase', average_right_phase)
        average_left_distance = average_left_phase
        average_right_phase = average_right_phase
        
        
    time.sleep(1)
    