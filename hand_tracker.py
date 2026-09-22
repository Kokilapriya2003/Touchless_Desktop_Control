import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from logger import logger
import config
import numpy as np

class HandTracker:
    def __init__(self):
        """Initializes MediaPipe Hand Landmarker using the modern Tasks API."""
        try:
            # Create the Landmarker
            # Using 'hands_new.task' as it was downloaded successfully
            base_options = python.BaseOptions(model_asset_path='hands_new.task')
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=2 if not config.current_config["single_hand_mode"] else 1,
                min_hand_detection_confidence=config.current_config["detection_confidence"],
                min_hand_presence_confidence=config.current_config["tracking_confidence"],
                min_tracking_confidence=config.current_config["tracking_confidence"]
            )
            self.detector = vision.HandLandmarker.create_from_options(options)

            # Drawing utility
            self.mp_draw = mp.solutions.drawing_utils if hasattr(mp, 'solutions') else None
            if not self.mp_draw:
                pass

            logger.info("HandTracker initialized with Tasks API.")
        except Exception as e:
            logger.error(f"Failed to initialize HandTracker with Tasks API: {e}")
            raise RuntimeError(f"HandTracker initialization failed: {e}")

    def find_hands(self, img, draw=True):
        """Detects hands and returns landmarks and handedness."""
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        results = self.detector.detect(mp_image)

        if results.hand_landmarks:
            if draw:
                self._draw_landmarks(img, results.hand_landmarks)

            return results.hand_landmarks, results.handedness

        return None, None

    def _draw_landmarks(self, img, hand_landmarks):
        """Simple manual drawing of landmarks."""
        h, w, _ = img.shape
        for hand_lms in hand_landmarks:
            for lm in hand_lms:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 3, (0, 255, 0), -1)

    def get_landmark_list(self, hand_landmarks):
        """Converts Tasks API landmarks to a list of [x, y, z]."""
        return [[lm.x, lm.y, lm.z] for lm in hand_landmarks]

    def update_settings(self, det_conf, track_conf, single_hand):
        """Updates MediaPipe settings dynamically."""
        config.current_config["detection_confidence"] = det_conf
        config.current_config["tracking_confidence"] = track_conf
        config.current_config["single_hand_mode"] = single_hand
        self.__init__()
        logger.info("HandTracker settings updated.")
