import numpy as np
import tofpipe
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import time

FREQ0 = 80320000
temp0 = 20
FREQ1 = 60240000
temp1 = 20

# The amount of pixels for a single image
# the library also defines two constants:
#  tofpipe.HVGA and tofpipe.VGA

FRAME_LEN = tofpipe.HVGA
wait_time = 1
while True:
    try:
        # only needs to be constructed once with params
        pipeline = tofpipe.SingleAlgorithm(FREQ0, frame_len=FRAME_LEN)

        # use the follwing for 2 frequency (8 phase) algorithm:
        # pipeline = tofpipe.DualAlgorithm(FREQ0, FREQ1, frame_len=FRAME_LEN)

        # Setup Camera

        start_time = time.time()
        camera = tofpipe.Camera()
        camera.open()
        camera.current_usecase = camera.usecases[0] #4 frames, 80.32MHz

        camera.start()
        raw_frames = camera.grab_raw()
        camera.stop()

        pipeline.run(raw_frames[1:, 1:, :].reshape(4,-1))
        def preprocess_image(image):
            image = gaussian_filter(image, 1)
            dtfloat = tofpipe.default_dtype()
            xout = np.ones((image.shape[0]*2,image.shape[1]), dtype=dtfloat)
            image = tofpipe.interpolate_mean(image, xout)
            return xout
        phase = pipeline.phase.reshape(240,640)
        phase = preprocess_image(phase)
        file_path = 'phase_live.npy'
        np.save(file_path, phase)
    except:
        print('Error occured, no file written')
    time.sleep(wait_time)