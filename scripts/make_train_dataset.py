import sys
from pathlib import Path
from argparse import ArgumentParser

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "external_project"))

from src.make_train_dataset.make_train_dataset import MakeDataSet


quick_dataset = MakeDataSet(
    save_folder="data/dataset",
    video_file_path="data/sam/raw/田家沟_20230718T173504Z_20230718T174350Z.mp4",
    is_debrisflow=True,
    data_type="train",
    frame_idx=10000,
    slice_windows_size=10,
    extract_freq=1,
    point_coordinates=[[800, 700]],
    sam_video_sign=True,
    sam_model_type="vit_h",
    sam_model_device="cpu",
    sam_checkpoint="models/pretrained/sam/sam_vit_h_4b8939.pth",
)
quick_dataset.make_dataset()
