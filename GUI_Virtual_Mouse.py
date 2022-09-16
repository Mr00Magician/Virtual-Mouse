import time
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import enum
from pyautogui import size
from numpy import interp
from pynput.mouse import Controller, Button
from mediapipe.python.solutions import hands as mp_hands, drawing_styles, drawing_utils

class Mode(enum.Enum):
    POINTER_MODE = 'point'
    LEFT_CLICK_MODE = 'left click'
    RIGHT_CLICK_MODE = 'right click'
    SCROLLING_MODE = 'scroll'

MAX_WEBCAM_DIST = 110

scr_w, scr_h = size()
cam_w, cam_h = int(640), int(480)

root = tk.Tk()
root.geometry(f'{int(cam_w * 1.5)}x{int(cam_h * 1.5)}')
root.title('Virtual Mouse v0.1.0')

label = tk.Label(root)
label.pack(fill = 'both', expand = tk.YES)

fps_on = tk.BooleanVar()
fps_on.set(False)
cap_id = tk.IntVar()
cap_id.set(0)
smoothness = tk.DoubleVar()
smoothness.set(3.5)
sensitivity = tk.IntVar()
sensitivity.set(2)
webcam_distance = tk.IntVar()
webcam_distance.set(30)

left_click_reg_dist = 12
right_click_reg_dist = 18
scroll_reg_dist = 40

detection_margin_left = 350
detection_margin_right = 100
detection_margin_up = 100
detection_margin_down = 200

def clear(var):
    var.set(None)

def custom_entry_dialog(var):
    custom_entry_win = tk.Toplevel(root)
    custom_entry_win.title('Set Custom Value')
    custom_entry_win.geometry('400x100')

    custom_entry = tk.Entry(custom_entry_win)
    custom_entry.pack()
    custom_entry.focus_set()

    label = tk.Label(custom_entry_win, text = 'Enter a value')
    label.pack()

    def set_value():
        value = custom_entry.get()
        if var == sensitivity:
            try:
                value = int(value)
                if value > 0:
                    var.set(value)
                    label.configure(text = 'Value set successfully!')
                else:
                    label.configure(text = 'Enter an integer greater than 0', fg = '#FF0000')
            except Exception as e:
                label.configure(text = 'Entered value is not an integer', fg = '#FF0000')

        elif var == webcam_distance:
            try:
                value = int(value)
                if value >= 10 and value <= 100:
                    var.set(value)
                    label.configure(text = 'Value set successfully!')
                else:
                    label.configure(text = 'Value must between 10 and 100 (both inclusive)', fg = '#FF0000')
            except Exception as e:
                label.configure(text = 'Entered value is not an integer', fg = '#FF0000')

        elif var == smoothness:
            try:
                value = float(value)
                if value > 0:
                    var.set(value)
                    label.configure(text = 'Value set successfully!')
                else:
                    label.configure(text = 'Value must be greater than 0', fg = '#FF0000')
            except Exception as e:
                label.configure(text = 'Entered value is not a number', fg = '#FF0000')
        else:
            global cap
            try:
                value = int(value)
                var.set(value)
                cap = cv2.VideoCapture(cap_id.get())
                label.configure(text = 'Value set successfully!')
            except Exception as e:
                label.configure(text = 'Entered value is not a number', fg = '#FF0000')

    set_button = tk.Button(custom_entry_win, text = 'Set Value', command = set_value)
    set_button.pack()

menubar = tk.Menu(root)
options_menu = tk.Menu(menubar, tearoff = 0)

sensitivity_menu = tk.Menu(options_menu, tearoff = 0)
sensitivity_menu.add_radiobutton(label = 1, variable = sensitivity, value = 1)
sensitivity_menu.add_radiobutton(label = 2, variable = sensitivity, value = 2)
sensitivity_menu.add_radiobutton(label = 3, variable = sensitivity, value = 3)
sensitivity_menu.add_radiobutton(label = 4, variable = sensitivity, value = 4)

smoothness_menu = tk.Menu(options_menu, tearoff = 0)
smoothness_menu.add_command(label = 'set custom value', command = lambda : custom_entry_dialog(smoothness))
smoothness_menu.add_separator()
smoothness_menu.add_radiobutton(label = 2, variable = smoothness, value = 2)
smoothness_menu.add_radiobutton(label = 2.5, variable = smoothness, value = 2.5)
smoothness_menu.add_radiobutton(label = 3, variable = smoothness, value = 3)
smoothness_menu.add_radiobutton(label = 3.5, variable = smoothness, value = 3.5)
smoothness_menu.add_radiobutton(label = 4, variable = smoothness, value = 4)
smoothness_menu.add_radiobutton(label = 4.5, variable = smoothness, value = 4.5)

Webcam_dist_menu = tk.Menu(options_menu, tearoff = 0)
Webcam_dist_menu.add_command(label = 'set custom value', command = lambda : custom_entry_dialog(webcam_distance))
Webcam_dist_menu.add_separator()
Webcam_dist_menu.add_radiobutton(label = 20, variable = webcam_distance, value = 20)
Webcam_dist_menu.add_radiobutton(label = 30, variable = webcam_distance, value = 30)
Webcam_dist_menu.add_radiobutton(label = 40, variable = webcam_distance, value = 40)
Webcam_dist_menu.add_radiobutton(label = 50, variable = webcam_distance, value = 50)

