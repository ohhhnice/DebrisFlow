import cv2
import os
from src.data_preprocessing.sam_video import SamVideo
from src.utils.load_video import extract_frames
from src.data_preprocessing.choose_points import VideoPointSelector


class MakeDataSet:
    def __init__(
        self,
        video_file_path: str,
        is_debrisflow: int,
        data_type: str,
        frame_idx: int,
        slice_windows_size: int,
        save_folder: str,
        show_photo: bool,
        **kwargs,
    ):
        self.video_file_path = video_file_path
        self.is_debrisflow = is_debrisflow
        self.data_type = data_type
        self.frame_idx = frame_idx
        self.slice_windows_size = slice_windows_size
        self.save_folder = save_folder
        self.show_photo = show_photo

        self.start_frame = self.frame_idx - self.slice_windows_size + 1
        self.sam = SamVideo(
            model_type=kwargs["sam_model_type"],
            model_device=kwargs["sam_model_device"],
            checkpoint=kwargs["sam_checkpoint"],
        )

    def make_dataset(
        self, extract_freq: int = 1, point_coordinates: tuple[int, int] = None
    ):
        cap = cv2.VideoCapture(self.video_file_path)
        ok = self.check_extract_info(cap)
        if not ok:
            cap.release()
            return
        self.save_dataset(cap, extract_freq, point_coordinates)
        cap.release()

    def check_extract_info(self, cap: cv2.VideoCapture) -> bool:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        while True:
            start_frame = self.frame_idx - self.slice_windows_size + 1
            if start_frame < 0 or self.frame_idx >= total_frames:
                print(
                    f"警告：提取的范围无效，视频帧数范围为 0 到 {total_frames - 1}, 你的提取范围是 {start_frame} 到 {self.frame_idx}"
                )
                ok = False
                break

            if self.show_photo:
                self._show_photo(cap, start_frame, self.frame_idx)

            feedback = self.get_user_feedback()  # 是/否/终止

            if feedback == "否":
                self.reset_extract_info(self.frame_idx, self.slice_windows_size)
                print("请重新设置参数...")
                self.prompt_for_new_params()
            else:
                ok = feedback != "终止"
                break
        self.start_frame = start_frame
        return ok

    def _show_photo(self, cap: cv2.VideoCapture, start_frame: int, end_frame: int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        ret, start_image = cap.read()
        if ret:
            cv2.imshow(f"Start Frame: {start_frame}", start_image)

        cap.set(cv2.CAP_PROP_POS_FRAMES, end_frame)
        ret, end_image = cap.read()
        if ret:
            cv2.imshow(f"End Frame: {end_frame}", end_image)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_user_feedback(self):
        while True:
            feedback = input("是否进行提取（是/否/终止）：")
            if feedback in ["是", "否", "终止"]:
                return feedback
            else:
                print("无效输入，请输入 '是' 或 '否' 或 '终止'")

    def reset_extract_info(self, frame_idx: int, slice_windows_size: int = None):
        if slice_windows_size is not None:
            self.slice_windows_size = slice_windows_size
        self.frame_idx = frame_idx
        print(
            f"参数已重置：frame_idx={self.frame_idx}, slice_windows_size={self.slice_windows_size}"
        )

    def prompt_for_new_params(self):
        try:
            self.frame_idx = int(input("请输入新的 frame_idx: "))
            input_slice_windows_size = input(
                "请输入新的 slice_windows_size(不改变直接回车): "
            )
            if input_slice_windows_size:
                self.slice_windows_size = int(input_slice_windows_size)
            print(
                f"新参数：frame_idx={self.frame_idx}, slice_windows_size={self.slice_windows_size}"
            )
        except ValueError:
            print("输入无效，请确保输入的是整数。")
            self.prompt_for_new_params()

    def save_dataset(
        self,
        cap: cv2.VideoCapture,
        extract_freq: int = 1,
        point_coordinates: tuple[int, int] = None,
    ):
        base_name = os.path.splitext(os.path.basename(self.video_file_path))[0]
        saved_base_name = f"{base_name}_FrameIdx{self.frame_idx}_SliceWindowsSize{self.slice_windows_size}_{self.data_type}_{self.is_debrisflow}"
        raw_video_file_path = os.path.join(
            self.save_folder,
            "raw_video",
            f"{saved_base_name}.mp4",
        )
        samed_video_file_path = os.path.join(
            self.save_folder,
            "samed_video",
            f"{saved_base_name}.mp4",
        )
        img_file_path = os.path.join(
            self.save_folder,
            "photo",
            f"{self.data_type}",
            f"{self.is_debrisflow}",
            f"{saved_base_name}.jpg",
        )
        video_fps, _, img_shape = extract_frames(self.video_file_path)
        self.save_raw_video(cap, raw_video_file_path, video_fps, img_shape)
        self.save_samed_video(
            raw_video_file_path, samed_video_file_path, extract_freq, point_coordinates
        )
        self.save_img(samed_video_file_path, img_file_path)

    def save_raw_video(
        self,
        cap: cv2.VideoCapture,
        save_file_path: str,
        video_fps: int,
        img_shape: tuple[int, int],
    ):
        save_dir = os.path.dirname(save_file_path)
        os.makedirs(save_dir, exist_ok=True)

        fourcc = cv2.VideoWriter.fourcc(*"mp4v")
        out = cv2.VideoWriter(save_file_path, fourcc, video_fps, img_shape)

        cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        for i in range(self.slice_windows_size):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        out.release()

    def save_samed_video(
        self,
        src_video_path: str,
        save_file_path: str,
        extract_freq: int = 1,
        point_coordinates: tuple[int, int] = None,
    ):
        if point_coordinates is None:
            point_coordinates = VideoPointSelector(src_video_path).get_selected_point()
        self.sam.predict_video(
            os.path.basename(src_video_path),
            os.path.dirname(src_video_path),
            os.path.dirname(save_file_path),
            extract_freq,
            point_coordinates,
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
        cv2.imwrite(save_file_path, frame)
        cap.release()
