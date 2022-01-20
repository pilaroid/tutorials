import picamera
import time
from gpiozero import Button

resolution = (1856,1392) #Optimal 4:3 Ratio
resolution_text = str(resolution[0]) + "x" + str(resolution[1])

def take_picture():
    print("Photo taken")
    camera.capture("photo.jpg")

button1 = Button(17)
button1.when_pressed = take_picture

with picamera.PiCamera(resolution=resolution_text, framerate=24) as camera:
    camera.start_preview()
    while True:
        time.sleep(1)
