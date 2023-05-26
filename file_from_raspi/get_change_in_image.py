import numpy as np
import tofpipe
import matplotlib.pyplot as plt
import time


FREQ0 = 80320000
temp0 = 20
FREQ1 = 60240000
temp1 = 20

# The amount of pixels for a single image
# the library also defines two constants:
#  tofpipe.HVGA and tofpipe.VGA

FRAME_LEN = tofpipe.HVGA

# only needs to be constructed once with params
pipeline = tofpipe.SingleAlgorithm(FREQ0, frame_len=FRAME_LEN)
pipeline_2 = tofpipe.SingleAlgorithm(FREQ0, frame_len=FRAME_LEN)

# use the follwing for 2 frequency (8 phase) algorithm:
# pipeline = tofpipe.DualAlgorithm(FREQ0, FREQ1, frame_len=FRAME_LEN)

# Setup Camera

start_time = time.time()
camera = tofpipe.Camera()
camera.open()
print(camera.usecases[0].nr_frames)
camera.current_usecase = camera.usecases[0] #4 frames, 80.32MHz

# Ask for user input
print("Take first image")
input()
# Get raw frames
camera.start()
raw_frames_1 = camera.grab_raw()
camera.stop()

print("Take second image")
input()
# Get raw frames
camera.start()
raw_frames_2 = camera.grab_raw()
camera.stop()

pipeline.run(raw_frames_1[1:, 1:, :].reshape(4,-1))
amplitude_1 = pipeline.amplitude.reshape(240,640)
pipeline_2.run(raw_frames_2[1:, 1:, :].reshape(4,-1))
amplitude_2 = pipeline_2.amplitude.reshape(240,640)

# Save both as images
plt.imsave("amplitude_1.png", amplitude_1, vmin=0, vmax=1000)
plt.imsave("amplitude_2.png", amplitude_2, vmin=0, vmax=1000)

car_cutoff = 100
car_silhouette = np.abs(amplitude_1 - amplitude_2) > car_cutoff
plt.imsave("car_silhouette.png", car_silhouette, vmin=0, vmax=1)

# Calculate the width and height of the silhouette
# minimum index of a 1
min_width = np.min(np.where(car_silhouette == 1)[1])
max_width = np.max(np.where(car_silhouette == 1)[1])
min_height = np.min(np.where(car_silhouette == 1)[0])
max_height = np.max(np.where(car_silhouette == 1)[0])
width = max_width - min_width
height = max_height - min_height
print("Width: {}, Height: {}".format(width, height))