options_menu.add_checkbutton(label = 'FPS', variable = fps_on, onvalue = True, offvalue = False)
options_menu.add_cascade(label = 'smoothness', menu = smoothness_menu)
options_menu.add_cascade(label = 'Min Webcam Distance', menu = Webcam_dist_menu)
options_menu.add_cascade(label = 'Sensitivity', menu = sensitivity_menu)
options_menu.add_command(label = 'Cap Device ID', command = lambda : custom_entry_dialog(cap_id))

menubar.add_cascade(label = 'options', menu = options_menu)

root.config(menu = menubar)

cap = cv2.VideoCapture(cap_id.get())
cap.set(3, cam_w)
cap.set(4, cam_h)

curr_mode = None
ptime = 0
curr_mouse_x, curr_mouse_y = 0, 0
prev_mouse_x, prev_mouse_y = 0, 0

hands = mp_hands.Hands(max_num_hands = 1)
mouse = Controller()

def show_image():
    global ptime, prev_mouse_x, prev_mouse_y

    left_click_reg_dist = 12 + 0.25 * (100 - webcam_distance.get())
    right_click_reg_dist = 16 + 0.25 * (100 - webcam_distance.get()) 
    scroll_reg_dist = 40 + 0.4 * (100 - webcam_distance.get())

    detection_margin_left = 350 + (sensitivity.get() - 2) * 25
    detection_margin_right = 100 + (sensitivity.get() - 2) * 25
    detection_margin_up = 100 + (sensitivity.get() - 2) * 15
    detection_margin_down = 200 + (sensitivity.get() - 2) * 15

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
                curr_mode = Mode.SCROLLING_MODE
            elif index_tip.y < index_pip.y and ring_tip.y >= ring_pip.y and middle_tip.y >= middle_pip.y and thumb_tip.x < thumb_ip.x - 0.007:
                curr_mode = Mode.POINTER_MODE
            elif index_tip.y < index_pip.y and ring_tip.y >= ring_pip.y and middle_tip.y < middle_pip.y and thumb_tip.x < thumb_ip.x - 0.007:
                curr_mode = Mode.LEFT_CLICK_MODE
            elif index_tip.y < index_pip.y and ring_tip.y >= ring_pip.y and middle_tip.y >= middle_pip.y and thumb_tip.x >= thumb_ip.x- 0.007:
                curr_mode = Mode.RIGHT_CLICK_MODE
            else:
                curr_mode = None

            if curr_mode == Mode.POINTER_MODE:
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
                curr_mouse_x = prev_mouse_x + (x_cursor - prev_mouse_x)/smoothness.get() 
                curr_mouse_y = prev_mouse_y + (y_cursor - prev_mouse_y)/smoothness.get() 

                mouse.position = scr_w - curr_mouse_x, curr_mouse_y
                prev_mouse_x, prev_mouse_y = curr_mouse_x, curr_mouse_y

            if curr_mode == Mode.LEFT_CLICK_MODE:
                x_index, y_index = int(index_tip.x * w), int(index_tip.y * h)
                x_middle, y_middle = int(middle_tip.x * w), int(middle_tip.y * h)

                cv2.circle(frame_BGR, (x_index, y_index), 10, (100, 0, 255), cv2.FILLED)
                cv2.circle(frame_BGR, (x_middle, y_middle), 10, (100, 0, 255), cv2.FILLED)
                cv2.line(frame_BGR, (x_index, y_index), (x_middle, y_middle), (100, 0, 255), 3)
                cv2.circle(frame_BGR, ((x_index + x_middle)//2, (y_index + y_middle)//2), 10, (100, 0, 255), cv2.FILLED)

                print(x_index - x_middle)
                if x_index - x_middle < left_click_reg_dist:
                    cv2.circle(frame_BGR, ((x_index + x_middle)//2, (y_index + y_middle)//2), 10, (0, 255, 0), cv2.FILLED)
                    mouse.click(Button.left)

            if curr_mode == Mode.RIGHT_CLICK_MODE:
                x_index, y_index = int(index_tip.x * w), int(index_tip.y * h)
                x_thumb, y_thumb = int(thumb_tip.x * w), int(thumb_tip.y * h)

                cv2.circle(frame_BGR, (x_index, y_index), 10, (100, 0, 255), cv2.FILLED)
                cv2.circle(frame_BGR, (x_thumb, y_thumb), 10, (100, 0, 255), cv2.FILLED)
                cv2.line(frame_BGR, (x_index, y_index), (x_thumb, y_thumb), (100, 0, 255), 3)
                cv2.circle(frame_BGR, ((x_index + x_thumb)//2, (y_index + y_thumb)//2), 10, (100, 0, 255), cv2.FILLED)

                if  x_thumb + y_thumb - (x_index + y_index) < right_click_reg_dist:
                    cv2.circle(frame_BGR, ((x_index + x_thumb)//2, (y_index + y_thumb)//2), 10, (0, 255, 0), cv2.FILLED)
                    mouse.click(Button.right)
            
            if curr_mode == Mode.SCROLLING_MODE:
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

    flipped_frame = cv2.cvtColor(cv2.flip(frame_BGR, 1), cv2.COLOR_BGR2RGB)
    flipped_frame = cv2.resize(flipped_frame, (int(cam_w * 1.5), int(cam_h * 1.5)))

    if fps_on.get():
        ctime = time.time()
        fps = int(1/(ctime-ptime))
        ptime = ctime
        cv2.putText(flipped_frame, str(fps), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    img = ImageTk.PhotoImage(Image.fromarray(flipped_frame))
    label.image = img
    label.configure(image = img)
    label.after(20, show_image)

show_image()
root.mainloop()
cap.release()