# IntelliPark
![Depth image of a toy car](car_pic_bmw.png)

This is our submission to the [Hackaburg 2023](https://hackaburg.de/) hackathon to make cars pay for parking space by their actual width as a Pigouvian tax on parking footprint. You can read more about the idea of our submission [on Devpost](https://devpost.com/software/tax-the-width).

## How to run this
This repository assumes you have a Raspberry Pi with an as-yet unreleased time of flight camera module plugged in and all the drivers running. You should also have an active SSH connection from your computer to that Raspberry. You can install the needed environment with Anaconda like this:

```
conda env create -f environment.yml
```

You also have to get the `tofpipe` library from Infineon, it's not quite public yet.

Then you can run the [stream_phase.py](file_from_raspi\stream_phase.py) file there to take a depth image once a second and saves it to your file. Then you can use the ´get_phase_from_raspi()´ method in [utils.py](utils.py) to get the depth information from that image transferred over SSH to your computer.

On your computer, run the `python scanner_script.py` script to measure how horizontally wide an object moved in front of the sensor is when you press a button. We use this to measure toy cars in our parking space demo. You can also visualize that by simultaneously running the `python 2d-anim2.py`. This opens a full screen window simulating a car park. Once you measure an object's width, it sizes a parking space in life-size where you could put it.

## Step-by-step to running the demo (with our setup graciously provided by Infineon at least)

Use these commands to get the image daemon on the Raspberry Pi running:
```
ssh pi@192.168.1.13
sudo insmod irs2877/driver/irs2877.ko
python stream_phase.py
```

Then on your own computer run:
```
python scanner_script.py
python 2d-anim2.py
```

## Other things in this repo

We put some things besides our final demo in this repository. With `collect_dataset.ipynb` we collected a small dataset of different scans in our model setup. It's not big enough to train some fancy neural networks, but we used it to calibrate our regular algorithm. As you can see in the `measurement_calibration.ipynb`, we usually manage to get the size to within 10% or so.

There are also some old Python artifacts in the `archive` folder if anyone is interested. We also went out to a nearby car park to capture some actual depth images of cars with our sensor. These images are in the `images` folder. There's also a nice selection of random screenshots in the main folder ending to look at.