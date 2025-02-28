import sys
from pathlib import Path
from argparse import ArgumentParser

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.utils.plot_line import plot_line_chart_from_csv


def parse_opt():
    parser = ArgumentParser()
    parser.add_argument(
        "--csv_file_path",
        type=str,
        default="data/output/田家沟_20230718T173504Z_20230718T174350Z.csv",
        help="the path of the csv file",
    )
    parser.add_argument(
        "--field_name",
        type=str,
        default="prediction",
        help="the column name for the line",
    )
    parser.add_argument(
        "--save_folder",
        type=str,
        default="data/plot/line_chart",
        help="the folder for saving the line chart",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    opts = parse_opt()

    plot_line_chart_from_csv(**vars(opts))
