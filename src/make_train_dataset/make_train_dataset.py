import cv2
import os
from src.data_preprocessing.sam_video import SamVideo
from src.utils.load_video import extract_frames
from src.data_preprocessing.choose_points import VideoPointSelector
from PIL import Image


class MakeDataSet:
    def __init__(
        self,
        save_folder: str,
        video_file_path: str,
        is_debrisflow: bool,
        data_type: str,
        frame_idx: int,
        slice_windows_size: int = 75,
        extract_freq: int = 1,
        point_coordinates:list[list[int]]=None,
        sam_video_sign: bool = False,
        **kwargs,
    ):
        self.save_folder = save_folder
        self.video_file_path = video_file_path
        self.is_debrisflow = is_debrisflow
        self.data_type = data_type
        self.frame_idx = frame_idx
        self.slice_windows_size = slice_windows_size
        self.extract_freq = extract_freq
        self.point_coordinates = point_coordinates
        self.sam_video_sign = sam_video_sign
        if self.sam_video_sign:
            self.sam = SamVideo(
                model_type=kwargs["sam_model_type"],
                model_device=kwargs["sam_model_device"],
                checkpoint=kwargs["sam_checkpoint"],
            )

    def make_dataset(self):
        cap = cv2.VideoCapture(self.video_file_path)
        start_frame_idx = (
            self.frame_idx - (self.slice_windows_size - 1) * self.extract_freq
        )
        ok = self.check_extract_info(cap, start_frame_idx, self.frame_idx)
        if not ok:
            cap.release()
            return

        self.save_dataset(
            cap,
            start_frame_idx,
        )
        cap.release()

    def save_dataset(
        self,
        cap: cv2.VideoCapture,
        start_frame_idx: int,
    ):
        raw_video_file_path, samed_video_file_path, img_file_path = self.get_name()

        self.save_raw_video(
            cap,
            raw_video_file_path,
            start_frame_idx,
            self.frame_idx,
        )
        if self.sam_video_sign:
            self.save_samed_video(
                raw_video_file_path, samed_video_file_path, self.extract_freq
            )
            self.save_img(samed_video_file_path, img_file_path)

    def save_raw_video(
        self,
        cap: cv2.VideoCapture,
        save_file_path: str,
        start_frame_idx: int,
        end_frame_idx: int,
    ):
        video_fps, _, img_shape = extract_frames(self.video_file_path)

        save_dir = os.path.dirname(save_file_path)
        os.makedirs(save_dir, exist_ok=True)

        fourcc = cv2.VideoWriter.fourcc(*"mp4v")
        out = cv2.VideoWriter(save_file_path, fourcc, video_fps, img_shape)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_idx)
        frame_count = end_frame_idx - start_frame_idx + 1
        for i in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        out.release()

    def save_samed_video(
        self,
        src_video_path: str,
        save_file_path: str,
        extract_freq: int,
    ):
        if self.point_coordinates is None:
            self.get_selected_point(src_video_path)
        self.sam.predict_video(
            os.path.basename(src_video_path),
            os.path.dirname(src_video_path),
            os.path.dirname(save_file_path),
            extract_freq,
            self.point_coordinates,
        )

    def save_img(self, src_video_path: str, save_file_path: str):
        cap = cv2.VideoCapture(src_video_path)
        _, video_frame_count, _ = extract_frames(src_video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, video_frame_count - 1)
        ret, frame = cap.read()
        if not ret:
            return
        save_dir = os.path.dirname(save_file_path)
        os.makedirs(save_dir, exist_ok=True)
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image.save(save_file_path)
        cap.release()

    def get_selected_point(self, src_video_path: str):
        self.point_coordinates = VideoPointSelector(src_video_path).get_selected_point()

    def get_name(
        self,
    ):
        is_debrisflow = int(self.is_debrisflow)
        base_name = os.path.splitext(os.path.basename(self.video_file_path))[0]
        saved_base_name = f"{base_name}_FrameIdx{self.frame_idx}_SliceWindowsSize{self.slice_windows_size}_ExtractFreq_{self.extract_freq}_{self.data_type}_{is_debrisflow}"
        raw_video_file_path = os.path.join(
            self.save_folder,
            f"{self.data_type}",
            "raw_video",
            f"{is_debrisflow}",
            f"{saved_base_name}.mp4",
        )
        samed_video_file_path = os.path.join(
            self.save_folder,
            f"{self.data_type}",
            "samed_video",
            f"{is_debrisflow}",
            f"{saved_base_name}.mp4",
        )
        img_file_path = os.path.join(
            self.save_folder,
            f"{self.data_type}",
            "photo",
            f"{is_debrisflow}",
            f"{saved_base_name}.jpg",
        )
        return raw_video_file_path, samed_video_file_path, img_file_path

    def check_extract_info(
        self,
        cap: cv2.VideoCapture,
        start_frame_idx: int,
        end_frame_idx: int,
    ) -> bool:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if start_frame_idx < 0 or end_frame_idx >= total_frames:
            print(
                f"警告：提取的范围无效，视频帧数范围为 0 到 {total_frames - 1}, 你的提取范围是 {start_frame_idx} 到 {end_frame_idx}"
            )
            return False
        return True
