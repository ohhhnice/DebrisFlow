import cv2
from src.data_preprocessing.sam_video import SamVideo
from src.utils.load_video import extract_frames
from src.data_preprocessing.choose_points import VideoPointSelector
from .make_train_dataset import MakeDataSet


class QuickMakeDataSet(MakeDataSet):
    def __init__(
        self,
        save_folder: str,
        show_photo: bool,
        video_file_path: str,
        is_debrisflow: bool,
        data_type: str,
        frame_idx: int,
        slice_windows_size: int = 75,
        extract_freq: int = 1,
        point_coordinates=None,
        **kwargs,
    ):
        super().__init__(save_folder, show_photo, **kwargs)
        self.video_file_path = video_file_path
        self.is_debrisflow = is_debrisflow
        self.data_type = data_type
        self.frame_idx = frame_idx
        self.slice_windows_size = slice_windows_size
        self.extract_freq = extract_freq
        self.point_coordinates = point_coordinates

    def make_dataset(self):
        """
        快速制作数据集，使用预设的参数而不是交互式输入
        """
        self.make_dataset_from_video(
            self.video_file_path,
            self.is_debrisflow,
            self.data_type,
        )

    def make_dataset_from_video(
        self,
        video_file_path: str,
        is_debrisflow: bool,
        data_type: str,
    ):
        cap = cv2.VideoCapture(video_file_path)
        frame_idx = self.frame_idx
        slice_windows_size = self.slice_windows_size
        extract_freq = self.extract_freq
        
        start_frame_idx = frame_idx - (slice_windows_size - 1) * extract_freq
        ok = self.check_extract_info(cap, start_frame_idx, frame_idx)
        if not ok:
            cap.release()
            return

        self.save_dataset(
            cap,
            video_file_path,
            is_debrisflow,
            data_type,
            frame_idx,
            slice_windows_size,
            extract_freq,
            start_frame_idx,
        )
        cap.release()

    def prompt_for_new_params(self) -> tuple[int, int, int, bool]:
        """
        覆盖父类的方法，直接返回预设的参数
        """
        return self.frame_idx, self.slice_windows_size, self.extract_freq, True

    def get_info(self):
        """
        覆盖父类的方法，直接返回预设的参数
        """
        return self.video_file_path, self.is_debrisflow, self.data_type, True

    def get_user_feedback(self):
        """
        覆盖父类的方法，直接返回 'y' 表示确认处理
        """
        return 'y'
