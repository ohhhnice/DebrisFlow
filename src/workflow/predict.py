from src.data_preprocessing.sam_video import SamVideo
from src.extract_features.extract_features import ExtractFeatures
from src.XGBoost.predict import xgb_predict


class DebrisFlowPredict:
    def __init__(
        self,
        video_name: str,
        src_folder: str,
        samed_video_folder: str,
        features_folder: str,
        output_folder: str,
        slice_windows_size: int,
        XGB_model_path: str,
        point_coordinates: list[int],
        extract_freq: int,
        vgg_model_weights_path: str,
        feature_size: int,
        device: str,
        **kwargs,
    ):
        self.src_folder = src_folder
        self.video_name = video_name
        self.samed_video_folder = samed_video_folder
        self.features_folder = features_folder
        self.output_folder = output_folder
        self.slice_windows_size = slice_windows_size
        self.XGB_model_path = XGB_model_path
        self.point_coordinates = point_coordinates
        self.extract_freq = extract_freq
        self.vgg_model_weights_path = vgg_model_weights_path
        self.feature_size = feature_size
        self.device = device

        self.sam = SamVideo(
            model_type=kwargs["sam_model_type"],
            model_device=kwargs["sam_model_device"],
            checkpoint=kwargs["sam_checkpoint"],
        )

    def predict_video(self):
        samed_video_name = self.sam.predict_video(
            self.video_name,
            self.src_folder,
            self.samed_video_folder,
            self.extract_freq,
            self.point_coordinates,
        )
        extract_features = ExtractFeatures(
            samed_video_name,
            self.samed_video_folder,
            self.features_folder,
            self.vgg_model_weights_path,
            self.feature_size,
            self.device,
            self.slice_windows_size,
        )
        features_file_name = extract_features.extract_video_features()
        xgb_predict(
            features_file_name,
            self.features_folder,
            self.XGB_model_path,
            self.output_folder,
        )

    def predict_frame(self, frame_idx: int):
        samed_video_name = self.sam.predict_frame(
            self.video_name,
            self.src_folder,
            self.samed_video_folder,
            frame_idx,
            self.slice_windows_size,
            self.point_coordinates,
        )
        extract_features = ExtractFeatures(
            samed_video_name,
            self.samed_video_folder,
            self.features_folder,
            self.vgg_model_weights_path,
            self.feature_size,
            self.device,
            self.slice_windows_size,
        )
        features_file_name = extract_features.extract_video_features()
        xgb_predict(
            features_file_name,
            self.features_folder,
            self.XGB_model_path,
            self.output_folder,
        )
