import sys
from pathlib import Path
from argparse import ArgumentParser
import torch
import cv2
import numpy as np
from PIL import Image

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.vgg_model.vgg import load_extract_feature_vgg_model, transformer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def parse_opt():

    parser = ArgumentParser()
    parser.add_argument(
        "--model_weights_path",
        type=str,
        default="./models/trained/vgg/vgg19_epoch5_accuracy1.0_loss2.4331241250038147.pth",
        help="model weights path",
    )
    parser.add_argument(
        "--feature_size", type=int, default=200, help="the number of the features"
    )
    parser.add_argument("--class_size", type=int, default=2, help="the number of class")
    parser.add_argument("--device", type=str, default=device)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    opts = parse_opt()
    vgg19 = load_extract_feature_vgg_model(**vars(opts))

    src_path = "./data/sam/raw/3.mp4"
    cap = cv2.VideoCapture(src_path)
    ret, frame = cap.read()
    cap.release()

    transform = transformer()
    img = frame.astype(np.uint8)
    img = Image.fromarray(img)
    img = transform(img).unsqueeze(0).to(device)
    vgg19_feature = vgg19(img)
    print(vgg19_feature)
