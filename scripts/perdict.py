import os
import sys
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from argparse import ArgumentParser
from src.data_preprocessing.sam_video import SamVideo
from src.utils.load_video import extract_frames
from src.extract_features.extract_features import ExtractFeatures
from src.XGBoost.predict import xgb_predict


class DebrisFlowPredict:
    def __init__(
        self,
        src_folder_path: str,
        video_Name: str,
        samed_video_path: str,
        features_path: str,
        output_path: str,
        slice_windows_size: int,
        XGB_model_path: str,
    ):
        self.src_folder_path = src_folder_path
        self.video_Name = video_Name
        self.samed_video_path = samed_video_path
        self.features_path = features_path
        self.output_path = output_path
        self.slice_windows_size = slice_windows_size
        self.XGB_model_path = XGB_model_path

        self.sam = SamVideo()
        self.extract_features = ExtractFeatures()

        self.loadVideoInfo()

    def predict_video(self):
        os.makedirs(self.samed_video_path, exist_ok=True)
        self.sam.predict_video(
            self.src_folder_path, self.video_Name, self.samed_video_path
        )
        os.makedirs(self.features_path, exist_ok=True)
        self.extract_features.extract_all_features(
            self.samed_video_path,
            self.features_path,
            self.video_Name,
            self.slice_windows_size,
        )
        xgb_predict(
            None,
            self.src_folder_path,
            self.video_Name,
            self.XGB_model_path,
            self.output_path,
            self.features_path,
        )

    def predict_frame(self, frame_idx: int):
        os.makedirs(self.samed_video_path, exist_ok=True)
        self.sam.predict_video(
            self.src_folder_path, self.video_Name, self.samed_video_path
        )
        array_list = self.extract_features.get_array_list(
            self.src_folder_path, self.video_Name, frame_idx, self.slice_windows_size
        )
        features_array = self.extract_features.extract_frame_features(array_list)
        xgb_predict(
            features_array,
            self.src_folder_path,
            self.video_Name,
            self.XGB_model_path,
            self.output_path,
        )

    def loadVideoInfo(self):
        self.videoFPS, self.videoFrameCount, self.imageShape = extract_frames(
            os.path.join(self.src_folder_path, self.video_Name)
        )  # fps, 帧数, 图像大小
        print("videoFPS: ", self.videoFPS)
        print("videoFrameCount: ", self.videoFrameCount)
        print("imageShape: ", self.imageShape)


def parse_opt():
    parser = ArgumentParser()
    parser.add_argument("--video_Name", type=str, default="3.mp4", help="video name")
    parser.add_argument(
        "--src_folder_path",
        type=str,
        default="./data/sam/raw",
        help="video folder path",
    )
    parser.add_argument(
        "--samed_video_path",
        type=str,
        default="./data/sam/processed",
        help="processed video path by SAM",
    )
    parser.add_argument(
        "--features_path",
        type=str,
        default="./data/extracted_features",
        help="The path saving extracted features based on samed video",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="./data/output",
        help="The path saving processed video and csv file by all workflow",
    )
    parser.add_argument(
        "--slice_windows_size",
        type=int,
        default=30,
        help="The size for slice windows to extract features",
    )
    parser.add_argument(
        "--XGB_model_path",
        type=str,
        default=None,
        help="The trained XGBoost model path",
    )
    opt = parser.parse_args()
    return opt


if __name__ == "__main__":
    opt = parse_opt()
    DebrisFlow = DebrisFlowPredict(**vars(opt))
    print(DebrisFlow.video_Name)
    print(DebrisFlow.src_folder_path)
    print(DebrisFlow.samed_video_path)
    print(DebrisFlow.features_path)
    print(DebrisFlow.output_path)
    print(DebrisFlow.slice_windows_size)
    # DebrisFlow.predict_video()
