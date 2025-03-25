import sys
from pathlib import Path
from argparse import ArgumentParser
import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.extract_features.extract_features import ExtractFeatures


def parse_opt():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    parser = ArgumentParser()
    parser.add_argument("--video_name", type=str, default="3.mp4", help="video name")
    parser.add_argument(
        "--src_folder",
        type=str,
        default="./data/sam/raw",
        help="The folder path of video processed by sam ",
    )
    parser.add_argument(
        "--dst_folder",
        type=str,
        default="./data/extracted_features",
        help="The folder path which saves the extracted features using for xgboost",
    )
    parser.add_argument(
        "--vgg_model_weights_path",
        type=str,
        default="./models/trained/vgg/vgg19_epoch5_accuracy1.0_loss2.4331241250038147.pth",
        help="vgg model weights path",
    )
    parser.add_argument(
        "--feature_size", type=int, default=200, help="the number of the features"
    )
    parser.add_argument("--device", type=str, default=device)
    parser.add_argument(
        "--slice_windows_size",
        type=int,
        default=30,
        help="The size for slice windows to extract features",
    )
    opt = parser.parse_args()
    return opt


if __name__ == "__main__":
    opts = parse_opt()
    ext_feat = ExtractFeatures(**vars(opts))
    ext_feat.extract_video_features()
