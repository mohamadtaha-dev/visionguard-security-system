from datetime import datetime
from pathlib import Path
import cv2


class SecuritySystem:

    def __init__(self):

        # =================================
        # DIRECTORIES
        # =================================

        self.log_directory = Path("logs")
        self.log_directory.mkdir(exist_ok=True)

        self.log_file = self.log_directory / "security.log"

        self.screenshot_directory = Path("screenshots")
        self.screenshot_directory.mkdir(exist_ok=True)

        # =================================
        # DETECTION STABILIZER
        # =================================

        self.previous_count = None
        self.candidate_count = None
        self.candidate_frames = 0

        self.required_stable_frames = 5

        # =================================
        # SECURITY STATE
        # =================================

        self.is_active = False
        self.alert_active = False

        # =================================
        # PRESENCE TIMER
        # =================================

        self.presence_start_time = None
        self.last_presence_duration = 0

        # =================================
        # PRESENCE HISTORY
        # =================================

        self.presence_history = []

        self.max_history_items = 20

        # =================================
        # STATISTICS
        # =================================

        self.total_detections = 0
        self.total_alerts = 0
        self.total_screenshots = 0
        self.total_presence_events = 0

        self.start_time = None

    # =================================
    # TIME
    # =================================

    def _get_time(self):

        return datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def _get_short_time(self):

        return datetime.now().strftime(
            "%H:%M:%S"
        )

    def _get_filename_time(self):

        return datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S-%f"
        )

    # =================================
    # LOG
    # =================================

    def log_event(self, event):

        message = f"[{self._get_time()}] {event}"

        try:

            with open(
                self.log_file,
                "a",
                encoding="utf-8"
            ) as file:

                file.write(message + "\n")

            print(message)

        except OSError as error:

            print(
                f"Could not write log: {error}"
            )

    # =================================
    # READ LOGS
    # =================================

    def read_logs(self, lines=10):

        if not self.log_file.exists():

            return []

        try:

            with open(
                self.log_file,
                "r",
                encoding="utf-8"
            ) as file:

                all_lines = file.readlines()

            return [
                line.strip()
                for line in all_lines[-lines:]
            ]

        except OSError as error:

            print(
                f"Could not read log file: {error}"
            )

            return []

    # =================================
    # START
    # =================================

    def start(self):

        if self.is_active:

            return

        self.is_active = True

        self.previous_count = None
        self.candidate_count = None
        self.candidate_frames = 0

        self.alert_active = False

        self.presence_start_time = None
        self.last_presence_duration = 0

        self.presence_history = []

        self.start_time = datetime.now()

        self.log_event(
            "Security system started"
        )

    # =================================
    # STOP
    # =================================

    def stop(self):

        if not self.is_active:

            return

        self.is_active = False

        self.previous_count = None
        self.candidate_count = None
        self.candidate_frames = 0

        self.alert_active = False

        if self.presence_start_time is not None:

            self._finish_presence()

        self.presence_start_time = None

        self.log_event(
            "Security system stopped"
        )

    # =================================
    # PERSON DETECTION
    # =================================

    def person_detected(self, count):

        try:

            count = int(count)

        except (TypeError, ValueError):

            count = 0

        count = max(0, count)

        # ---------------------------------
        # FIRST DETECTION
        # ---------------------------------

        if self.previous_count is None:

            self.previous_count = count

            self.candidate_count = None
            self.candidate_frames = 0

            if count > 0:

                self._start_presence()

                self.total_detections += 1

                if count == 1:

                    self.log_event(
                        "1 person detected"
                    )

                else:

                    self.log_event(
                        f"{count} people detected"
                    )

            else:

                self.log_event(
                    "No person detected"
                )

            return

        # ---------------------------------
        # SAME COUNT
        # ---------------------------------

        if count == self.previous_count:

            self.candidate_count = None
            self.candidate_frames = 0

            return

        # ---------------------------------
        # NEW CANDIDATE
        # ---------------------------------

        if count != self.candidate_count:

            self.candidate_count = count
            self.candidate_frames = 1

            return

        # ---------------------------------
        # CANDIDATE CONTINUES
        # ---------------------------------

        self.candidate_frames += 1

        if (
            self.candidate_frames
            < self.required_stable_frames
        ):

            return

        # ---------------------------------
        # ACCEPT NEW COUNT
        # ---------------------------------

        old_count = self.previous_count

        self.previous_count = count

        self.candidate_count = None
        self.candidate_frames = 0

        # ---------------------------------
        # PERSON ENTERED
        # ---------------------------------

        if old_count == 0 and count > 0:

            self._start_presence()

        # ---------------------------------
        # PERSON LEFT
        # ---------------------------------

        elif old_count > 0 and count == 0:

            self._finish_presence()

        # ---------------------------------
        # LOG
        # ---------------------------------

        if count == 0:

            self.log_event(
                "No person detected"
            )

        elif count == 1:

            self.total_detections += 1

            self.log_event(
                "1 person detected"
            )

        else:

            self.total_detections += 1

            self.log_event(
                f"{count} people detected"
            )

    # =================================
    # PRESENCE START
    # =================================

    def _start_presence(self):

        if self.presence_start_time is not None:

            return

        self.presence_start_time = datetime.now()

        self.total_presence_events += 1

        entry = {
            "type": "ENTER",
            "time": self._get_short_time(),
            "date": self._get_time(),
            "duration": "00:00:00"
        }

        self._add_presence_history(entry)

        self.log_event(
            "Presence timer started"
        )

    # =================================
    # PRESENCE FINISH
    # =================================

    def _finish_presence(self):

        if self.presence_start_time is None:

            return

        elapsed = (
            datetime.now()
            - self.presence_start_time
        )

        self.last_presence_duration = max(
            0,
            int(elapsed.total_seconds())
        )

        duration = self._format_duration(
            self.last_presence_duration
        )

        # ---------------------------------
        # UPDATE LAST ENTER EVENT
        # ---------------------------------

        if self.presence_history:

            last_event = self.presence_history[-1]

            if last_event["type"] == "ENTER":

                last_event["duration"] = duration

        # ---------------------------------
        # ADD EXIT EVENT
        # ---------------------------------

        exit_entry = {
            "type": "EXIT",
            "time": self._get_short_time(),
            "date": self._get_time(),
            "duration": duration
        }

        self._add_presence_history(
            exit_entry
        )

        self.log_event(
            f"Presence ended - Duration: {duration}"
        )

        self.presence_start_time = None

    # =================================
    # ADD HISTORY
    # =================================

    def _add_presence_history(self, entry):

        self.presence_history.append(entry)

        if len(self.presence_history) > self.max_history_items:

            self.presence_history.pop(0)

    # =================================
    # GET HISTORY
    # =================================

    def get_presence_history(self):

        return list(
            reversed(self.presence_history)
        )

    # =================================
    # CLEAR HISTORY
    # =================================

    def clear_presence_history(self):

        self.presence_history.clear()

        self.log_event(
            "Presence history cleared"
        )

    # =================================
    # PRESENCE DURATION
    # =================================

    def get_presence_duration(self):

        if self.presence_start_time is None:

            return self.last_presence_duration

        elapsed = (
            datetime.now()
            - self.presence_start_time
        )

        return max(
            0,
            int(elapsed.total_seconds())
        )

    # =================================
    # FORMAT DURATION
    # =================================

    def _format_duration(self, total_seconds):

        try:

            total_seconds = int(
                total_seconds
            )

        except (TypeError, ValueError):

            total_seconds = 0

        total_seconds = max(
            0,
            total_seconds
        )

        hours = total_seconds // 3600

        minutes = (
            total_seconds % 3600
        ) // 60

        seconds = (
            total_seconds % 60
        )

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

    # =================================
    # PRESENCE TIME
    # =================================

    def get_presence_time(self):

        return self._format_duration(
            self.get_presence_duration()
        )

    # =================================
    # SMART ALERT
    # =================================

    def check_smart_alert(self, person_count):

        try:

            person_count = int(
                person_count
            )

        except (TypeError, ValueError):

            person_count = 0

        person_count = max(
            0,
            person_count
        )

        if person_count == 0:

            self.alert_active = False

            return None

        if self.alert_active:

            return None

        self.alert_active = True

        if person_count == 1:

            message = (
                "New person detected"
            )

        else:

            message = (
                f"Multiple people detected: "
                f"{person_count}"
            )

        self.total_alerts += 1

        self.log_event(
            f"SMART ALERT: {message}"
        )

        return message

    # =================================
    # SECURITY ALERT
    # =================================

    def security_alert(self, message):

        self.total_alerts += 1

        self.log_event(
            f"SECURITY ALERT: {message}"
        )

    # =================================
    # SCREENSHOT
    # =================================

    def save_screenshot(self, frame):

        if frame is None:

            return None

        timestamp = self._get_filename_time()

        filename = (
            f"security_{timestamp}.jpg"
        )

        filepath = (
            self.screenshot_directory
            / filename
        )

        try:

            success = cv2.imwrite(
                str(filepath),
                frame
            )

        except Exception as error:

            self.log_event(
                f"Screenshot error: {error}"
            )

            return None

        if success:

            self.total_screenshots += 1

            self.log_event(
                "Security screenshot saved: "
                f"{filename}"
            )

            return filepath

        self.log_event(
            "Failed to save security screenshot"
        )

        return None

    # =================================
    # UPTIME
    # =================================

    def get_uptime(self):

        if self.start_time is None:

            return "00:00:00"

        elapsed = (
            datetime.now()
            - self.start_time
        )

        total_seconds = int(
            elapsed.total_seconds()
        )

        return self._format_duration(
            total_seconds
        )

    # =================================
    # STATISTICS
    # =================================

    def get_statistics(self):

        return {

            "detections":
                self.total_detections,

            "alerts":
                self.total_alerts,

            "screenshots":
                self.total_screenshots,

            "presence_events":
                self.total_presence_events,

            "presence":
                self.get_presence_time(),

            "uptime":
                self.get_uptime()
        }