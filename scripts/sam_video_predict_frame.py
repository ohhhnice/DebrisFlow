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
    parser.add_argument("--video_name", type=str, default="田家沟_20230718T173504Z_20230718T174350Z.mp4", help="video name")
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
        default=[[800,700]] + [[1400,480]] + [[286, 928], [769, 721], [1054, 621], [1302, 535], [1469, 486], [1393, 504], [1185, 579], [918, 673], [633, 777], [478, 847], [169, 979]],
        help="The coordinates of the object of interest",
    )
    parser.add_argument(
        "--frame_idx",
        type=int,
        default=7200,
        help="The frame idx need to predict",
    )
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
    sam = SamVideo(
        model_type="vit_h",
        model_device="cuda",
        checkpoint="models\pretrained\sam\sam_vit_h_4b8939.pth",
    )
    sam.predict_frame(**vars(opts))
