import cv2


def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)  # 打开视频文件
    fps = cap.get(cv2.CAP_PROP_FPS)  # 获取视频帧率
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    _, frame = cap.read()
    cap.release()
    print(f"fps: {fps}\nframeCount: {frameCount}\nImage shape: {frame.shape[:2][::-1]}")
    return fps, frameCount, frame.shape[:2][::-1]
