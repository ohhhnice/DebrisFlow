import os
import sys
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "external_project"))

from argparse import ArgumentParser
from src.data_preprocessing.sam_video import SamVideo
from src.extract_features.extract_features import ExtractFeatures
from src.XGBoost.predict import xgb_predict


class DebrisFlowPredict:
    def __init__(
        self,
        video_name: str,
        src_folder: str,
        samed_video_folder: str,
        features_folder: str,
        output_folder: str,
        slice_windows_size: int,
        XGB_model_path: str,
        point_coordinates: list[int],
        extract_freq: int,
        **kwargs,
    ):
        self.src_folder = src_folder
        self.video_name = video_name
        self.samed_video_folder = samed_video_folder
        self.features_folder = features_folder
        self.output_folder = output_folder
        self.slice_windows_size = slice_windows_size
        self.XGB_model_path = XGB_model_path
        self.point_coordinates = point_coordinates
        self.extract_freq = extract_freq

        self.sam = SamVideo(
            model_type=kwargs["sam_model_type"],
            model_device=kwargs["sam_model_device"],
            checkpoint=kwargs["sam_checkpoint"],
        )

    def predict_video(self):
        samed_video_name = self.sam.predict_video(
            self.video_name,
            self.src_folder,
            self.samed_video_folder,
            self.point_coordinates,
            self.extract_freq,
        )
        extract_features = ExtractFeatures(
            samed_video_name,
            self.samed_video_folder,
            self.features_folder,
            self.slice_windows_size,
        )
        extract_features.extract_video_features()
        xgb_predict(
            None,
            self.src_folder,
            self.video_name,
            self.XGB_model_path,
            self.output_folder,
            self.features_folder,
        )

    def predict_frame(self, frame_idx: int):
        samed_video_name = self.sam.predict_frame(
            self.video_name,
            self.src_folder,
            self.samed_video_folder,
            self.point_coordinates,
            frame_idx,
            self.slice_windows_size,
        )
        extract_features = ExtractFeatures(
            samed_video_name,
            self.samed_video_folder,
            self.features_folder,
            self.slice_windows_size,
        )
        extract_features.extract_video_features()
        xgb_predict(
            self.src_folder,
            self.video_name,
            self.XGB_model_path,
            self.output_folder,
        )


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
        "--samed_video_folder",
        type=str,
        default="./data/sam/processed",
        help="processed video path by SAM",
    )
    parser.add_argument(
        "--features_folder",
        type=str,
        default="./data/extracted_features",
        help="The path saving extracted features based on samed video",
    )
    parser.add_argument(
        "--output_folder",
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
    parser.add_argument(
        "--sam_model_type",
        type=str,
        default="vit_h",
        help="The model type for SAM (vit_h, vit_base, vit_large, vit_base_patch16_224)",
    )
    parser.add_argument(
        "--sam_model_device",
        type=str,
        default="cuda",
        help="The device for SAM model (cpu, cuda)",
    )
    parser.add_argument(
        "--sam_checkpoint",
        type=str,
        default="models\pretrained\sam\sam_vit_h_4b8939.pth",
        help="The checkpoint for SAM model",
    )
    opt = parser.parse_args()
    return opt


if __name__ == "__main__":
    opt = parse_opt()
    DebrisFlow = DebrisFlowPredict(**vars(opt))
    DebrisFlow.predict_video()
