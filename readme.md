# What is Beerbot?
In short, it's a universal robot platform that lets you do the following:
- Control the robot remotely over WLAN or the Internet using a keyboard or gamepad
- See low latency livestream and control the robot using a web browser

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
mkdir mediamtx
cd mediamtx
wget https://github.com/bluenviron/mediamtx/releases/download/v1.10.0/mediamtx_v1.10.0_linux_arm64v8.tar.gz
tar xzvf mediamtx_v1.10.0_linux_arm64v8.tar.gz
```

Next, copy the mediamtx config to the folder where mediamtx was installed.
```
cp mediamtx.yml streaming/mediamtx.yml
```

nano mediamtx.yml
Scroll all the way down, comment out “all_others:” by adding # (so the line reads #all_others:
Now under the line paths: paste the following
  cam1:
    runOnInit: bash -c 'rpicam-vid -t 0 --camera 0 --nopreview --codec yuv420 --width 1280 --height 720 --inline --listen -o - | ffmpeg -f rawvideo -pix_fmt yuv420p -s:v 1280x720 -i /dev/stdin -c:v libx264 -preset ultrafast -tune zerolatency -b:v 0.5M -f rtsp rtsp://localhost:$RTSP_PORT/$MTX_PATH'
    runOnInitRestart: yes

Note the spacebar indentations and make sure it looks the same on your screen!

runOnInit: bash -c 'rpicam-vid -t 0 --camera 0 --nopreview --codec yuv420 --width 1280 --height 720 --inline --listen -o - | ffmpeg -f rawvideo -pix_fmt yuv420p -s:v 1280x720 -i /dev/stdin -c:v h264_v4l2m2m -b:v 0.5M -g 10 -keyint_min 1 -flags +low_delay -max_delay 0 -f rtsp rtsp://localhost:8554/cam1'

Finally, create a virtual environment from the repository root folder and install the required python packages:
```commandline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### Run the server
Every time you restart Raspberry Pi you will need to activate the virtual environment the code runs from.
The reason it's like that is to keep python projects self-contained so that the packages they use and install 
don't cause conflicts between projects.
```
source .venv/bin/activate
```
Once you do this, you should see `(venv)` to the left of the current path and username in the console.

Finally you can run the server:
```commandline
python server.py <host> <port>
```
Where `<host>` and `<port>` should be replaced with your hostname or ip-address and port for websocket interface.
For example for local streaming you can use 
```commandline
python server.py localhost 443
```
Once you do this, streaming and web interface should start.
You should now be able to open the connection to the robot in your web browser
## Development
The python backend was designed to support abstract hardware, so adding support to new Pi Hats or controls
should be quite straightforward by implementing `AbstractChassisBackend` and `AbstractGimbalBackend` classes
in the `backend/hardware_backends` folder.
