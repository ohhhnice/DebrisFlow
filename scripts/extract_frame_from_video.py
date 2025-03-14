import sys
from pathlib import Path
import os
import cv2
from PIL import Image

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.utils.frame_processor import FrameProcessor


def extract_frame_from_video(video_path: str, frame_idx: int, save_photo_path: str):
    frame_process = FrameProcessor()
    frame = frame_process.get_frame(video_path, frame_idx)

    save_dir = os.path.dirname(save_photo_path)
    os.makedirs(save_dir, exist_ok=True)
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    image.save(save_photo_path)


if __name__ == "__main__":
    video_path = "data/sam/raw/田家沟_20230718T173504Z_20230718T174350Z.mp4"
    frame_idx = 10000
    save_photo_path = "article_source/photo/展示图片.jpg"
    extract_frame_from_video(video_path, frame_idx, save_photo_path)
