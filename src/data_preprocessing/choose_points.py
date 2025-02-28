import cv2


class VideoPointSelector:
    def __init__(self, video_path, frame_num=0):
        self.video_path = video_path
        self.frame_num = frame_num
        self.selected_point = None

    def click_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.selected_point = (x, y)
            print(f"Selected point: {self.selected_point}")
            cv2.circle(param, (x, y), 5, (0, 255, 0), -1)  # 在点击位置画个绿色圆圈
            cv2.imshow("Video Frame", param)

    def get_selected_point(self):
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_num)
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return None

        windows_name = "set point"
        cv2.imshow(windows_name, frame)
        cv2.setMouseCallback(windows_name, self.click_event, param=frame)

        while self.selected_point is None:
            cv2.waitKey(1000)

        cap.release()
        cv2.destroyAllWindows()
        return self.selected_point
