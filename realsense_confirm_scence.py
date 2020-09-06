import pyrealsense2 as rs
import numpy as np
import cv2


WIDTH = 1280
HEIGHT = 720
FPS = 30

align = rs.align(rs.stream.color)
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.bgr8, FPS)
config.enable_stream(rs.stream.depth, WIDTH, HEIGHT, rs.format.z16, FPS)
config = pipeline.start(config)

# filter setting
dec_filter = rs.decimation_filter()   # Decimation - reduces depth frame density
dec_filter.set_option(rs.option.filter_magnitude, 4)
spat_filter = rs.spatial_filter()     # Spatial    - edge-preserving spatial smoothing
dec_filter.set_option(rs.option.filter_magnitude, 2)
spat_filter.set_option(rs.option.filter_smooth_alpha, 0.5)
spat_filter.set_option(rs.option.filter_smooth_delta, 20)
spat_filter.set_option(rs.option.holes_fill, 3)
temp_filter = rs.temporal_filter()    # Temporal   - reduces temporal noise
temp_filter.set_option(rs.option.filter_smooth_alpha, 0.5)
temp_filter.set_option(rs.option.filter_smooth_delta, 20)
temp_filter.set_option(rs.option.holes_fill, 3)
depth_to_disparity = rs.disparity_transform(True)
disparity_to_depth = rs.disparity_transform(False)
hole_filling = rs.hole_filling_filter()
hole_filling.set_option(rs.option.holes_fill, 1)

# get intrinsics
profile = config.get_stream(rs.stream.depth)
depth_intr = profile.as_video_stream_profile().get_intrinsics()

try:
    while True:

        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)  # aligned the position of pixel between color image and depth image

        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()
        
        # get the distance before post processing
        x = int(WIDTH / 2)
        y = int(HEIGHT / 2)

        depth = depth_frame.get_distance(x, y)
        depth_point = rs.rs2_deproject_pixel_to_point(depth_intr, [x, y], depth)
        print(depth_point)
        
        # post processing
        depth_frame = dec_filter.process(depth_frame)
        depth_frame = depth_to_disparity.process(depth_frame)
        depth_frame = spat_filter.process(depth_frame)
        depth_frame = temp_filter.process(depth_frame)
        depth_frame = disparity_to_depth.process(depth_frame)
        depth_frame = hole_filling.process(depth_frame)

        depth_color_frame = rs.colorizer().colorize(depth_frame)
        depth_color_image = np.asanyarray(depth_color_frame.get_data())

        color_image = np.asanyarray(color_frame.get_data())

        if not color_frame or not depth_frame:
            continue
        else:
            half_size = (int(WIDTH/2), int(HEIGHT/2))
            half_color = cv2.resize(color_image, half_size)
            half_depth_color = cv2.resize(depth_color_image, half_size)
            confirm_video = cv2.hconcat([half_color, half_depth_color])
            cv2.namedWindow('confirm_video_window', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('confirm_video_window', confirm_video)
        
        c = cv2.waitKey(1)
        
        if cv2.getWindowProperty('confirm_video_window', cv2.WND_PROP_AUTOSIZE) < 1:
            break
        if c == 27:
            cv2.destroyAllWindows()
            break

finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()
