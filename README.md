# IntelliPark

This is our submission to the [Hackaburg 2023](https://hackaburg.de/) hackathon. You can read more about the idea of our submission [here](https://devpost.com/software/tax-the-width).

## How to run this
This repository assumes you have a Raspberry Pi with an as-yet unreleased time of flight camera module plugged in and all the drivers running. You should also have an active SSH connection from your computer to that Raspberry. You can install the needed environment with Anaconda like this:

```
conda env create -f environment.yml
```

You also have to get the `tofpipe` from Infineon, it's not quite public yet.

Then you can run the [stream_phase.py](file_from_raspi\stream_phase.py) file there to take a depth image once a second and saves it to your file. Then you can use the ´get_phase_from_raspi()´ method in [utils.py](utils.py) to get the depth information from that image transferred over SSH to your computer.

On your computer, run the `python scanner_script.py` script to measure how horizontally wide an object moved in front of the sensor is when you press a button. We use this to measure toy cars in our parking space demo. You can also visualize that by simultaneously running the `python 2d-anim_HC.py`. This opens a full screen windows simulating a car park. Once you measure an objects width, it sizes a parking space in life-size where you could put it.

## Step-by-step to get this running (with our setup graciously provided by Infineon at least)

Use this commands to get the image deamon on the Raspberry Pi running:
```
ssh pi@192.168.1.13
sudo insmod irs2877/driver/irs2877.ko
python stream_phase.py
```

Then on your own computer run
```
python scanner_script.py
python 2d-anim_HC.py
```
