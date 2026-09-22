# Touchless Desktop Control

## Project Purpose
**Touchless Desktop Control** is an AI-powered computer vision application that enables touchless human-computer interaction. Using real-time hand gesture recognition via a standard webcam, users can control mouse navigation, trigger clicks, manage media playback, adjust audio volume, and execute system commands without physically touching a mouse or keyboard.

---

## Features
- **Cursor Control**: Move the system cursor smoothly using your index finger.
- **Mouse Clicks**: Pinch thumb and index finger for left-click actions.
- **Scrolling**: Two-finger navigation (index + middle) for scrolling up and down.
- **Volume Management**: Intuitive thumb up/down gestures to increase or decrease audio volume.
- **Media Controls**: Open palm for Play/Pause, directional swipes for Next/Previous tracks.
- **System Actions**: Make a fist to mute audio, extend three fingers to capture instant screenshots.
- **Safety Features**: Emergency stop hotkey (`ESC`) and on-screen emergency stop toggle.
- **Modern User Interface**: Dark-mode dashboard built with CustomTkinter displaying live video feed, active gesture, confidence level, and FPS metrics.

---

## Technology Stack
- **Programming Language**: Python 3.10+
- **Computer Vision & Tracking**: OpenCV (`opencv-python`), Google MediaPipe (`mediapipe`) Tasks API
- **Desktop Automation**: PyAutoGUI (`pyautogui`), Keyboard (`keyboard`), Screeninfo (`screeninfo`)
- **Audio Control**: PyCaw (`pycaw`), Comtypes (`comtypes`)
- **Graphical User Interface**: CustomTkinter (`customtkinter`), Pillow (`PIL`)
- **Numerical Processing**: NumPy (`numpy`)

---

## Project Structure
```text
TouchlessDesktopControl/
├── main.py                 # Application entry point
├── hand_tracker.py         # MediaPipe Hand Landmarker detection and tracking
├── gesture_detector.py     # Rule-based and dynamic gesture classification
├── desktop_controller.py   # Windows automation (mouse, keyboard, volume, screen)
├── config.py               # Configuration loader and default settings
├── config.json             # User-configurable parameters
├── logger.py               # Application logging utility
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation
├── .gitignore              # Git ignored files and directories
├── gui/
│   └── main_window.py      # CustomTkinter dashboard and webcam stream
└── utils/
    └── smoothing.py        # Exponential moving average and coordinate mapping
```

---

## Installation & Setup

### Prerequisites
- Windows 10 or Windows 11
- Python 3.10 or higher
- Standard integrated or USB webcam

### 1. Clone the Repository
```powershell
git clone https://github.com/Kokilapriya2003/Touchless_Desktop_Control.git
cd Touchless_Desktop_Control
```

### 2. Virtual Environment Setup
Create and activate an isolated Python virtual environment:

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Or in Command Prompt:
# venv\Scripts\activate.bat
```

### 3. Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running the Application
Launch the graphical interface:

```powershell
python main.py
```

1. Click **Start Camera** to initialize the webcam video feed.
2. Click **Start Control** to activate gesture automation.
3. Use hand gestures in front of the camera to control the desktop.
4. Press `ESC` or click **STOP CONTROL** at any time to instantly deactivate automation.

---

## Gesture Controls Guide

| Gesture | Landmarks / Pattern | Desktop Action |
|---|---|---|
| **Index Finger Up** | Index extended, others folded | Move Cursor |
| **Pinch** | Thumb tip + Index tip touching | Left Click |
| **Two Fingers Up** | Index + Middle extended | Scroll (Up if high, Down if low) |
| **Thumb Up** | Thumb raised upward | Volume Up |
| **Thumb Down** | Thumb pointed downward | Volume Down |
| **Open Palm** | All 5 fingers extended | Play / Pause Media |
| **Swipe Right** | Fast hand movement to right | Next Track |
| **Swipe Left** | Fast hand movement to left | Previous Track |
| **Fist** | All fingers curled | Mute / Unmute Audio |
| **Three Fingers Up** | Index + Middle + Ring extended | Take Screenshot |

---

## Configuration
Application parameters can be customized directly in `config.json`:

```json
{
    "camera_index": 0,
    "detection_confidence": 0.7,
    "tracking_confidence": 0.7,
    "cursor_smoothing": 0.5,
    "cursor_sensitivity": 1.0,
    "pinch_threshold": 0.05,
    "gesture_cooldown": 0.5,
    "scroll_sensitivity": 5,
    "swipe_threshold": 0.2,
    "screen_margin": 0.1,
    "single_hand_mode": true
}
```

- `cursor_smoothing`: Exponential smoothing factor (0.1 to 0.9) to reduce jitter.
- `pinch_threshold`: Distance threshold between thumb and index for pinch detection.
- `gesture_cooldown`: Cooldown interval (in seconds) between discrete gesture actions.
- `screen_margin`: Boundary margin to facilitate reaching screen edges.

---

## Troubleshooting
- **Camera Not Found / Black Screen**: Verify that no other software (e.g., Teams, Zoom, Skype) is utilizing the camera. Change `camera_index` in `config.json` if using an external USB webcam.
- **Jittery Cursor Movement**: Increase the `cursor_smoothing` parameter in `config.json` (e.g., set to `0.7`).
- **Pinch Not Registering**: Adjust `pinch_threshold` in `config.json` according to your camera distance.
- **Permission / Admin Errors**: Run your terminal or PowerShell as Administrator if Windows security prevents keyboard/mouse simulation.
- **Audio Control Issues**: Verify Windows audio endpoint settings and ensure PyCaw has access to master volume controls.
