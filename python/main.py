import threading
import time
import logging
import random
import queue
import socket
import sys
import picamera
import os
import subprocess

from gpiozero import MotionSensor
from datetime import datetime
from states import State

# Create required directories
if not os.path.exists('/home/pi/wildlife_camera/log'):
    os.makedirs('/home/pi/wildlife_camera/log')
if not os.path.exists('/home/pi/wildlife_camera/videos'):
    os.makedirs('/home/pi/wildlife_camera/videos')

# Create logfile
logfile = '/home/pi/wildlife_camera/log/trailcam_log_'+str(datetime.now().strftime('%Y%m%d-%H%M'))+'.csv'

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='(%(asctime)s %(threadName)s) %(message)s', datefmt='%Y-%m-%d, %H:%M:%S,')

pir = MotionSensor(17)

BUF_SIZE = 10
q = queue.Queue(BUF_SIZE)

class DefaultState(State):
    """
    The default mode.
    """

    def on_event(self, event):
        if event == 'stream_on':
            logging.debug('entering live view mode')
            logging.debug('setting up video stream')
            vlc_cmd = "raspivid -o - -t 9999999 -w 640 -h 360 -fps 25|cvlc stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8000}' :demux=h264 &"
            subprocess.call([vlc_cmd], shell=True)
            return StreamState()

        elif event == 'motion_on':
            logging.debug('entering motion detect mode')
            while True:
                logging.debug('waiting for motion')
                pir.wait_for_motion()
                logging.info('motion detected')
                logging.debug('capturing video')
                ts = '{:%d%m%Y_%H%M%S}'.format(datetime.now())
                with picamera.PiCamera() as camera:
                    camera.resolution = (1024, 768)
                    camera.annotate_background = picamera.Color('black')
                    camera.start_recording('/home/pi/wildlife_camera/videos/video.h264')
                    start = datetime.now()
                    while (datetime.now() - start).seconds < 30:
                        camera.annotate_text = 'nature_cam_'+datetime.now().strftime('%d_%m_%y_%H:%M:%S')
                        camera.wait_recording(0.2)
                    camera.stop_recording()
                time.sleep(5)
                timestamp = datetime.now().strftime('%d_%m_%y_%H_%M_%S')
                input_video  = '/home/pi/wildlife_camera/videos/video.h264'
                logging.info('attempting to save video')
                if os.path.isdir('/mnt/usb/videos'):
                    logging.info('saving to /mnt/usb/videos')
                    output_video = '/mnt/usb/videos/{}.mp4'.format(timestamp)
                else:
                    logging.info('USB drive not mounted')
                subprocess.call(['MP4Box', '-add', input_video, output_video])
                if not q.empty():
                    message = q.get()
                    logging.debug('fetching (' + str(message) + '): ' + str(q.qsize()) + ' items in queue')
                    if message == 'stop':
                        if not q.empty():
                            message = q.get()
                        logging.debug('fetching (' + str(message) + '): ' + str(q.qsize()) + ' items in queue')
                        if message == 'motion_off':
                            break
                    elif message == 'motion_off':
                        break
            logging.debug('motion detect ended')
            return DefaultState()
        return self

class StreamState(State):
    """
    The stream mode state.
    """

    def on_event(self, event):
        if event == 'stream_off':
            logging.debug('exiting live view mode...')
            logging.debug('killing video stream...')
            cmdline = ['pkill', '-e', 'vlc']
            subprocess.check_output(cmdline)
            cmdline = ['pkill', '-e', 'raspivid']
            subprocess.check_output(cmdline)
            return DefaultState()
        return self

class MotionState(State):
    """
    The motion detect mode state. The can't get here atm.
    """

    def on_event(self, event):
        if event == 'motion_off':
            return DefaultState()
        return self

class SimpleDevice(object):
    """
    A simple state machine that mimics the high level functionality.
    """

    def __init__(self):
        """ Initialise the components. """
        # Start with the default state.
        self.state = DefaultState()

    def on_event(self, event):
        """
        This is the core of the state machine. Incoming events are delegated to the given states which handle the state.
        """

        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)

class ProducerThread(threading.Thread):
    def __init__(self, target=None, name=None):
        super().__init__()
        self.target = target
        self.name = name
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        server_address = ('0.0.0.0', 5005)
        logging.debug('starting up on %s port %s' % server_address)
        self.sock.bind(server_address)

    def run(self):
        # Listen for incoming connection
        self.sock.listen(1)

        while True:
            # Wait for a connection
            logging.debug('waiting for connection...')
            connection, client_address = self.sock.accept()
            try:
                logging.debug('connection from %s %s' % client_address)
                while True:
                    message = connection.recv(16)
                    logging.debug('recieved "%s"' % message)
                    if message:
                        message = message.decode("utf-8")
                        if not q.full():
                            q.put(message)
                            logging.debug('putting "' + str(message) + '" in queue: ' + str(q.qsize()) + ' messages in queue')
            finally:
                # Clean up the connection
                connection.close()

class ConsumerThread(threading.Thread):
    def __init__(self, target=None, name=None):
        super().__init__()
        self.target = target
        self.name = name
        self.stream_state = 0
        self.motion_state = 0
        self.device = SimpleDevice()

    def run(self):
        while True:
            if not q.empty():
                message = q.get()
                if message != 'stop':
                    logging.debug('fetching (' + str(message) + '): ' + str(q.qsize()) + ' items in queue')
                    self.device.on_event(message)
                    self.device.state

if __name__ == '__main__':
    p = ProducerThread(name='producer')
    c = ConsumerThread(name='consumer')

    p.start()
    time.sleep(2)
    c.start()
    time.sleep(2)
