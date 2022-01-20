import picamera
import time
import uuid
from gpiozero import Button

resolution = (1856,1392) #Optimal 4:3 Ratio
resolution_text = str(resolution[0]) + "x" + str(resolution[1])

def take_picture():
    camera.annotate_text = "Photo - 3"
    time.sleep(1)
    camera.annotate_text = "Photo - 2"
    time.sleep(1)
    camera.annotate_text = "Photo - 1"
    time.sleep(1)
    camera.annotate_text = ""
    camera.capture("photo"+ str(uuid.uuid4())[:8] + ".jpg")
    camera.annotate_text = "Photo Taken"
    time.sleep(1)
    print("Photo taken")

button1 = Button(17)
button1.when_pressed = take_picture

with picamera.PiCamera(resolution=resolution_text, framerate=24) as camera:
    camera.annotate_text_size = 160
    camera.start_preview()
    while True:
        time.sleep(1)

