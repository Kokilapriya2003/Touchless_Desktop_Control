
class Smoothing:
    """Implements simple exponential moving average smoothing."""
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        self.prev_val = None

    def smooth(self, val):
        if self.prev_val is None:
            self.prev_val = val
            return val

        smoothed = self.alpha * val + (1 - self.alpha) * self.prev_val
        self.prev_val = smoothed
        return smoothed

def map_range(x, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another."""
    return (x - in_min) * (out_max - out_min) / (in_max - in_min + 1e-6) + out_min
