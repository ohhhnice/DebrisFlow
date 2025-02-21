

class DebrisFlowPredict():
    def __init__(self):
        pass

    def predict_video(self, video_path: str):
        pass

    def predict_frame(self, video_path: str, frame_idx: int):
        pass


if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path

    FILE = Path(__file__).resolve()
    ROOT = FILE.parents[1]
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))

    predict = DebrisFlowPredict()
