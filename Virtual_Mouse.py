from ast import arg
import cv2
import enum
import argparse
from pyautogui import size
from numpy import interp
from pynput.mouse import Controller, Button
from mediapipe.python.solutions import hands as mp_hands, drawing_styles, drawing_utils

parser = argparse.ArgumentParser()

parser.add_argument(
    '-f',
    '--fps_on',
    help = 'use this argument to enable fps',
    action = 'store_true'
)
parser.add_argument(
    '-s',
    '--smooth',
    help = 'Default smooth_value is 3.5. Providing a higher value to this argument will result in a higher delay in cursor movement but lesser shakiness, and vice - versa',
    type = float,
    metavar = '<smooth_value>'
)
parser.add_argument(
    '-v',
    '--version',
    help = "Show this software's version info",
    action = 'store_true'
)

parser.add_argument(
    '-i',
    '--inc_register_dist',
    help = '''Recommended to use this option if you are less than about 50cm away from your webcam. 
        This flag increases the minimum distance required between certain combination of fingers to 
        trigger a mouse action. You can pass this flag multiple times such as "-iii" to further its effect.''',
    action = 'count'
)

parser.add_argument(
    '-S',
    '--sensitivity',
    help = '''Change sensitivity of the virtual mouse. This will also effect the boundary within which 
        you can point your finger and move the cursor. Default value is 2''',
    type = int,
    choices = (1, 2, 3, 4)
)
parser.add_argument(
    '-c',
    '--cap_id',
    help = 'Set ID of your video capture device. Default is 0.',
    type = int
)

args = parser.parse_args()

if args.version:
    print('Version 1.1\nVirtual Mouse\nDeveloper: Mohd Anas Nadeem')
    exit(0)

if args.fps_on:
    import time

class Mode(enum.Enum):
    POINTER_MODE = 'point'
    LEFT_CLICK_MODE = 'left click'
    RIGHT_CLICK_MODE = 'right click'
    SCROLLING_MODE = 'scroll'

MODE = None
scr_w, scr_h = size()
cam_w, cam_h = int(640), int(480)

ptime = 0
curr_mouse_x, curr_mouse_y = 0, 0
prev_mouse_x, prev_mouse_y = 0, 0
smoothening = 3.5
if args.smooth:
    smoothening = args.smooth

left_click_reg_dist = 20
right_click_reg_dist = 14
scroll_reg_dist = 40
if args.inc_register_dist:
    for i in range(args.inc_register_dist):
        left_click_reg_dist += 10
        right_click_reg_dist += 10
        scroll_reg_dist += 10
reg_distances = [left_click_reg_dist, right_click_reg_dist, scroll_reg_dist]

detection_margin_left = 350
detection_margin_right = 100
detection_margin_up = 100
detection_margin_down = 200

if args.sensitivity:
    detection_margin_left += (args.sensitivity - 2) * 25
    detection_margin_right += (args.sensitivity - 2) * 25
    detection_margin_up += (args.sensitivity - 2) * 15
    detection_margin_down += (args.sensitivity - 2) * 15

cv2.namedWindow('main', cv2.WINDOW_NORMAL)
cv2.resizeWindow('main', int(cam_w * 1.5), int(cam_h * 1.5))

if args.cap_id:
    cap = cv2.VideoCapture(args.cap_id)
else:
    cap = cv2.VideoCapture(0)

cap.set(3, cam_w)
cap.set(4, cam_h)

hands = mp_hands.Hands(max_num_hands = 1)
mouse = Controller()

