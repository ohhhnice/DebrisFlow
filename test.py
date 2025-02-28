from src.data_preprocessing.choose_points import VideoPointSelector

video_path = "data/sam/raw/3.mp4"  # 替换为你的视频路径
selector = VideoPointSelector(video_path)
point = selector.get_selected_point()
print(f"Final selected point: {point}")
