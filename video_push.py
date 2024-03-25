import subprocess as sp
import sys
from RTMP import RTMP
import cv2 as cv

# camera_path = "/dev/video0" or "result.mp4"
if len(sys.argv) > 1:
    camera_path = sys.argv[1]
else:
    camera_path = "/dev/video0"

cap = cv.VideoCapture(camera_path)

video_setting = {
    "width": int(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
    "height": int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)),
    "fps": int(cap.get(cv.CAP_PROP_FPS))
}

out_rtmp = RTMP()
out_rtmp.push_connect(video_setting['width'], video_setting["height"], video_setting['fps'])

# read webcamera
while(cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        print("Opening camera is failed")
        break
   
    # write to pipe
    out_rtmp.push_img_str(frame.tostring())
