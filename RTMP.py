import subprocess as sp


class RTMP:
    def __init__(self, url="rtmp://127.0.0.1:1935/live"):
        self.url = url
        self.pipe = None

    def push_connect(self, width=1920, height=1080, fps=25):
        command = ['ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec','rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', "{}x{}".format(width, height),
            '-r', str(fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            '-f', 'flv', 
            self.url]
        self.pipe = sp.Popen(command, stdin=sp.PIPE)

    def push_img_str(self, img_str):
        if self.pipe is None:
            self.push_connect()
        if self.pipe is not None:
            self.pipe.stdin.write(img_str)
        else:
            print("RTMP not connected yet")