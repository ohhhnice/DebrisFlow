import sys
from pathlib import Path
from argparse import ArgumentParser

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "external_project"))

from src.make_train_dataset.make_train_dataset import MakeDataSet


def parse_opt():
    parser = ArgumentParser()
    parser.add_argument(
        "--video_file_path",
        type=str,
        default="data/sam/raw/3.mp4",
        help="the path of the video file",
    )
    parser.add_argument(
        "--is_debrisflow",
        type=int,
        default=1,
        help="the label of the video file (1 for debris flow, 0 for not)",
    )
    parser.add_argument(
        "--data_type",
        type=str,
        default="train",
        help="the type of the dataset (train or val)",
    )
    parser.add_argument(
        "--frame_idx",
        type=int,
        default=10,
        help="the idx of the frame which will be extracted",
    )
    parser.add_argument(
        "--slice_windows_size",
        type=int,
        default=3,
        help="The size for slice windows to extract features",
    )
    parser.add_argument(
        "--save_folder",
        type=str,
        default="data/dataset",
        help="the folder for saving the dataset",
    )
    parser.add_argument(
        "--show_photo",
        type=bool,
        default=True,
        help="whether to show the photo",
    )
    parser.add_argument(
        "--sam_model_type",
        type=str,
        default="vit_h",
        help="the type of the SAM model",
    )
    parser.add_argument(
        "--sam_model_device",
        type=str,
        default="cuda",
        help="the device of the SAM model",
    )
    parser.add_argument(
        "--sam_checkpoint",
        type=str,
        default="models\pretrained\sam\sam_vit_h_4b8939.pth",
        help="the checkpoint of the SAM model",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    opts = parse_opt()

    data = MakeDataSet(**vars(opts))
    data.make_dataset()
