import cv2
import base64


class FrameProcessor:
    """视频帧处理工具类，用于提取帧图像和兴趣点选择"""

    @staticmethod
    def get_frame(video_path, frame_idx):
        """获取指定索引的帧图像"""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 如果帧索引超出范围，则取最后一帧
        if frame_idx >= total_frames:
            frame_idx = total_frames - 1

        # 设置帧位置
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return None

        return frame

    @staticmethod
    def get_range_frames(video_path, center_idx, window_size, extract_freq):
        """获取指定范围内的起始帧和结束帧"""
        # 计算开始和结束的帧索引
        start_idx = max(0, center_idx - window_size + 1)
        end_idx = center_idx

        # 获取起始帧和结束帧
        start_frame = FrameProcessor.get_frame(video_path, start_idx)
        end_frame = FrameProcessor.get_frame(video_path, end_idx)

        return {
            "start_idx": start_idx,
            "end_idx": end_idx,
            "start_frame": FrameProcessor.encode_frame(start_frame),
            "end_frame": FrameProcessor.encode_frame(end_frame),
        }

    @staticmethod
    def encode_frame(frame):
        """将帧图像编码为Base64格式"""
        if frame is None:
            return None

        # 将BGR转为RGB
        # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 编码为JPEG格式
        _, buffer = cv2.imencode(".jpg", frame)

        # 转换为Base64字符串
        return base64.b64encode(buffer).decode("utf-8")

    @staticmethod
    def draw_point(frame, coordinates, radius=5, color=(0, 0, 255)):
        """在帧上绘制兴趣点"""
        if frame is None or coordinates is None:
            return None

        # 创建副本以避免修改原始帧
        frame_copy = frame.copy()

        # 绘制点
        cv2.circle(frame_copy, tuple(coordinates), radius, color, -1)

        return frame_copy

    @staticmethod
    def compute_coordinates_from_relative(rel_x, rel_y, frame_width, frame_height):
        """从相对坐标计算绝对坐标"""
        x = int(rel_x * frame_width)
        y = int(rel_y * frame_height)
        return [x, y]

    @staticmethod
    def encode_frame_with_point(frame, coordinates, radius=5, color=(0, 0, 255)):
        """在帧上绘制兴趣点并编码为Base64格式"""
        if frame is None:
            return None

        if coordinates and len(coordinates) == 2:
            # 创建副本以避免修改原始帧
            frame_with_point = frame.copy()

            # 绘制点
            cv2.circle(frame_with_point, tuple(coordinates), radius, color, -1)

            # 编码为Base64
            return FrameProcessor.encode_frame(frame_with_point)

        # 如果没有坐标，直接编码原始帧
        return FrameProcessor.encode_frame(frame)
