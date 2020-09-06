import pyrealsense2 as rs
import numpy as np
import cv2
import time
from datetime import datetime as dt
import boto3
import os
import shutil

WIDTH = 1280#640
HEIGHT = 720#480
FPS = 6
#THRESHOLD = 1.5


def main():
    now = dt.now()
    nowstr = now.strftime('%Y-%m-%d-%H')
    color_floder = '/home/pi/imgs/'+nowstr+'/'
    deep_floder = '/home/pi/deep_imgs/'+nowstr+'/'
    os.makedirs(color_floder, exist_ok=True)
    os.makedirs(deep_floder, exist_ok=True)
    align = rs.align(rs.stream.color)
    config = rs.config()
    config.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.bgr8, FPS)
    config.enable_stream(rs.stream.depth, WIDTH, HEIGHT, rs.format.z16, FPS)

    pipeline = rs.pipeline()
    profile = pipeline.start(config)
    depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
    #max_dist = THRESHOLD/depth_scale

    try:
        time0 = time.time()
        while True:
            # フレーム取得
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)

            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()
            if not depth_frame or not color_frame:
                continue
            # RGB画像
            color_image = np.asanyarray(color_frame.get_data())

            # 深度画像
            depth_color_frame = rs.colorizer().colorize(depth_frame)
            depth_color_image = np.asanyarray(depth_color_frame.get_data())

            # 指定距離以上を無視した深度画像
            '''
            depth_image = np.asanyarray(depth_frame.get_data())
            depth_filtered_image = (depth_image < max_dist) * depth_image
            depth_gray_filtered_image = (depth_filtered_image * 255. / max_dist).reshape((HEIGHT, WIDTH)).astype(np.uint8)

            # 指定距離以上を無視したRGB画像
            color_filtered_image = (depth_filtered_image.reshape((HEIGHT, WIDTH, 1)) > 0) * color_image
            '''
            # 表示
            #cv2.namedWindow('demo', cv2.WINDOW_AUTOSIZE)
            #cv2.imshow('demo', color_image)

            c = cv2.waitKey(1)

            # 自動的に保存
            count = 0
            for filename in os.listdir(color_floder):
                if filename.endswith('.jpg'):
                    count += 1
            if count >= 10:
                break
            time_delay = 300
            if (time.time() - time0) > time_delay:
                #print("saving")
                cv2.imwrite(color_floder+'{}.jpg'.format(count + 1), color_image)
                cv2.imwrite(deep_floder+'deep_{}.jpg'.format(count + 1), depth_color_image)
                time0 += time_delay
            if c == 27:
                break
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('data-saving-bucket')
        for filename in os.listdir(color_floder):
            bucket.upload_file(color_floder+filename, 'color_images/'+nowstr+'/'+filename)
        for filename in os.listdir(deep_floder):
            bucket.upload_file(deep_floder +filename, 'deep_images/'+nowstr+'/'+filename)
        #shutil.rmtree('/home/pi/imgs/')
        #shutil.rmtree('/home/pi/deep_imgs/')
        #os.mkdir('/home/pi/imgs/')
        #os.mkdir('/home/pi/deep_imgs/')


if __name__ == "__main__":
    main()
