import threading
from datetime import datetime as dt
import time


class Clock:
    def __init__(self, ws, source_name="clock text"):
        self.ws = ws
        self.source_name = source_name

        self.active = False

    def set_time(self, minutes):
        self.active = True

    def play(self):
        if not self.active:
            self.active = True
            self.thread = threading.Thread(target=self._run)
            self.thread.start()
        self.active = True

    def pause(self):
        self.active = False

    def _run(self):
        while self.active:
            now = dt.now()
            display = now.strftime("%I:%M %p")
            self._update_obs(display)
            time.sleep(1)

    def _update_obs(self, time):
        try:
            self.ws.set_input_settings(
                name=self.source_name, settings={"text": time}, overlay=True
            )
        except Exception as e:
            print(f"⚠️ Could not update timer text: {e}")
