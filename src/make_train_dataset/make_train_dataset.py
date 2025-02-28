import cv2
import os
from src.data_preprocessing.sam_video import SamVideo
from src.utils.load_video import extract_frames
from src.data_preprocessing.choose_points import VideoPointSelector


class MakeDataSet:
    def __init__(
        self,
        save_folder: str,
        show_photo: bool,
        **kwargs,
    ):
        self.save_folder = save_folder
        self.show_photo = show_photo

        self.sam = SamVideo(
            model_type=kwargs["sam_model_type"],
            model_device=kwargs["sam_model_device"],
            checkpoint=kwargs["sam_checkpoint"],
        )

    def make_dataset(self):
        while True:
            video_file_path, is_debrisflow, data_type, ok = self.get_info()
            if not ok:
                return
            self.make_dataset_from_video(
                video_file_path,
                is_debrisflow,
                data_type,
            )

    def make_dataset_from_video(
        self,
        video_file_path: str,
        is_debrisflow: bool,
        data_type: str,
    ):
        cap = cv2.VideoCapture(video_file_path)
        while True:
            frame_idx, slice_windows_size, extract_freq, ok = (
                self.prompt_for_new_params()
            )
            if not ok:
                cap.release()
                return
            start_frame_idx = frame_idx - (slice_windows_size - 1) * extract_freq
            ok = self.check_extract_info(cap, start_frame_idx, frame_idx)
            if not ok:
                cap.release()
                return
            feedback = self.get_user_feedback()
            if feedback == "s":
                break
            elif feedback == "n":
                continue
            elif feedback == "y":
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

    def get_info(self):
        video_file_path = input("请输入视频文件路径（终止程序输入stop）：")
        if video_file_path == "stop":
            return None, None, None, False
        is_debrisflow = int(
            input("请输入你想提取泥石流还是非泥石流（1: 泥石流 / 0: 非泥石流）：")
        )
        data_type = input("请输入数据集类型（train / val）：")
        return (
            video_file_path,
            is_debrisflow,
            data_type,
            True,
        )

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
        if self.show_photo:
            self._show_photo(cap, start_frame_idx, end_frame_idx)
        return True

    def _show_photo(
        self, cap: cv2.VideoCapture, start_frame_idx: int, end_frame_idx: int
    ):
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_idx)
        ret, start_image = cap.read()
        if ret:
            cv2.imshow(f"Start Frame Idx: {start_frame_idx}", start_image)

        cap.set(cv2.CAP_PROP_POS_FRAMES, end_frame_idx)
        ret, end_image = cap.read()
        if ret:
            cv2.imshow(f"End Frame Idx: {end_frame_idx}", end_image)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_user_feedback(self):
        while True:
            feedback = input("是否进行提取 (是:y /否: n /终止: s):")
            if feedback in ["y", "n", "s"]:
                return feedback
            else:
                print("无效输入，请输入 'y' 或 'n' 或 's'")

    def prompt_for_new_params(self) -> tuple[int, int, int, bool]:
        try:
            flag = input("是否继续对此视频提取数据集？（是:y, 否:n）")
            if flag == "n":
                return None, None, None, False
            frame_idx = int(input("请输入的 frame_idx: "))
            slice_windows_size = int(
                input("请输入 slice_windows_size (不改变直接回车): ")
            )
            extract_freq = int(input("请输入 extract_freq (不改变直接回车): "))
            print(
                f"参数：frame_idx={frame_idx}, slice_windows_size={slice_windows_size}, extract_freq={extract_freq}"
            )
            return frame_idx, slice_windows_size, extract_freq, True
        except ValueError:
            print("输入无效，请确保输入的是整数。")
            self.prompt_for_new_params()

    def save_dataset(
        self,
        cap: cv2.VideoCapture,
        video_file_path: str,
        is_debrisflow: bool,
        data_type: str,
        frame_idx: int,
        slice_windows_size: int,
        extract_freq: int,
        start_frame_idx: int,
    ):
        base_name = os.path.splitext(os.path.basename(video_file_path))[0]
        saved_base_name = f"{base_name}_FrameIdx{frame_idx}_SliceWindowsSize{slice_windows_size}_ExtractFreq_{extract_freq}_{data_type}_{is_debrisflow}"
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
            f"{data_type}",
            f"{is_debrisflow}",
            f"{saved_base_name}.jpg",
        )
        video_fps, _, img_shape = extract_frames(video_file_path)
        self.save_raw_video(
            cap,
            raw_video_file_path,
            video_fps,
            img_shape,
            start_frame_idx,
            frame_idx,
        )
        self.save_samed_video(raw_video_file_path, samed_video_file_path, extract_freq)
        self.save_img(samed_video_file_path, img_file_path)

    def save_raw_video(
        self,
        cap: cv2.VideoCapture,
        save_file_path: str,
        video_fps: int,
        img_shape: tuple[int, int],
        start_frame_idx: int,
        end_frame_idx: int,
    ):
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
