import cv2


def extract_frames(videoPath):
    cap = cv2.VideoCapture(videoPath)  # 打开视频文件
    fps = cap.get(cv2.CAP_PROP_FPS)  # 获取视频帧率
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ret, frame = cap.read()
    cap.release()
    return fps, frameCount, frame.shape[:2][::-1]
