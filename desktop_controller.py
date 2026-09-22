import pyautogui
import keyboard
import ctypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from logger import logger
import config
import os
from datetime import datetime

class DesktopController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.volume_control = self._init_volume()
        self.active = False

    def _init_volume(self):
        """Initializes PyCaw volume control."""
        try:
            speakers = AudioUtilities.GetSpeakers()
            # In some versions of PyCaw, the volume interface is already accessible
            # via the _volume attribute or we can use the standard IAudioEndpointVolume.
            # The most reliable way is often using the EndpointVolume property if available.
            if hasattr(speakers, 'EndpointVolume'):
                return speakers.EndpointVolume

            # Fallback: Use the raw COM interface
            interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        except Exception as e:
            logger.error(f"Could not initialize volume control: {e}")
            return None

    def set_active(self, status: bool):
        self.active = status
        logger.info(f"Desktop control {'activated' if status else 'deactivated'}.")

    def move_cursor(self, x, y):
        if not self.active: return
        try:
            pyautogui.moveTo(x, y, _pause=False)
        except Exception as e:
            logger.error(f"Cursor move error: {e}")

    def left_click(self):
        if not self.active: return
        pyautogui.click()

    def right_click(self):
        if not self.active: return
        pyautogui.rightClick()

    def double_click(self):
        if not self.active: return
        pyautogui.doubleClick()

    def mouse_down(self):
        if not self.active: return
        pyautogui.mouseDown()

    def mouse_up(self):
        if not self.active: return
        pyautogui.mouseUp()

    def scroll(self, direction):
        if not self.active: return
        amount = config.current_config["scroll_sensitivity"] * 10
        pyautogui.scroll(amount if direction == 'up' else -amount)

    def volume_up(self):
        if not self.active or not self.volume_control: return
        try:
            current_vol = self.volume_control.GetMasterVolumeLevelScalar()
            self.volume_control.SetMasterVolumeLevelScalar(min(1.0, current_vol + 0.05), None)
        except Exception as e:
            logger.error(f"Volume Up error: {e}")

    def volume_down(self):
        if not self.active or not self.volume_control: return
        try:
            current_vol = self.volume_control.GetMasterVolumeLevelScalar()
            self.volume_control.SetMasterVolumeLevelScalar(max(0.0, current_vol - 0.05), None)
        except Exception as e:
            logger.error(f"Volume Down error: {e}")

    def mute(self):
        if not self.active or not self.volume_control: return
        try:
            is_muted = self.volume_control.GetMute()
            self.volume_control.SetMute(not is_muted, None)
        except Exception as e:
            logger.error(f"Mute error: {e}")

    def play_pause(self):
        if not self.active: return
        try:
            pyautogui.press('playpause')
        except Exception:
            try:
                keyboard.press_and_release('play/pause media')
            except:
                logger.error("Play/Pause key not supported on this system.")

    def next_track(self):
        if not self.active: return
        try:
            pyautogui.press('nexttrack')
        except Exception:
            try:
                keyboard.press_and_release('next track')
            except:
                logger.error("Next Track key not supported on this system.")

    def previous_track(self):
        if not self.active: return
        try:
            pyautogui.press('prevtrack')
        except Exception:
            try:
                keyboard.press_and_release('previous track')
            except:
                logger.error("Previous Track key not supported on this system.")

    def take_screenshot(self):
        if not self.active: return
        save_path = "screenshots"
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(save_path, filename)

        pyautogui.screenshot(filepath)
        logger.info(f"Screenshot saved to {filepath}")

    def press_key(self, key):
        if not self.active: return
        keyboard.press_and_release(key)

    def hotkey(self, keys):
        if not self.active: return
        keyboard.press_and_release(keys)
