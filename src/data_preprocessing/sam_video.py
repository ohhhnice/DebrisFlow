import os
import cv2
from tqdm import tqdm
import numpy as np

from src.utils.load_video import extract_frames
from external_project.segment_anything import SamPredictor, sam_model_registry
from src.data_preprocessing.choose_points import VideoPointSelector


class SamVideo:
    def __init__(
        self,
        model_type: str,
        model_device: str,
        checkpoint: any,
    ):
        self.checkpoint = checkpoint
        self.model_type = model_type
        self.model_device = model_device
        self.loadModel()

    def predict_frame(
        self,
        video_name: str,
        src_folder: str,
        dst_folder: str,
        frame_idx: int,
        slice_windows_size: int,
        point_coordinates: tuple[int, int] = None,
    ) -> str:
        src_path = os.path.join(src_folder, video_name)
        video_fps, video_frame_count, img_shape = extract_frames(src_path)
        start_idx = frame_idx - slice_windows_size + 1
        if start_idx < 0 or frame_idx >= video_frame_count:
            print("报错，帧数范围错误！")
            return

        os.makedirs(dst_folder, exist_ok=True)
        base_name, ext = os.path.splitext(video_name)
        save_video_name = "{}_frame{:>03d}{}".format(base_name, frame_idx, ext)
        save_path = os.path.join(dst_folder, save_video_name)

        if point_coordinates is None:
            point_coordinates = VideoPointSelector(src_path).get_selected_point()

        cap = cv2.VideoCapture(src_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_idx)
        fourcc = cv2.VideoWriter.fourcc(*"mp4v")
        out = cv2.VideoWriter(save_path, fourcc, video_fps, img_shape)

        print("=" * 30 + " SAM VIDEO " + "=" * 30 + "\n")
        for frameIdx in tqdm(
            range(slice_windows_size), desc="Writing frames(SAM)", unit="frame"
        ):
            ret, frame = cap.read()
            if not ret:
                break
            output_frame = self._get_masked_photo(frame, point_coordinates)
            out.write(output_frame)
        out.release()
        cap.release()
        return save_video_name

    def predict_video(
        self,
        video_name: str,
        src_folder: str,
        dst_folder: str,
        extract_freq: int = 1,
        point_coordinates: tuple[int, int] = None,
    ) -> str:
        os.makedirs(dst_folder, exist_ok=True)
        src_path = os.path.join(src_folder, video_name)
        save_path = os.path.join(dst_folder, video_name)
        video_fps, video_frame_count, img_shape = extract_frames(src_path)

        cap = cv2.VideoCapture(src_path)
        fourcc = cv2.VideoWriter.fourcc(*"mp4v")
        out = cv2.VideoWriter(save_path, fourcc, video_fps, img_shape)

        if point_coordinates is None:
            point_coordinates = VideoPointSelector(src_path).get_selected_point()

        print("=" * 30 + " SAM VIDEO " + "=" * 30 + "\n")
        for frameIdx in tqdm(
            range(video_frame_count), desc="Writing frames(SAM)", unit="frame"
        ):
            ret, frame = cap.read()
            if not ret:
                break
            if frameIdx % extract_freq != 0:
                continue
            output_frame = self._get_masked_photo(frame, point_coordinates)
            out.write(output_frame)
        out.release()
        cap.release()
        return video_name

    def loadModel(self):
        model = sam_model_registry[self.model_type](checkpoint=self.checkpoint)
        model.to(device=self.model_device)
        self.predictor = SamPredictor(model)

    def _get_masked_photo(
        self,
        image: np.ndarray,
        point_coordinates: list[int],
    ) -> np.array:
        self.predictor.set_image(image)
        points = np.array([point_coordinates])  # 传设置预标记点
        masks, scores, _ = self.predictor.predict(  # 使用SAM_predictor返回覆盖、置信度
            point_coords=points,
            point_labels=np.array(
                [1]
            ),  # 设置label（需要预测的主体一般设置为1，背景一般设置为0）
            multimask_output=True,
        )
        idx = np.argmax(scores)
        masked_arr = masks[idx]
        return masked_arr[..., np.newaxis] * image
