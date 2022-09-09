import cv2
import time
import enum
from pyautogui import size
from pynput.mouse import Controller, Button
from mediapipe.python.solutions import hands as mp_hands, drawing_styles, drawing_utils

class Mode(enum.Enum):
    POINTER_MODE = 'point'
    LEFT_CLICK_MODE = 'left click'
    RIGHT_CLICK_MODE = 'right click'
    SCROLLING_MODE = 'scroll'

MODE = None
scr_w, scr_h = size()
cam_w, cam_h = 640, 480

ptime = 0
curr_mouse_x, curr_mouse_y = 0, 0
prev_mouse_x, prev_mouse_y = 0, 0
smoothening = 3.5

cv2.namedWindow('main', cv2.WINDOW_NORMAL)
cv2.resizeWindow('main', cam_w, cam_h)

cap = cv2.VideoCapture(0)
cap.set(3, cam_w)
cap.set(4, cam_h)

hands = mp_hands.Hands(max_num_hands = 1)
mouse = Controller()

while True:
    ret, frame = cap.read()

    frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    ctime = time.time()
    fps = int(1/(ctime-ptime))
    ptime = ctime

    frame_RGB.flags.writeable = False
    results = hands.process(frame_RGB)

    frame_RGB.flags.writeable = True
    frame_BGR = cv2.cvtColor(frame_RGB, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            index_tip = landmarks.landmark[8]
            index_pip = landmarks.landmark[6]
            middle_tip = landmarks.landmark[12]
            middle_pip = landmarks.landmark[10]
            ring_tip = landmarks.landmark[16]
            ring_pip = landmarks.landmark[14]
            thumb_tip = landmarks.landmark[4]
            thumb_ip = landmarks.landmark[3]

            if index_tip.y < index_pip.y and ring_tip.y < ring_pip.y and middle_tip.y < middle_pip.y and thumb_tip.x < thumb_ip.x - 0.007:
                MODE = Mode.SCROLLING_MODE
            elif index_tip.y < index_pip.y and ring_tip.y >= ring_pip.y and middle_tip.y >= middle_pip.y and thumb_tip.x < thumb_ip.x - 0.007:
                MODE = Mode.POINTER_MODE
            elif index_tip.y < index_pip.y and ring_tip.y >= ring_pip.y and middle_tip.y < middle_pip.y and thumb_tip.x < thumb_ip.x - 0.007:
                MODE = Mode.LEFT_CLICK_MODE
            elif index_tip.y < index_pip.y and ring_tip.y >= ring_pip.y and middle_tip.y >= middle_pip.y and thumb_tip.x >= thumb_ip.x- 0.007:
                MODE = Mode.RIGHT_CLICK_MODE
            else:
                MODE = None

            h, w, c = frame_BGR.shape
            if MODE == Mode.POINTER_MODE:
                cv2.circle(frame_BGR, (int(index_tip.x * w), int(index_tip.y * h)), 10, (100, 0, 255), cv2.FILLED)

                x_cursor = (scr_w/2 - scr_w * index_tip.x)**(40/31)
                if type(x_cursor) == complex:
                    x_cursor = 0
                elif x_cursor > scr_w:
                    x_cursor = scr_w - 10
                y_cursor = scr_h - (scr_h/2 - scr_h * index_tip.y)**(40/31)
                if type(y_cursor) == complex:
                    y_cursor = scr_h - 10

                ## smoothening
                curr_mouse_x = prev_mouse_x + (x_cursor - prev_mouse_x)/smoothening 
                curr_mouse_y = prev_mouse_y + (y_cursor - prev_mouse_y)/smoothening 

                mouse.position = curr_mouse_x, curr_mouse_y
                prev_mouse_x, prev_mouse_y = curr_mouse_x, curr_mouse_y

            if MODE == Mode.LEFT_CLICK_MODE:
                x_index, y_index = int(index_tip.x * w), int(index_tip.y * h)
                x_middle, y_middle = int(middle_tip.x * w), int(middle_tip.y * h)
                cv2.circle(frame_BGR, (x_index, y_index), 10, (100, 0, 255), cv2.FILLED)
                cv2.circle(frame_BGR, (x_middle, y_middle), 10, (100, 0, 255), cv2.FILLED)
                cv2.line(frame_BGR, (x_index, y_index), (x_middle, y_middle), (100, 0, 255), 3)
                cv2.circle(frame_BGR, ((x_index + x_middle)//2, (y_index + y_middle)//2), 10, (100, 0, 255), cv2.FILLED)
                print(x_index - x_middle)
                if x_index - x_middle < 20:
                    cv2.circle(frame_BGR, ((x_index + x_middle)//2, (y_index + y_middle)//2), 10, (0, 255, 0), cv2.FILLED)
                    mouse.click(Button.left)

            if MODE == Mode.RIGHT_CLICK_MODE:
                x_index, y_index = int(index_tip.x * w), int(index_tip.y * h)
                x_thumb, y_thumb = int(thumb_tip.x * w), int(thumb_tip.y * h)
                cv2.circle(frame_BGR, (x_index, y_index), 10, (100, 0, 255), cv2.FILLED)
                cv2.circle(frame_BGR, (x_thumb, y_thumb), 10, (100, 0, 255), cv2.FILLED)
                cv2.line(frame_BGR, (x_index, y_index), (x_thumb, y_thumb), (100, 0, 255), 3)
                cv2.circle(frame_BGR, ((x_index + x_thumb)//2, (y_index + y_thumb)//2), 10, (100, 0, 255), cv2.FILLED)
                print(x_thumb - x_index, y_thumb - y_index)
                if  x_thumb - x_index < 14 and y_thumb - y_index < 14:
                    cv2.circle(frame_BGR, ((x_index + x_thumb)//2, (y_index + y_thumb)//2), 10, (0, 255, 0), cv2.FILLED)
                    mouse.click(Button.right)


            drawing_utils.draw_landmarks(
                frame_BGR,
                landmarks,
                mp_hands.HAND_CONNECTIONS,
                drawing_styles.get_default_hand_landmarks_style(),
                drawing_styles.get_default_hand_connections_style()
            )

    flipped_frame = cv2.flip(frame_BGR, 1)
    cv2.putText(flipped_frame, str(fps), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow('main', flipped_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()