import json
import os
from logger import logger

DEFAULT_CONFIG = {
    "camera_index": 0,
    "detection_confidence": 0.7,
    "tracking_confidence": 0.7,
    "cursor_smoothing": 0.5,
    "cursor_sensitivity": 1.0,
    "pinch_threshold": 0.05, # Normalized distance
    "gesture_cooldown": 0.5,
    "scroll_sensitivity": 5,
    "swipe_threshold": 0.2, # Normalized
    "stability_frames": 3,
    "screen_margin": 0.1,
    "presentation_mode": False,
    "single_hand_mode": True,
    "gesture_mappings": {
        "IndexUp": "Move Cursor",
        "Pinch": "Left Click",
        "TwoFinger": "Scroll",
        "ThumbUp": "Volume Up",
        "ThumbDown": "Volume Down",
        "OpenPalm": "Play/Pause",
        "SwipeLeft": "Previous Track",
        "SwipeRight": "Next Track",
        "Fist": "Mute",
        "ThreeFingers": "Screenshot"
    }
}

CONFIG_FILE = "config.json"

def load_config():
    """Loads configuration from JSON file or returns defaults."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Ensure all default keys exist
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return DEFAULT_CONFIG

def save_config(config):
    """Saves configuration to JSON file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info("Configuration saved successfully.")
    except Exception as e:
        logger.error(f"Error saving config: {e}")

# Singleton config instance
current_config = load_config()
