import sys
from pathlib import Path
from argparse import ArgumentParser
import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


from src.XGBoost.train import train_xgboost


def parse_opt():
    parser = ArgumentParser()
    parser.add_argument(
        "--csv_name",
        type=str,
        default="3.csv",
        help="the name of train dataset csv",
    )
    parser.add_argument(
        "--src_folder",
        type=str,
        default="./data/extracted_features",
        help="train dataset root",
    )
    parser.add_argument(
        "--dst_folder",
        type=str,
        default="models/trained/XGBoost",
        help="the path for saving trained model",
    )
    parser.add_argument(
        "--label_colname", type=str, default="target", help="the colname of the label"
    )
    parser.add_argument(
        "--test_size", type=float, default=0.2, help="the ratio for the test data"
    )
    parser.add_argument("--num_rounds", type=int, default=100, help="the train rounds")
    parser.add_argument("--random_state", type=int, default=42, help="learning rate")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    opts = parse_opt()

    train_xgboost(**vars(opts))
