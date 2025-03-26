import sys
from pathlib import Path
from argparse import ArgumentParser
import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.vgg_model.train import train_based_on_vgg19


def parse_opt():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    parser = ArgumentParser()
    parser.add_argument(
        "--train_data_folder", type=str, default="./data/vgg", help="train dataset root"
    )
    parser.add_argument(
        "--val_data_folder", type=str, default="./data/vgg", help="val dataset root"
    )
    parser.add_argument("--batch_size", type=int, default=3, help="batch size")
    parser.add_argument(
        "--model_weights_path",
        type=str,
        default="models/pretrained/vgg/vgg19_weights.pth",
        help="model weights path",
    )
    parser.add_argument(
        "--feature_size", type=int, default=200, help="the number of the features"
    )
    parser.add_argument("--class_size", type=int, default=2, help="the number of class")
    parser.add_argument("--device", type=str, default=device)
    parser.add_argument("--lr", type=float, default=0.001, help="learning rate")
    parser.add_argument(
        "--log_dir", type=str, default="src/vgg_model/logs", help="log dir"
    )
    parser.add_argument("--epochs", type=int, default=50, help="number of epochs")
    parser.add_argument(
        "--save_pth_dir",
        type=str,
        default="models/trained/vgg",
        help="save train pth dir",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    opts = parse_opt()

    train_based_on_vgg19(**vars(opts))
