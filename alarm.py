import winsound
import threading


class AlarmSystem:

    def __init__(self):
        self.active = False
        self.thread = None

    def _alarm_loop(self):

        while self.active:

            try:
                # صدای هشدار
                winsound.Beep(1000, 300)

                if not self.active:
                    break

                winsound.Beep(700, 300)

            except Exception as error:

                print(
                    f"Alarm error: {error}"
                )

                break

    def play_alarm(self):

        # اگر آلارم از قبل فعال است
        if self.active:
            return

        self.active = True

        self.thread = threading.Thread(
            target=self._alarm_loop,
            daemon=True
        )

        self.thread.start()

        print("🔊 SECURITY ALARM!")

    def stop_alarm(self):

        self.active = False

    def reset(self):

        self.stop_alarm()

    def release(self):

        self.stop_alarm()