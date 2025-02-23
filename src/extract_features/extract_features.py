import numpy as np


class ExtractFeatures:
    def __init__(self):
        pass

    def extract_vgg_features(self, img_array):
        pass

    def calculate_grey_variance(self, img_list: list[np.array]):
        pass

    def extract_frame_features(self, img_array_list: np.array) -> np.array:
        pass

    def get_array_list(
        self,
        src_folder: str,
        video_name: str,
        frame_idx: int,
        slice_windows_size: int,
    ) -> list[np.array]:
        pass

    def extract_all_features(
        self,
        src_folder_path: str,
        dst_folder_path: str,
        video_name: str,
        slice_windows_size: int = 30,
    ):
        pass
