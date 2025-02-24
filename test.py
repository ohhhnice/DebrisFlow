import cv2
import os
import queue
import numpy as np


class ExtractFeatures:
    def __init__(
        self,
        video_name: str,
        src_folder: str,
    ):
        self.video_naem = video_name
        self.src_folder = src_folder
        self.src_path = os.path.join(src_folder, video_name)

        self.cap = cv2.VideoCapture(self.src_path)

    def test(self):
        ret, frame = self.cap.read()
        print(frame.shape)
        print(type(np.mean(frame)))
        print(np.mean(frame != 0))

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
            print("视频资源已释放")

    def __del__(self):
        self.release()


if __name__ == "__main__":
    video_name = "3.mp4"
    src_folder = "./data/sam/processed"
    a = ExtractFeatures(video_name, src_folder)
    a.test()
