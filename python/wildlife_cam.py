from gpiozero import MotionSensor
import logging
from datetime import datetime
from subprocess import call
import picamera
import time
import os

# Create required directories
if not os.path.exists('/home/pi/wildlife_camera/log'):
    os.makedirs('/home/pi/wildlife_camera/log')

if not os.path.exists('/home/pi/wildlife_camera/videos'):
    os.makedirs('/home/pi/wildlife_camera/videos')

# Create logfile
logfile = "/home/pi/wildlife_camera/log/trailcam_log_"+str(datetime.now().strftime("%Y%m%d-%H%M"))+".csv"
logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d, %H:%M:%S,')

pir = MotionSensor(17)

print('Starting')
logging.info('Starting')

# Wait an initial duration to allow PIR to settle
time.sleep(10)

count = 0

while True:
    print('Waiting for motion...')
    pir.wait_for_motion()
    count += 1
    logging.info('Motion detected')
    print('Motion detected [', count, ']')
    while pir.motion_detected:
        print('Capturing video')
        ts = '{:%d%m%Y_%H%M%S}'.format(datetime.now())
        with picamera.PiCamera() as camera:
            camera.resolution = (1024, 768)
            camera.annotate_background = picamera.Color('black')
            camera.start_recording('/home/pi/wildlife_camera/videos/video.h264')
            start = datetime.now()
            while (datetime.now() - start).seconds < 30:
                camera.annotate_text = 'NatureCam_'+datetime.now().strftime('%d_%m_%y_%H:%M:%S')
                camera.wait_recording(0.2)
            camera.stop_recording()
        time.sleep(5)
        timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
        input_video = '/home/pi/wildlife_camera/videos/video.h264'
        logging.info('Attempting to save video')

        if os.path.isdir('/mnt/usb/videos'):
            logging.info('Saving to /mnt/usb/videos/')
            output_video = '/mnt/usb/videos/{}.mp4'.format(timestamp)
        else:
            logging.info('USB drive not mounted')
        call(['MP4Box', '-add', input_video, output_video])
        time.sleep(10)
    print('Motion ended')
    logging.info('Motion ended')

