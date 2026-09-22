import numpy as np
import math
from logger import logger
import config

class GestureDetector:
    def __init__(self):
        self.prev_centroid = None
        self.swipe_frames = []
        self.swipe_threshold = config.current_config["swipe_threshold"]

    def get_distance(self, p1, p2):
        """Calculates Euclidean distance between two points."""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def is_finger_up(self, lm_list, finger_tip, finger_pip):
        """Checks if a finger is extended (except thumb)."""
        return lm_list[finger_tip][1] < lm_list[finger_pip][1]

    def detect_gesture(self, lm_list, hand_label):
        """
        Analyzes landmarks to identify a gesture.
        Returns: (gesture_name, confidence)
        """
        if not lm_list:
            return "None", 0.0

        # Finger tips and PIPs
        # Thumb: 4, Index: 8, Middle: 12, Ring: 16, Pinky: 20
        # PIPs: Thumb: 2, Index: 6, Middle: 10, Ring: 14, Pinky: 18

        # Thumb is special (horizontal movement usually)
        thumb_is_up = False
        if hand_label == "Right":
            thumb_is_up = lm_list[4][0] < lm_list[3][0]
        else:
            thumb_is_up = lm_list[4][0] > lm_list[3][0]

        index_up = self.is_finger_up(lm_list, 8, 6)
        middle_up = self.is_finger_up(lm_list, 12, 10)
        ring_up = self.is_finger_up(lm_list, 16, 14)
        pinky_up = self.is_finger_up(lm_list, 20, 18)

        # 1. Pinch (Thumb + Index)
        pinch_dist = self.get_distance(lm_list[4], lm_list[8])
        if pinch_dist < config.current_config["pinch_threshold"]:
            return "Pinch", 0.95

        # 2. Fist (All folded)
        if not index_up and not middle_up and not ring_up and not pinky_up:
            return "Fist", 0.90

        # 3. Open Palm (All extended)
        if index_up and middle_up and ring_up and pinky_up:
            return "OpenPalm", 0.95

        # 4. Move Cursor (Only Index)
        if index_up and not middle_up and not ring_up and not pinky_up:
            return "IndexUp", 0.95

        # 5. Scroll (Index + Middle)
        if index_up and middle_up and not ring_up and not pinky_up:
            return "TwoFinger", 0.95

        # 6. Screenshot (Index, Middle, Ring)
        if index_up and middle_up and ring_up and not pinky_up:
            return "ThreeFingers", 0.95

        # 7. Volume Up (Thumb Up)
        # Simple heuristic: Thumb is above index base
        if thumb_is_up and not index_up and not middle_up:
             # In reality, we check Y coordinate relative to hand center
             if lm_list[4][1] < lm_list[5][1]:
                return "ThumbUp", 0.85

        # 8. Volume Down (Thumb Down)
        if not thumb_is_up and not index_up and not middle_up:
             if lm_list[4][1] > lm_list[5][1]:
                return "ThumbDown", 0.85

        # 9. Swipes (Dynamic tracking)
        gesture, conf = self.track_swipe(lm_list)
        if gesture != "None":
            return gesture, conf

        return "None", 0.0

    def track_swipe(self, lm_list):
        """Tracks hand centroid to detect left/right swipes."""
        # Centroid is average of landmarks
        centroid = np.mean(lm_list, axis=0)

        if self.prev_centroid is None:
            self.prev_centroid = centroid
            return "None", 0.0

        # We look at the X movement over time
        dx = centroid[0] - self.prev_centroid[0]
        self.prev_centroid = centroid

        # Store history for swipe detection
        self.swipe_frames.append(dx)
        if len(self.swipe_frames) > 10:
            self.swipe_frames.pop(0)

        if len(self.swipe_frames) == 10:
            total_dx = sum(self.swipe_frames)
            if total_dx > self.swipe_threshold:
                self.swipe_frames = [] # Reset
                return "SwipeRight", 0.80
            elif total_dx < -self.swipe_threshold:
                self.swipe_frames = [] # Reset
                return "SwipeLeft", 0.80

        return "None", 0.0
