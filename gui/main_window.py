import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import threading
import time
from logger import logger
import config
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from desktop_controller import DesktopController
from utils.smoothing import Smoothing, map_range
import keyboard

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Touchless Desktop Control")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")

        # Initialization
        self.tracker = HandTracker()
        self.detector = GestureDetector()
        self.controller = DesktopController()
        self.config = config.load_config()

        # State
        self.camera_running = False
        self.control_active = False
        self.current_gesture = "None"
        self.current_action = "None"
        self.fps = 0
        self.confidence = 0.0
        self.hand_label = "None"

        # Smoothing for cursor
        self.smooth_x = Smoothing(config.current_config["cursor_smoothing"])
        self.smooth_y = Smoothing(config.current_config["cursor_smoothing"])

        # UI Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # LEFT SIDE: Webcam Feed
        self.feed_frame = ctk.CTkFrame(self)
        self.feed_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.video_label = ctk.CTkLabel(self.feed_frame, text="")
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)

        # RIGHT SIDE: Dashboard
        self.dash_frame = ctk.CTkFrame(self, width=300)
        self.dash_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.status_title = ctk.CTkLabel(self.dash_frame, text="CONTROL DASHBOARD", font=("Segoe UI", 20, "bold"))
        self.status_title.pack(pady=20)

        # Status Indicators
        self.cam_status_lbl = ctk.CTkLabel(self.dash_frame, text="Camera: OFF", text_color="red")
        self.cam_status_lbl.pack(pady=5)

        self.ctrl_status_lbl = ctk.CTkLabel(self.dash_frame, text="Control: INACTIVE", text_color="red")
        self.ctrl_status_lbl.pack(pady=5)

        self.sep = ctk.CTkFrame(self.dash_frame, height=2, fg_color="gray")
        self.sep.pack(fill="x", padx=20, pady=15)

        self.gesture_lbl = ctk.CTkLabel(self.dash_frame, text="Detected Gesture:\nNone", font=("Segoe UI", 16))
        self.gesture_lbl.pack(pady=10)

        self.action_lbl = ctk.CTkLabel(self.dash_frame, text="Action:\nNone", font=("Segoe UI", 16))
        self.action_lbl.pack(pady=10)

        self.fps_lbl = ctk.CTkLabel(self.dash_frame, text="FPS: 0", font=("Segoe UI", 12))
        self.fps_lbl.pack(pady=5)

        self.conf_lbl = ctk.CTkLabel(self.dash_frame, text="Confidence: 0%", font=("Segoe UI", 12))
        self.conf_lbl.pack(pady=5)

        self.hand_lbl = ctk.CTkLabel(self.dash_frame, text="Hand: None", font=("Segoe UI", 12))
        self.hand_lbl.pack(pady=5)

        # Buttons
        self.btn_cam = ctk.CTkButton(self.dash_frame, text="Start Camera", command=self.toggle_camera)
        self.btn_cam.pack(pady=10, padx=20)

        self.btn_ctrl = ctk.CTkButton(self.dash_frame, text="Start Control", fg_color="green", command=self.toggle_control)
        self.btn_ctrl.pack(pady=10, padx=20)

        self.btn_stop = ctk.CTkButton(self.dash_frame, text="STOP CONTROL", fg_color="red", hover_color="darkred", command=self.emergency_stop)
        self.btn_stop.pack(pady=20, padx=20)

        # Setup ESC listener
        keyboard.add_hotkey('esc', self.emergency_stop)

    def toggle_camera(self):
        if not self.camera_running:
            self.camera_running = True
            self.btn_cam.configure(text="Stop Camera")
            self.cam_status_lbl.configure(text="Camera: ON", text_color="green")
            threading.Thread(target=self.camera_loop, daemon=True).start()
        else:
            self.camera_running = False
            self.btn_cam.configure(text="Start Camera")
            self.cam_status_lbl.configure(text="Camera: OFF", text_color="red")

    def toggle_control(self):
        self.control_active = not self.control_active
        self.controller.set_active(self.control_active)
        if self.control_active:
            self.btn_ctrl.configure(text="Stop Control", fg_color="orange")
            self.ctrl_status_lbl.configure(text="Control: ACTIVE", text_color="green")
        else:
            self.btn_ctrl.configure(text="Start Control", fg_color="green")
            self.ctrl_status_lbl.configure(text="Control: INACTIVE", text_color="red")

    def emergency_stop(self):
        self.control_active = False
        self.controller.set_active(False)
        self.btn_ctrl.configure(text="Start Control", fg_color="green")
        self.ctrl_status_lbl.configure(text="Control: INACTIVE", text_color="red")
        logger.warning("EMERGENCY STOP TRIGGERED")

    def camera_loop(self):
        cap = cv2.VideoCapture(config.current_config["camera_index"])
        prev_time = 0

        while self.camera_running:
            success, img = cap.read()
            if not success:
                logger.error("Failed to read from webcam")
                break

            img = cv2.flip(img, 1)
            h, w, c = img.shape

            # Tracking
            hands, handedness = self.tracker.find_hands(img)

            if hands:
                # Process only the first hand for control
                hand_lms = self.tracker.get_landmark_list(hands[0])

                if handedness and len(handedness) > 0:
                    hand_label = handedness[0]
                else:
                    hand_label = "Unknown"

                gesture, confidence = self.detector.detect_gesture(hand_lms, hand_label)

                # UI Update Data
                self.current_gesture = gesture
                self.confidence = confidence
                self.hand_label = hand_label

                # Action Execution
                self.execute_action(hand_lms, gesture)
            else:
                self.current_gesture = "None"
                self.confidence = 0.0
                self.hand_label = "None"

            # FPS Calculation
            curr_time = time.time()
            self.fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
            prev_time = curr_time

            # Update GUI
            self.update_ui_elements(img)

        cap.release()

    def execute_action(self, lms, gesture):
        # Coordinate Mapping for Cursor
        if gesture == "IndexUp":
            # Index finger tip (landmark 8)
            ix, iy = lms[8][0], lms[8][1]

            # Screen resolution
            import screeninfo
            screen = screeninfo.get_monitors()[0]
            sw, sh = screen.width, screen.height

            # Margin for easier reach
            margin = config.current_config["screen_margin"]

            # Map normalized coordinates to screen
            mapped_x = map_range(ix, margin, 1-margin, 0, sw)
            mapped_y = map_range(iy, margin, 1-margin, 0, sh)

            # Smooth it
            sx = self.smooth_x.smooth(mapped_x)
            sy = self.smooth_y.smooth(mapped_y)

            self.current_action = "Move Cursor"
            self.controller.move_cursor(sx, sy)

        elif gesture == "Pinch":
            self.current_action = "Left Click"
            self.controller.left_click()

        elif gesture == "TwoFinger":
            self.current_action = "Scroll"
            if lms[8][1] < 0.5:
                self.controller.scroll('up')
            else:
                self.controller.scroll('down')

        elif gesture == "ThumbUp":
            self.current_action = "Volume Up"
            self.controller.volume_up()

        elif gesture == "ThumbDown":
            self.current_action = "Volume Down"
            self.controller.volume_down()

        elif gesture == "OpenPalm":
            self.current_action = "Play/Pause"
            self.controller.play_pause()

        elif gesture == "SwipeRight":
            self.current_action = "Next Track"
            self.controller.next_track()

        elif gesture == "SwipeLeft":
            self.current_action = "Previous Track"
            self.controller.previous_track()

        elif gesture == "Fist":
            self.current_action = "Mute"
            self.controller.mute()

        elif gesture == "ThreeFingers":
            self.current_action = "Screenshot"
            self.controller.take_screenshot()

        else:
            self.current_action = "None"

    def update_ui_elements(self, img):
        # Convert BGR to RGB for Pillow
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        # Resize to fit frame
        img_pil = img_pil.resize((640, 480))

        # Use CTkImage for better scaling on HighDPI displays
        img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(640, 480))

        self.video_label.configure(image=img_ctk)
        self.video_label.image = img_ctk

        # Update Labels
        self.gesture_lbl.configure(text=f"Detected Gesture:\n{self.current_gesture}")
        self.action_lbl.configure(text=f"Action:\n{self.current_action}")
        self.fps_lbl.configure(text=f"FPS: {int(self.fps)}")
        self.conf_lbl.configure(text=f"Confidence: {int(self.confidence * 100)}%")
        self.hand_lbl.configure(text=f"Hand: {self.hand_label}")