while True:
    if cv2.getWindowProperty('main', cv2.WND_PROP_VISIBLE) == 0:
        cv2.destroyAllWindows()
        break
    ret, frame = cap.read()

    frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

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

            h, w, c = frame_BGR.shape

            cv2.rectangle(frame_BGR, (cam_w - detection_margin_left, detection_margin_up), (detection_margin_right, cam_h - detection_margin_down), (255, 100, 100), 2)

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

            if MODE == Mode.POINTER_MODE:
                cv2.circle(frame_BGR, (int(index_tip.x * w), int(index_tip.y * h)), 10, (100, 0, 255), cv2.FILLED)

                x_cursor = interp(index_tip.x * w, (detection_margin_right, cam_w - detection_margin_left), (0, scr_w))
                if type(x_cursor) == complex:
                    x_cursor = 0
                elif x_cursor > scr_w:
                    x_cursor = scr_w - 10
                y_cursor = interp(index_tip.y * h, (detection_margin_up, cam_h - detection_margin_down), (0, scr_h))
                if type(y_cursor) == complex:
                    y_cursor = scr_h - 10

                ## smoothening
                curr_mouse_x = prev_mouse_x + (x_cursor - prev_mouse_x)/smoothening 
                curr_mouse_y = prev_mouse_y + (y_cursor - prev_mouse_y)/smoothening 

                mouse.position = scr_w - curr_mouse_x, curr_mouse_y
                prev_mouse_x, prev_mouse_y = curr_mouse_x, curr_mouse_y

            if MODE == Mode.LEFT_CLICK_MODE:
                x_index, y_index = int(index_tip.x * w), int(index_tip.y * h)
                x_middle, y_middle = int(middle_tip.x * w), int(middle_tip.y * h)

                cv2.circle(frame_BGR, (x_index, y_index), 10, (100, 0, 255), cv2.FILLED)
                cv2.circle(frame_BGR, (x_middle, y_middle), 10, (100, 0, 255), cv2.FILLED)
                cv2.line(frame_BGR, (x_index, y_index), (x_middle, y_middle), (100, 0, 255), 3)
                cv2.circle(frame_BGR, ((x_index + x_middle)//2, (y_index + y_middle)//2), 10, (100, 0, 255), cv2.FILLED)

                if x_index - x_middle < left_click_reg_dist:
                    cv2.circle(frame_BGR, ((x_index + x_middle)//2, (y_index + y_middle)//2), 10, (0, 255, 0), cv2.FILLED)
                    mouse.click(Button.left)

            if MODE == Mode.RIGHT_CLICK_MODE:
                x_index, y_index = int(index_tip.x * w), int(index_tip.y * h)
                x_thumb, y_thumb = int(thumb_tip.x * w), int(thumb_tip.y * h)

                cv2.circle(frame_BGR, (x_index, y_index), 10, (100, 0, 255), cv2.FILLED)
                cv2.circle(frame_BGR, (x_thumb, y_thumb), 10, (100, 0, 255), cv2.FILLED)
                cv2.line(frame_BGR, (x_index, y_index), (x_thumb, y_thumb), (100, 0, 255), 3)
                cv2.circle(frame_BGR, ((x_index + x_thumb)//2, (y_index + y_thumb)//2), 10, (100, 0, 255), cv2.FILLED)

                if  x_thumb - x_index < right_click_reg_dist and y_thumb - y_index < right_click_reg_dist:
                    cv2.circle(frame_BGR, ((x_index + x_thumb)//2, (y_index + y_thumb)//2), 10, (0, 255, 0), cv2.FILLED)
                    mouse.click(Button.right)
            
            if MODE == Mode.SCROLLING_MODE:
                x_index, y_index = int(index_tip.x * w), int(index_tip.y * h)
                x_middle, y_middle = int(middle_tip.x * w), int(middle_tip.y * h)
                x_ring, y_ring = int(ring_tip.x * w), int(ring_tip.y * h)

                cv2.circle(frame_BGR, (x_index, y_index), 10, (100, 0, 255), cv2.FILLED)
                cv2.circle(frame_BGR, (x_middle, y_middle), 10, (100, 0, 255), cv2.FILLED)
                cv2.circle(frame_BGR, (x_ring, y_ring), 10, (100, 0, 255), cv2.FILLED)
                cv2.line(frame_BGR, (x_index, y_index), (x_middle, y_middle), (100, 0, 255), 3)
                cv2.line(frame_BGR, (x_ring, y_ring), (x_middle, y_middle), (100, 0, 255), 3)
                cv2.circle(frame_BGR, ((x_index + x_middle)//2, (y_index + y_middle)//2), 10, (100, 0, 255), cv2.FILLED)
                cv2.circle(frame_BGR, ((x_ring + x_middle)//2, (y_ring + y_middle)//2), 10, (100, 0, 255), cv2.FILLED)

                if  x_index - x_middle > scroll_reg_dist and x_middle - x_ring < scroll_reg_dist:
                    cv2.circle(frame_BGR, ((x_index + x_middle)//2, (y_index + y_middle)//2), 10, (0, 255, 0), cv2.FILLED)
                    mouse.scroll(0, -1)
                elif  x_index - x_middle < scroll_reg_dist and x_middle - x_ring > scroll_reg_dist:
                    cv2.circle(frame_BGR, ((x_ring + x_middle)//2, (y_ring + y_middle)//2), 10, (0, 255, 0), cv2.FILLED)
                    mouse.scroll(0, 1)
                
            drawing_utils.draw_landmarks(
                frame_BGR,
                landmarks,
                mp_hands.HAND_CONNECTIONS,
                drawing_styles.get_default_hand_landmarks_style(),
                drawing_styles.get_default_hand_connections_style()
            )

    flipped_frame = cv2.flip(frame_BGR, 1)
    if args.fps_on:
        ctime = time.time()
        fps = int(1/(ctime-ptime))
        ptime = ctime
        cv2.putText(flipped_frame, str(fps), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow('main', flipped_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()