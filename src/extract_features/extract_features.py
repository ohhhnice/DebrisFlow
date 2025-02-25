import numpy as np
import pandas as pd
import os
import cv2
import sys
from pathlib import Path
from tqdm import tqdm
import queue
from PIL import Image
import torch
from torchvision.models.vgg import VGG

FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.utils.load_video import extract_frames
from src.vgg_model.vgg import load_extract_feature_vgg_model, transformer


class ExtractFeatures:
    def __init__(
        self,
        video_name: str,
        src_folder: str,
        dst_folder: str,
        vgg_model_weights_path: str,
        feature_size: int,
        device: str = torch.device("cuda" if torch.cuda.is_available() else "cpu"),
        slice_windows_size: int = 30,
    ):
        self.video_name = video_name
        self.src_folder = src_folder
        self.dst_folder = dst_folder
        self.vgg_model_weights_path = vgg_model_weights_path
        self.feature_size = feature_size
        self.device = device
        self.slice_windows_size = slice_windows_size
        self.src_path = os.path.join(src_folder, video_name)

        self.time_tmp_feat_queue = queue.Queue()
        self.cap = cv2.VideoCapture(self.src_path)
        self.vgg19 = load_extract_feature_vgg_model(
            self.vgg_model_weights_path, self.feature_size, 2, self.device
        )

    def extract_video_features(self) -> str:
        print("=" * 30 + " EXTRACT VIDEO FEATRUES " + "=" * 30 + "\n")
        _, video_frame_count, _ = extract_frames(self.src_path)
        if video_frame_count < self.slice_windows_size:
            print("窗口取值过大!")
            return ""

        self.init_time_tmp_feat_queue()
        os.makedirs(self.dst_folder, exist_ok=True)
        base_name, _ = os.path.splitext(self.video_name)
        file_name = f"{base_name}.csv"
        dst_path = os.path.join(self.dst_folder, file_name)

        for frameIdx in tqdm(
            range(video_frame_count - self.slice_windows_size + 1),
            desc="Extract video features",
            unit="frame",
        ):
            ret, frame = self.cap.read()
            if not ret:
                break
            frame_feature = self.calculate_frame_features(frame)
            if not os.path.exists(dst_path):
                frame_feature.to_csv(dst_path, mode="w", header=True, index=False)
            else:
                frame_feature.to_csv(dst_path, mode="a", header=False, index=False)
        return file_name

    def calculate_frame_features(self, frame: np.ndarray) -> np.ndarray:
        time_tmp_feat = self.extract_frame_tmp_time_features(frame)
        self.time_tmp_feat_queue.put(time_tmp_feat)
        vgg_feat = self.extract_vgg_features(frame)
        time_feat = self.calculate_time_features()
        self.time_tmp_feat_queue.get()

        merged_feat = np.concatenate((time_feat, vgg_feat), axis=0)
        colnames = ["mean_grey", "area_ratio"] + [
            f"vgg_{i}" for i in range(len(vgg_feat))
        ]
        return pd.DataFrame([merged_feat], columns=colnames)

    def extract_vgg_features(self, frame: np.ndarray) -> np.ndarray:
        transform = transformer()
        img = frame.astype(np.uint8)
        img = Image.fromarray(img)
        img = transform(img).unsqueeze(0).to(self.device)
        vgg19_feature = self.vgg19(img).squeeze().numpy()
        return vgg19_feature

    def extract_frame_tmp_time_features(self, frame: np.ndarray) -> dict:
        """灰度均值、面积比例"""
        tmp_time_feat = {"mean_grey": np.mean(frame), "area_ratio": np.mean(frame != 0)}
        return tmp_time_feat

    def calculate_time_features(self) -> np.ndarray:
        feat = []
        feat.append(self.calculate_mean_grey_variance())
        feat.append(self.calculate_area_ratio_variance())
        return np.array(feat)

    def calculate_mean_grey_variance(self) -> np.float64:
        grey_list = []
        for dic in self.time_tmp_feat_queue.queue:
            grey_list.append(dic["mean_grey"])
        return np.var(grey_list)

    def calculate_area_ratio_variance(self) -> np.float64:
        area_ratio_list = []
        for dic in self.time_tmp_feat_queue.queue:
            area_ratio_list.append(dic["area_ratio"])
        return np.var(area_ratio_list)

    def init_time_tmp_feat_queue(self):
        cap = cv2.VideoCapture(self.src_path)
        for _ in range(self.slice_windows_size - 1):
            ret, frame = cap.read()
            if not ret:
                break
            time_tmp_feat = self.extract_frame_tmp_time_features(frame)
            self.time_tmp_feat_queue.put(time_tmp_feat)
        cap.release()

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
            print("视频资源已释放")

    def __del__(self):
        self.release()
