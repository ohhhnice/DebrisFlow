import sys
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "external_project"))

from argparse import ArgumentParser
from run.predict import DebrisFlowPredict


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
        default="cpu",
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
