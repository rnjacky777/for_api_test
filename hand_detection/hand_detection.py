from typing import List, Tuple, Union
from mediapipe.python.solutions import hands
from cv2.typing import MatLike
import mediapipe as mp
import configparser
import math
import cv2



class HandDetection():
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands
    img: MatLike = None
    cam = None

    def __init__(self) -> None:

        # Get config
        config = configparser.ConfigParser()
        config.read('./config.ini')
        default = config['default']

        # Set cam default setting
        self.cam = cv2.VideoCapture(int(default['cam']), cv2.CAP_DSHOW)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, int(default['cam_w']))
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, int(default['cam_h']))
        self.cam.set(cv2.CAP_PROP_FPS, 30)

    # region calculator
    def vector_2d_angle(self, v1, v2):  # 計算手指座標夾角
        v1_x = v1[0]
        v1_y = v1[1]
        v2_x = v2[0]
        v2_y = v2[1]
        try:
            angle_ = math.degrees(math.acos(
                (v1_x*v2_x+v1_y*v2_y)/(((v1_x**2+v1_y**2)**0.5)*((v2_x**2+v2_y**2)**0.5))))
        except:
            angle_ = 180
        return angle_

    def hand_angle(self, hand_):  # 計算手指角度
        angle_list = []
        # thumb 大拇指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0]) - int(hand_[2][0])),
             (int(hand_[0][1])-int(hand_[2][1]))),
            ((int(hand_[3][0]) - int(hand_[4][0])),
             (int(hand_[3][1]) - int(hand_[4][1])))
        )
        angle_list.append(angle_)
        # index 食指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])-int(hand_[6][0])),
             (int(hand_[0][1]) - int(hand_[6][1]))),
            ((int(hand_[7][0]) - int(hand_[8][0])),
             (int(hand_[7][1]) - int(hand_[8][1])))
        )
        angle_list.append(angle_)
        # middle 中指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0]) - int(hand_[10][0])),
             (int(hand_[0][1]) - int(hand_[10][1]))),
            ((int(hand_[11][0]) - int(hand_[12][0])),
             (int(hand_[11][1]) - int(hand_[12][1])))
        )
        angle_list.append(angle_)
        # ring 無名指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0]) - int(hand_[14][0])),
             (int(hand_[0][1]) - int(hand_[14][1]))),
            ((int(hand_[15][0]) - int(hand_[16][0])),
             (int(hand_[15][1]) - int(hand_[16][1])))
        )
        angle_list.append(angle_)
        # pink 小拇指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0]) - int(hand_[18][0])),
             (int(hand_[0][1]) - int(hand_[18][1]))),
            ((int(hand_[19][0]) - int(hand_[20][0])),
             (int(hand_[19][1]) - int(hand_[20][1])))
        )
        angle_list.append(angle_)
        return angle_list

    def get_finger_angle(self, hand_landmarks) -> tuple[List, int, int]:
        finger_points = []
        for i in hand_landmarks:  # 將 21 個節點換算成座標，記錄到 finger_points
            x = i.x*540
            y = i.y*310
            finger_points.append((x, y))
        if finger_points:
            finger_angle = self.hand_angle(finger_points)
        return finger_angle

    def _normalized_to_pixel_coordinates(self,
                                         normalized_x: float, normalized_y: float, image_width: int,
                                         image_height: int) -> Union[None, Tuple[int, int]]:

        # Checks if the float value is between 0 and 1.
        def is_valid_normalized_value(value: float) -> bool:
            return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                                              math.isclose(1, value))

        if not (is_valid_normalized_value(normalized_x) and
                is_valid_normalized_value(normalized_y)):
            # TODO: Draw coordinates even if it's outside of the image bounds.
            return None
        x_px = min(math.floor(normalized_x * image_width), image_width - 1)
        y_px = min(math.floor(normalized_y * image_height), image_height - 1)
        return x_px, y_px
    # endregion

    # region main process
    def hand_pos(self, finger_angle, output_pos,hand_type):  # 判斷手勢與功能
        f1 = finger_angle[0]  # 大拇指角度
        f2 = finger_angle[1]  # 食指角度
        f3 = finger_angle[2]  # 中指角度
        f4 = finger_angle[3]  # 無名指角度
        f5 = finger_angle[4]  # 小拇指角度
        # 手指角度 <50:伸直 >=50:捲縮
        if f1 < 50 and f2 < 50 and f3 < 50 and f4 < 50 and f5 < 50:  # 5
            cv2.putText(img=self.img, text=hand_type+" True", org=output_pos, fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=3,
                        color=(255, 0, 255), thickness=3, lineType=cv2.LINE_4)
        elif f1 >= 50 and f2 >= 50 and f3 >= 50 and f4 >= 50 and f5 >= 50:  # 0
            cv2.putText(img=self.img, text=hand_type+" False", org=output_pos, fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=3,
                        color=(255, 0, 255), thickness=3, lineType=cv2.LINE_4)
        else:
            cv2.putText(img=self.img, text=hand_type+" Don't care", org=output_pos, fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=3,
                        color=(255, 0, 255), thickness=3, lineType=cv2.LINE_4)

    def hand_draw(self, img, hand_landmarks):  # 繪製出手部模型
        self.mp_drawing.draw_landmarks(
            img,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style())

    def process_image(self, process_method: hands.Hands):
        ret1, img = self.cam.read()
        # 水平翻轉
        self.img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        if not ret1:
            raise ValueError("Cannot receive frame")
        return process_method.process(imgRGB)

    def get_output_pos(self, hand_landmarks) -> Union[None, Tuple[int, int]]:
        x = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST].x
        y = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST].y
        image_rows, image_cols, _ = self.img.shape
        return self._normalized_to_pixel_coordinates(x, y, image_cols, image_rows)

    def run(self):
        with self.mp_hands.Hands(
                model_complexity=0,
                min_detection_confidence=0.5,
                max_num_hands=8,
                min_tracking_confidence=0.5) as hands:
            if not self.cam.isOpened():
                print("Cannot open camera")
                exit()
            while True:
                results = self.process_image(hands)
                if results.multi_hand_landmarks:
                    for hand_landmarks,handedness in zip(results.multi_hand_landmarks,results.multi_handedness):
                        # 檢查左右手
                        hand_type = handedness.classification[0].label
                        self.hand_draw(img=self.img, hand_landmarks=hand_landmarks,)
                        output_text_pos = self.get_output_pos(hand_landmarks)
                        finger_angle = self.get_finger_angle(hand_landmarks.landmark)
                        self.hand_pos(finger_angle=finger_angle, output_pos=output_text_pos,hand_type=hand_type)
                cv2.imshow('My Image', self.img)
                if cv2.waitKey(5) == ord('q'):
                    break
        self.cam.release()
        cv2.destroyAllWindows()
    # endregion

if __name__ == '__main__':
    main = HandDetection()
    main.run()
