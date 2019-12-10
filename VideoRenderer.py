import cv2 as cv
import os


class VideoRenderer:

    def __init__(self):
        self.to_remove = []
        self.index = 0

    def write(self, frame):
        cv.imwrite('output/%04d.png' % self.index, frame)
        self.to_remove.append('%04d.png' % self.index)
        self.index += 1

    def render(self):
        print("Rendering video...")
        os.chdir('./output')
        os.system("ffmpeg -framerate 60 -i %04d.png -y -an -pix_fmt yuv420p -c:v libx264 -preset slow -crf 17 -r 60 -c:a aac Trainjourneys.mp4")
        print("Removing frames...")
        for frame in self.to_remove:
            os.remove(frame)
