import pyrealsense2 as rs
import numpy as np
import cv2
import time
import os
from datetime import datetime as dt

WIDTH = 1280
HEIGHT = 720
FPS = 30

align = rs.align(rs.stream.color)
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.bgr8, FPS)
config.enable_stream(rs.stream.depth, WIDTH, HEIGHT, rs.format.z16, FPS)

now = dt.now()
nowstr = now.strftime('%Y-%m-%d-%H')
floder = '/home/pi/data'
os.makedirs(floder, exist_ok=True)
file_name = '/home/pi/data/d435data.bag'
config.enable_record_to_file(file_name)
pipeline.start(config)

try:
    time0 = time.time()
    time_delay = 60
    while True:
        frames = pipeline.wait_for_frames()
        if (time.time() - time0) >= time_delay:
            print("---------------------finish!----------------------------")
            break

finally:
    # Stop streaming
    time.sleep(5)
    pipeline.stop()
