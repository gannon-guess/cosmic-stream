import threading
import time


class CountdownTimer:
    def __init__(self, ws, source_name="timer text"):
        self.ws = ws
        self.source_name = source_name

        self.paused = True
        self.max_duration = 0
        self._start_time = None

    def set_time(self, minutes):
        self.duration = int(minutes * 60)
        self.max_duration = self.duration
        self.paused = True

    def play(self):
        if self.paused:
            self.paused = False
            self._start_time = time.monotonic()
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def pause(self):
        if not self.paused:
            self.paused = True
            self.running = False
            self.thread.join()

    def _run(self):
        last_displayed = None

        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            elapsed = time.monotonic() - self._start_time
            self.remaining = max(0, int(self.duration - elapsed))

            if self.remaining != last_displayed:
                self._update_obs(self.remaining)
                last_displayed = self.remaining

            if self.remaining <= 0:
                self.running = False
                break

            time.sleep(0.25)

    def _update_obs(self, remaining):
        mins = remaining // 60
        secs = remaining % 60
        display = f"{mins:02}:{secs:02}"

        try:
            self.ws.set_input_settings(
                name=self.source_name, settings={"text": display}, overlay=True
            )
        except Exception as e:
            print(f"⚠️ Could not update timer text: {e}")
