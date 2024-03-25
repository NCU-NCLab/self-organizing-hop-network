from RTMP import RTMP
import sys, cv2
from wifi_auto_connect import WiFi_Scanner


ip_end_num = 1
interface = "wlan1"
video_setting = {
    "width": 640,
    "height": 480,
    "fps": 29
}

if len(sys.argv) > 1:
    ip_end_num = sys.argv[1]
if len(sys.argv) > 2:
    interface = sys.argv[2]

wfs = WiFi_Scanner(interface)

out_rtmp = RTMP()
out_rtmp.push_connect(video_setting['width'], video_setting["height"], video_setting['fps'])

while True:
    bwf = wfs.get_best_wifi_info_maxid(ip_end_num)
    if bwf is None:
        print("\033[91mNo WiFi is available\033[00m")
        continue
    prefix_ip = "192.168.10"+bwf.SSID[-1]
    wfs.connect(bwf, ip_end_num)
    in_rtmpUrl = f"rtmp://{prefix_ip}.1:1935/live"
    camera_path = "result.mp4"

    cap = cv2.VideoCapture(in_rtmpUrl)
    video_setting['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_setting["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_setting['fps'] = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('relay.mp4', fourcc, 20.0, (video_setting['width'], video_setting["height"]))
    
    while 1:
        try:
            ret,frame = cap.read()
            cv2.imshow('frame',frame)
            # out.write(frame)
            out_rtmp.push_img_str(frame.tostring())
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except:
            print("\033[91mreceive frame is over\033[00m")
            print("\033[93msave video\033[00m")
            break
    cap.release()
    out.release()
    cv2.destroyAllWindows()
