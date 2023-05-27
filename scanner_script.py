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
from datetime import datetime
import scipy
import keyboard
import utils

phase_img_clean = utils.get_phase_from_raspi()
keystroke_to_wait_for = "ö"
print('Got a clean plate to compare to')
for i in range(10):
    keyboard.wait(keystroke_to_wait_for)
    print('Got a key')
    phase_img = utils.get_phase_from_raspi()
    proper_width = utils.measure_vehicle_width(phase_img_clean, phase_img, verbose=True)
    with open('shift.txt', 'w') as f:
        x = str(100 * proper_width) + ', ' + datetime.now().strftime("%H:%M:%S")
        print(x)
        f.write(x)
        f.close()