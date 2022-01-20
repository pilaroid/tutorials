import picamera
import time

from http import server
import socketserver
import logging
import io
from threading import Condition
from gpiozero import Button
import uuid
resolution = (1856,1392) #Optimal 4:3 Ratio
resolution_text = str(resolution[0]) + "x" + str(resolution[1])

PAGE='<html><body><img src="stream.mjpg" width="' + str(resolution[0]) + '" height="' + str(resolution[1]) +'" /></body></html>'

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

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution=resolution_text, framerate=24) as camera:
    camera.annotate_text_size = 160
    output = StreamingOutput()
    camera.start_preview()
    camera.start_recording(output, format='mjpeg')
    camera.annotate_text = ""
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()

    finally:
        camera.stop_recording()
