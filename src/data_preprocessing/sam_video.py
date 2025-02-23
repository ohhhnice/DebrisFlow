import sys
import os
import cv2
from tqdm import tqdm
import numpy as np
from pathlib import Path
from typing import Optional
from argparse import ArgumentParser

FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
    sys.path.append(str(ROOT / "external_project"))

from src.utils.load_video import extract_frames
from external_project.segment_anything import SamPredictor, sam_model_registry


class SamVideo:
    def __init__(
        self,
        model_type: str,
        model_device: str,
        checkpoint: any,
    ):
        self.checkpoint = checkpoint
        self.model_type = model_type
        self.model_device = model_device
        self.loadModel()

    def predict_frame(self, **kwargs):
        pass

    def predict_video(
        self,
        video_name: str,
        src_folder: str,
        dst_folder: str,
        point_coordinates: list[int],
        extract_freq: int = 1,
    ):
        os.makedirs(dst_folder, exist_ok=True)
        src_path = os.path.join(src_folder, video_name)
        save_path = os.path.join(dst_folder, video_name)
        video_fps, video_frame_count, img_shape = extract_frames(src_path)

        cap = cv2.VideoCapture(src_path)
        # 创建一个 VideoWriter 对象，用于写入新的视频文件
        fourcc = cv2.VideoWriter.fourcc(*"mp4v")  # 选择编码格式为MP4
        out = cv2.VideoWriter(save_path, fourcc, video_fps, img_shape)

        # 将每一帧写入输出视频
        print("=" * 30 + " SAM VIDEO " + "=" * 30)
        for frameIdx in tqdm(
            range(video_frame_count), desc="Writing frames(SAM)", unit="frame"
        ):
            # for frameIdx in range(video_frame_count):
            if frameIdx % extract_freq != 0:
                continue
            ret, frame = cap.read()
            if not ret:
                break
            output_frame = self._get_masked_photo(frame, point_coordinates)
            out.write(output_frame)
        out.release()
        cap.release()

    def loadModel(self):
        model = sam_model_registry[self.model_type](checkpoint=self.checkpoint)
        model.to(device=self.model_device)
        self.predictor = SamPredictor(model)

    def _get_masked_photo(self, image, point_coordinates) -> np.array:
        self.predictor.set_image(image)
        points = np.array([point_coordinates])  # 传设置预标记点
        masks, scores, _ = self.predictor.predict(  # 使用SAM_predictor返回覆盖、置信度
            point_coords=points,
            point_labels=np.array(
                [1]
            ),  # 设置label（需要预测的主体一般设置为1，背景一般设置为0）
            multimask_output=True,
        )
        idx = np.argmax(scores)
        masked_arr = masks[idx]
        return masked_arr[..., np.newaxis] * image


def parse_opt():
    parser = ArgumentParser()
    parser.add_argument("--video_name", type=str, default="3.mp4", help="video name")
    parser.add_argument(
        "--src_folder",
        type=str,
        default="./data/sam/raw",
        help="video folder path",
    )
    parser.add_argument(
        "--dst_folder",
        type=str,
        default="./data/sam/processed",
        help="processed video folder by SAM",
    )
    parser.add_argument(
        "--point_coordinates",
        nargs="+",
        type=int,
        default=[800, 700],
        help="The coordinates of the object of interest.",
    )
    parser.add_argument(
        "--extract_freq",
        type=int,
        default=30,
        help="The frequency to extract frames",
    )
    opt = parser.parse_args()
    return opt


if __name__ == "__main__":
    opts = parse_opt()
    sam = SamVideo(
        model_type="vit_h",
        model_device="cpu",
        checkpoint="models\pretrained\sam\sam_vit_h_4b8939.pth",
    )
    sam.predict_video(**vars(opts))
