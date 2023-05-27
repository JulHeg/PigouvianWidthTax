import numpy as np
import tofpipe
import matplotlib.pyplot as plt
import time
from scipy.ndimage import gaussian_filter
from skimage.measure import label
from scipy import ndimage
import scipy
import numpy as np
import pysftp

def get_phase_from_raspi():
    """
    Gets a phase image from the raspberry pi. This is quite janky because the TCP/IP didn't work so we use SFTP to poll.
    :return: The phase image as a numpy array.
    """
    max_retry = 5
    for i in range(max_retry):
        try:
            with pysftp.Connection('192.168.1.13', username='pi', password='raspberry') as sftp: # Committing out credentials to GitHub
                sftp.get('phase_live.npy')
            
            # Show the image we just got
            file_path = 'phase_live.npy'
            phase = np.load(file_path)
            return phase
        except:
            time.sleep(1)
    print('Failed to get image from Raspberry Pi')
    

def measure_vehicle_width(clean_plate_phase, vehicle_capture_phase, axis_scales = [.002, .002], verbose = False, save_images = False):
    """
    Measures the width of a vehicle in a phase image. This uses some fairly ad-hoc hodgepodge image processing techniques to detect where the image changed from the clean plate to out image with the vehicle.
    Then we know where the car is. Next we use the depth information with some light trigonometry to get the width of the vehicle in metres.
    
    :param clean_plate_phase: The phase image of the clean plate taken before without any vehicles.
    :param vehicle_capture_phase: The phase image of the vehicle.
    :param axis_scales: The axis scales of the phase image in meters per pixel.
    :param verbose: Whether to print extra information
    :param save_images: Whether to save some images.
    :return: The width of the vehicle in meter.
    """
    if save_images:
        plt.imsave('clean_plate_phase.png', clean_plate_phase)
        plt.imsave('vehicle_capture_phase.png', vehicle_capture_phase)
    alphas = np.zeros_like(clean_plate_phase)
    for i in range(alphas.shape[0]):
        for j in range(alphas.shape[1]):
            alphas[i, j] = (axis_scales[0]**2 * (i - alphas.shape[0] / 2)**2 + axis_scales[1]**2 * (j - alphas.shape[1] / 2)**2)**0.5
    def preprocess_image(image):
        image = np.nan_to_num(image)
        image = gaussian_filter(image, 1)
        return image
    def getLargestCC(segmentation):
        labels = label(segmentation)
        assert( labels.max() != 0 ) # assume at least 1 CC
        largestCC = labels == np.argmax(np.bincount(labels.flat)[1:])+1
        return largestCC

    test = preprocess_image(vehicle_capture_phase) - preprocess_image(clean_plate_phase)
    test = scipy.signal.wiener(test, mysize=(5, 5))
    test *= 2 / (alphas + 1)**2
    test = np.abs(test)
    car_cutoff = 0.02
    car_silhouette = test > car_cutoff
    #car_silhouette = scipy.ndimage.percentile_filter(car_silhouette, 0.7, size=5)
    if np.sum(car_silhouette) > 0:
        car_silhouette = getLargestCC(car_silhouette)
        car_silhouette_where = np.where(car_silhouette == 1)
        if save_images:
            plt.imsave('car_silhouette.png', car_silhouette)
        min_width = np.min(car_silhouette_where[0])
        max_width = np.max(car_silhouette_where[0])
        min_depth = np.min(car_silhouette_where[1])
        max_depth = np.max(car_silhouette_where[1])
        if verbose:
            print("Width: ", max_width - min_width)
            print("Depth: ", max_depth - min_depth)
        
        n_pixels = 40
        left_pixels = (car_silhouette_where[0][-n_pixels:], car_silhouette_where[1][-n_pixels:])
        right_pixels = (car_silhouette_where[0][:n_pixels], car_silhouette_where[1][:n_pixels])
        depth_map = scipy.signal.wiener(preprocess_image(vehicle_capture_phase)) * 0.11
        depth_map = scipy.signal.medfilt(depth_map, 3)
        def get_mean_x_displacement(pixel_locations):
            distances = depth_map[pixel_locations[0], pixel_locations[1]]
            if verbose:
                print(np.mean(distances))
            return distances * np.sin(axis_scales[0] * (pixel_locations[0] - alphas.shape[0] / 2))
        proper_width = np.mean(get_mean_x_displacement(left_pixels) - get_mean_x_displacement(right_pixels))
        return proper_width