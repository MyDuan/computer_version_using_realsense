import pyrealsense2 as rs
import numpy as np
import cv2
import time
import os
from datetime import datetime as dt

WIDTH = 1280
HEIGHT = 720
FPS = 6

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
prof = pipeline.start(config)
#dev = prof.get_device().as_recorder()

try:
    time0 = time.time()
    time_delay = 60
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if not color_frame or not depth_frame:
            continue
        '''
        color_image = np.asanyarray(color_frame.get_data())
        cv2.namedWindow('confirm_video_window', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('confirm_video_window', color_image)
        c = cv2.waitKey(1)

        if cv2.getWindowProperty('confirm_video_window', cv2.WND_PROP_AUTOSIZE) < 1:
            break
        if c == 27:
            cv2.destroyAllWindows()
            break
        
        #dev.pause()
        #time.sleep(0.6)
        #dev.resume()
        '''
        if (time.time() - time0) >= time_delay:
            print("---------------------finish!----------------------------")
            break

finally:
    # Stop streaming
    #time.sleep(5)
    pipeline.stop()
