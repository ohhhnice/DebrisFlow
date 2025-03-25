import cv2

class VideoPointSelector:
    def __init__(self, video_path, frame_num=0):
        self.video_path = video_path
        self.frame_num = frame_num
        self.selected_points = []  # 存储多个点
        self.current_frame = None  # 保存当前帧用于重绘

    def click_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.selected_points.append([x, y])  # 添加新点
            print(f"Selected point: {[x, y]}, Total: {len(self.selected_points)}")
            
            # 在帧副本上绘制所有点
            display_frame = self.current_frame.copy()
            for point in self.selected_points:
                cv2.circle(display_frame, tuple(point), 5, (0, 255, 0), -1)
            cv2.imshow("Video Frame", display_frame)

    def get_selected_point(self):
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_num)
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return []
        
        self.current_frame = frame.copy()
        window_name = "Video Frame"
        cv2.imshow(window_name, frame)
        cv2.setMouseCallback(window_name, self.click_event)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # 按q键结束选点
                break

        cap.release()
        cv2.destroyAllWindows()
        return self.selected_points
    

if __name__=="__main__":
    video_path = "./data/sam/raw/田家沟_20230718T173504Z_20230718T174350Z.mp4"
    points = VideoPointSelector(video_path).get_selected_point()
    print(points)