import picamera
import time

resolution = (1856,1392) #Optimal 4:3 Ratio

camera = picamera.PiCamera()
camera.resolution = resolution
camera.start_preview()
while True:
    time.sleep(1)
