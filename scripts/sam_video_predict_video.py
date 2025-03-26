import sys
from pathlib import Path
from argparse import ArgumentParser

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
    sys.path.append(str(ROOT / "external_project"))

from src.data_preprocessing.sam_video import SamVideo


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
        type=list[list[int]],
        default=[[800, 700]],
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
