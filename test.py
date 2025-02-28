from src.utils.load_video import extract_frames

video_path = "data/dataset/samed_video/田家沟_20230718T173504Z_20230718T174350Z_FrameIdx300_SliceWindowsSize10_ExtractFreq_2_val_1.mp4"  # 替换为你的视频路径
fps, frameCount, frame_shape = extract_frames(video_path)
print(fps, frameCount, frame_shape)
