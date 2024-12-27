# What is Beerbot?
In short, it's a universal robot platform that lets you do the following:
- Control the robot remotely over WLAN or the Internet using a keyboard or gamepad
- View the low latency (100-200ms over WiFi!) WebRTC livestream and control the robot using a web browser 
(works best with Chromium/Chrome and its derivatives)

This project was originally created to have a robotic tank platform with a fridge that could drive around
and serve beer. However, thanks to its simple and modular design, it was transformed to support various
types of chassis such as tank or car type as well as camera gimbals.

## Setup on Raspberry Pi
The project was tested both with Pi 3b and Pi Zero 2W. There's a good chance it will work on different 
models or even different boards such as Jetson Nano with some small code changes.

For performance reasons, it's recommended to install Lite version of Raspbian 64 bit, especially when using Pi Zero.
### Install required packages
`sudo raspi-config`

Choose `Interfacing Options -> I2C -> Yes` if you want to be able to use I2C Pi hats such as the 
[Waveshare Servo Driver hat](waveshare.com/wiki/Servo_Driver_HAT).

Exit the config screen by hitting escape repeatedly and call the following commands from the console:
```
sudo apt update
sudo apt install python3-pip python3-rpi.gpio python3-smbus gstreamer1.0-tools screen ffmpeg -y
sudo reboot
```

Make sure you're in the root folder of this repository.
Install and configure mediamtx that provides low latency web streaming:
```
wget https://github.com/bluenviron/mediamtx/releases/download/v1.10.0/mediamtx_v1.10.0_linux_arm64v8.tar.gz
tar xzvf mediamtx_v1.10.0_linux_arm64v8.tar.gz
```

Finally, create a virtual environment from the repository root folder and install the required python packages:
```commandline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the software

Once everything is installed, running the robot software consists of two components:
1. Run the video streaming in one screen
2. Run the robot server in another screen


### Running the video stream
Create a new screen by typing
```commandline
screen
```
and press enter. Accept the conditions by pressing spacebar.

Now you can start streaming and choose between different profiles (there's a `mediamtx-balanced` as well as `mediamtx-low-latency.yml`file available)

For example:
```commandline
./mediamtx mediamtx-balanced.yml
```

Finally, minimize the screen by pressing `ctrl+A`, releasing and then pressing `D` key.

### Running the robot server
Create a new screen by typing
```commandline
screen
```

Activate the virtual environment
```
source .venv/bin/activate
```
Once you do this, you should see `(venv)` to the left of the current path and username in the console.

Finally you can run the server:
```commandline
python server.py
```

Congratulations! You should now be able to open the connection to the robot in your web browser and control it!

Try http://<robot_ip>:5000 where `<robot_ip>` should be replaced with the IP address of the robot.

## Development
The python backend was designed to support abstract hardware, so adding support to new Pi Hats or controls
should be quite straightforward by implementing `AbstractChassisBackend` and `AbstractGimbalBackend` classes
in the `backend/hardware_backends` folder.
