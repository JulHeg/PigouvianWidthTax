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

# use the follwing for 2 frequency (8 phase) algorithm:
# pipeline = tofpipe.DualAlgorithm(FREQ0, FREQ1, frame_len=FRAME_LEN)

# Setup Camera

start_time = time.time()
camera = tofpipe.Camera()
camera.open()
i = 0
while True:
    print('Ready for taking images')
    input()
    try:
        for usecase_nr in range(len(camera.usecases)):
            pipeline = tofpipe.SingleAlgorithm(FREQ0, frame_len=FRAME_LEN)
            print(camera.usecases[usecase_nr].nr_frames)
            camera.current_usecase = camera.usecases[usecase_nr] #4 frames, 80.32MHz
            print(f'There are {len(camera.usecases)} usecases')
            # Get raw frames
            camera.start()
            raw_frames = camera.grab_raw()
            camera.stop()

            # run calculation
            pipeline.run(raw_frames[1:, 1:, :].reshape(4,-1))

            # get output
            amplitude = pipeline.amplitude.reshape(240,640)
            phase = pipeline.phase.reshape(240,640)
            sat_error = pipeline.saturation_error.reshape(240,640)
            min_amplitude_error = pipeline.min_amplitude_error.reshape(240,640)
            symmetry_error = pipeline.symmetry_error.reshape(240,640)

            # print some stats
            print("Amplitude: min: {}, max: {}".format(amplitude.min(), amplitude.max()))
            print("Phase: min: {}, max: {}".format(phase.min(), phase.max())) # Tiefe
            print("Saturation Error: min: {}, max: {}".format(sat_error.min(), sat_error.max()))
            print("Min Amplitude Error: min: {}, max: {}".format(min_amplitude_error.min(), min_amplitude_error.max()))
            print("Symmetry Error: min: {}, max: {}".format(symmetry_error.min(), symmetry_error.max()))

            # Print shapes of output
            print("Amplitude shape: {}".format(amplitude.shape))
            print("Phase shape: {}".format(phase.shape))
            print("Saturation Error shape: {}".format(sat_error.shape))
            print("Min Amplitude Error shape: {}".format(min_amplitude_error.shape))
            print("Symmetry Error shape: {}".format(symmetry_error.shape))

            # Plot phase with matplotlib
            plt.imshow(phase)
            #plt.show()
            # Save phase as png
            # Add colorbar
            plt.colorbar()
            plt.savefig(f"images/phase{i}_{usecase_nr}.png")
            # Save data as npy too
            np.save(f"images/phase{i}_{usecase_nr}.npy", phase)
            # Plot amplitude with matplotlib
            plt.clf()
            plt.imshow(amplitude)
            # Clear the previous colorbar
            plt.colorbar()

            plt.savefig(f"images/amplitude{i}_{usecase_nr}.png")
            np.save(f"images/amplitude{i}_{usecase_nr}.npy", amplitude)

            end_time = time.time()
            print("Time elapsed: {}".format(end_time - start_time))
            plt.clf()
    except:
        print('RRRRRRRRRRRRRRRRRRRRRORRRRRRRRRRRRRR')
    i += 1