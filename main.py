import cv2
import time
import traceback

from camera import Camera
from face_detector import FaceDetector
from security import SecuritySystem
from alarm import AlarmSystem
from report import SecurityReport


# ==========================================
# VISIONGUARD
# ==========================================

WINDOW_NAME = "VisionGuard"

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720


# ==========================================
# COLORS
# ==========================================

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
YELLOW = (0, 255, 255)
BLUE = (255, 180, 0)
GRAY = (170, 170, 170)
DARK = (20, 20, 20)


# ==========================================
# TEXT
# ==========================================

def draw_text(
    image,
    text,
    x,
    y,
    color=WHITE,
    scale=0.6,
    thickness=1
):

    cv2.putText(
        image,
        str(text),
        (int(x), int(y)),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA
    )


# ==========================================
# SAFE INTEGER
# ==========================================

def safe_int(value, default=0):

    try:

        if hasattr(value, "item"):
            value = value.item()

        return int(value)

    except Exception:

        try:
            return int(float(value))

        except Exception:
            return default


# ==========================================
# FACE NORMALIZATION
# ==========================================

def normalize_faces(faces):

    result = []

    if faces is None:
        return result

    try:

        for face in faces:

            try:

                if len(face) < 4:
                    continue

                x = safe_int(face[0])
                y = safe_int(face[1])
                w = safe_int(face[2])
                h = safe_int(face[3])

                if w <= 0 or h <= 0:
                    continue

                result.append(
                    (x, y, w, h)
                )

            except Exception:

                continue

    except Exception:

        pass

    return result


# ==========================================
# PREPARE FRAME
# ==========================================

def prepare_frame(frame):

    if frame is None:
        return None

    try:

        return cv2.resize(
            frame,
            (
                FRAME_WIDTH,
                FRAME_HEIGHT
            ),
            interpolation=cv2.INTER_LINEAR
        )

    except Exception:

        return frame


# ==========================================
# DRAW PANEL
# ==========================================

def draw_panel(
    image,
    x1,
    y1,
    x2,
    y2,
    border_color=(80, 80, 80)
):

    overlay = image.copy()

    cv2.rectangle(
        overlay,
        (x1, y1),
        (x2, y2),
        DARK,
        -1
    )

    cv2.addWeighted(
        overlay,
        0.86,
        image,
        0.14,
        0,
        image
    )

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        border_color,
        1
    )


# ==========================================
# SECTION TITLE
# ==========================================

def draw_section_title(
    canvas,
    title,
    x,
    y,
    color=WHITE
):

    draw_text(
        canvas,
        title,
        x,
        y,
        color,
        0.58,
        2
    )

    cv2.line(
        canvas,
        (x, y + 8),
        (x + 285, y + 8),
        (70, 70, 70),
        1
    )


# ==========================================
# HEADER
# ==========================================

def draw_header(canvas):

    cv2.rectangle(
        canvas,
        (0, 0),
        (
            FRAME_WIDTH,
            70
        ),
        (12, 12, 12),
        -1
    )

    cv2.rectangle(
        canvas,
        (0, 0),
        (6, 70),
        GREEN,
        -1
    )

    draw_text(
        canvas,
        "VISIONGUARD",
        25,
        32,
        GREEN,
        0.85,
        2
    )

    draw_text(
        canvas,
        "AI SECURITY & COMPUTER VISION",
        27,
        55,
        GRAY,
        0.42,
        1
    )

    cv2.circle(
        canvas,
        (1110, 31),
        6,
        GREEN,
        -1
    )

    draw_text(
        canvas,
        "SYSTEM ONLINE",
        1125,
        36,
        GREEN,
        0.48,
        1
    )

    draw_text(
        canvas,
        "LIVE",
        1200,
        58,
        GRAY,
        0.38,
        1
    )


# ==========================================
# STATUS
# ==========================================

def draw_status(
    canvas,
    security,
    face_count,
    camera_online=True
):

    x = 30
    y = 110

    draw_section_title(
        canvas,
        "SYSTEM STATUS",
        x,
        y
    )

    y += 35

    camera_status = (
        "ONLINE"
        if camera_online
        else "OFFLINE"
    )

    draw_text(
        canvas,
        "Camera",
        x,
        y,
        GRAY,
        0.45,
        1
    )

    draw_text(
        canvas,
        camera_status,
        x + 150,
        y,
        GREEN if camera_online else RED,
        0.45,
        2
    )

    y += 27

    draw_text(
        canvas,
        "Face Detection",
        x,
        y,
        GRAY,
        0.45,
        1
    )

    draw_text(
        canvas,
        "ENABLED",
        x + 150,
        y,
        GREEN,
        0.45,
        1
    )

    y += 27

    draw_text(
        canvas,
        "Eye Detection",
        x,
        y,
        GRAY,
        0.45,
        1
    )

    draw_text(
        canvas,
        "ENABLED",
        x + 150,
        y,
        GREEN,
        0.45,
        1
    )

    y += 27

    draw_text(
        canvas,
        "People Counting",
        x,
        y,
        GRAY,
        0.45,
        1
    )

    draw_text(
        canvas,
        "ENABLED",
        x + 150,
        y,
        GREEN,
        0.45,
        1
    )

    y += 27

    draw_text(
        canvas,
        "Smart Alert",
        x,
        y,
        GRAY,
        0.45,
        1
    )

    draw_text(
        canvas,
        "ENABLED",
        x + 150,
        y,
        GREEN,
        0.45,
        1
    )

    y += 32

    draw_text(
        canvas,
        "CURRENT PEOPLE",
        x,
        y,
        GRAY,
        0.40,
        1
    )

    draw_text(
        canvas,
        face_count,
        x + 150,
        y,
        YELLOW if face_count else GRAY,
        0.62,
        2
    )

    y += 29

    presence_time = (
        security.get_presence_time()
    )

    draw_text(
        canvas,
        "PRESENCE",
        x,
        y,
        GRAY,
        0.40,
        1
    )

    draw_text(
        canvas,
        presence_time,
        x + 150,
        y,
        YELLOW if face_count else GRAY,
        0.46,
        1
    )


# ==========================================
# STATISTICS
# ==========================================

def draw_statistics(
    canvas,
    security
):

    stats = security.get_statistics()

    x = 30
    y = 355

    draw_section_title(
        canvas,
        "STATISTICS",
        x,
        y
    )

    y += 35

    values = [

        (
            "Detections",
            stats["detections"],
            GRAY
        ),

        (
            "Alerts",
            stats["alerts"],
            RED
            if stats["alerts"]
            else GRAY
        ),

        (
            "Screenshots",
            stats["screenshots"],
            GRAY
        ),

        (
            "Presence Events",
            stats["presence_events"],
            GRAY
        ),

        (
            "Uptime",
            stats["uptime"],
            GREEN
        )
    ]

    for label, value, color in values:

        draw_text(
            canvas,
            label,
            x,
            y,
            GRAY,
            0.43,
            1
        )

        draw_text(
            canvas,
            value,
            x + 150,
            y,
            color,
            0.45,
            1
        )

        y += 26


# ==========================================
# EVENT HISTORY
# ==========================================

def draw_events(
    canvas,
    security
):

    x = 30
    y = 575

    draw_section_title(
        canvas,
        "EVENT HISTORY",
        x,
        y
    )

    logs = security.read_logs(5)

    y += 30

    if not logs:

        draw_text(
            canvas,
            "No events yet.",
            x,
            y,
            GRAY,
            0.42,
            1
        )

        return

    for log in reversed(logs):

        if len(log) > 47:

            log = log[-47:]

        color = GRAY

        if "ALERT" in log:

            color = RED

        elif "detected" in log.lower():

            color = YELLOW

        elif "started" in log.lower():

            color = GREEN

        draw_text(
            canvas,
            log,
            x,
            y,
            color,
            0.31,
            1
        )

        y += 22

        if y > 690:

            break


# ==========================================
# PRESENCE HISTORY
# ==========================================

def draw_presence_history(
    canvas,
    security
):

    x = 375
    y = 610

    draw_section_title(
        canvas,
        "PRESENCE HISTORY",
        x,
        y
    )

    history = (
        security.get_presence_history()
    )

    y += 30

    if not history:

        draw_text(
            canvas,
            "No presence events yet.",
            x,
            y,
            GRAY,
            0.40,
            1
        )

        return

    history = history[:4]

    for item in history:

        event_type = item.get(
            "type",
            "UNKNOWN"
        )

        event_time = item.get(
            "time",
            "--:--:--"
        )

        duration = item.get(
            "duration",
            "00:00:00"
        )

        if event_type == "ENTER":

            label = "ENTER"
            color = GREEN

        elif event_type == "EXIT":

            label = "EXIT"
            color = RED

        else:

            label = event_type
            color = GRAY

        draw_text(
            canvas,
            label,
            x,
            y,
            color,
            0.42,
            2
        )

        draw_text(
            canvas,
            event_time,
            x + 75,
            y,
            WHITE,
            0.40,
            1
        )

        draw_text(
            canvas,
            f"Duration: {duration}",
            x + 165,
            y,
            GRAY,
            0.38,
            1
        )

        y += 27


# ==========================================
# CAMERA INFO
# ==========================================

def draw_camera_info(
    canvas,
    face_count,
    fps
):

    draw_text(
        canvas,
        f"FPS: {fps:.1f}",
        FRAME_WIDTH - 155,
        35,
        GREEN,
        0.45,
        1
    )

    draw_text(
        canvas,
        f"Faces: {face_count}",
        FRAME_WIDTH - 155,
        55,
        YELLOW,
        0.45,
        1
    )


# ==========================================
# CAMERA LABEL
# ==========================================

def draw_camera_label(
    canvas,
    x,
    y
):

    draw_text(
        canvas,
        "LIVE CAMERA",
        x + 15,
        y + 28,
        GREEN,
        0.48,
        2
    )

    cv2.circle(
        canvas,
        (x + 125, y + 22),
        5,
        RED,
        -1
    )


# ==========================================
# ALERT BOX
# ==========================================

def draw_alert(
    canvas,
    camera_x1,
    camera_y1,
    message
):

    if not message:
        return

    x1 = camera_x1 + 20
    y1 = camera_y1 + 50

    x2 = camera_x1 + 340
    y2 = camera_y1 + 105

    cv2.rectangle(
        canvas,
        (x1, y1),
        (x2, y2),
        RED,
        -1
    )

    draw_text(
        canvas,
        "SECURITY ALERT",
        x1 + 15,
        y1 + 23,
        WHITE,
        0.48,
        2
    )

    short_message = str(
        message
    )

    if len(short_message) > 35:

        short_message = (
            short_message[:35]
        )

    draw_text(
        canvas,
        short_message,
        x1 + 15,
        y1 + 45,
        WHITE,
        0.34,
        1
    )


# ==========================================
# MAIN
# ==========================================

def main():

    print("================================")
    print("        VISIONGUARD")
    print("================================")
    print("Starting system...")

    camera = None
    detector = None
    security = None
    alarm = None
    report = None

    try:

        camera = Camera()

        detector = FaceDetector()

        security = SecuritySystem()

        alarm = AlarmSystem()

        report = SecurityReport(
            security
        )

        security.start()

        security.log_event(
            "VisionGuard started"
        )

        print("Camera: ONLINE")
        print("Face detection: ENABLED")
        print("Eye detection: ENABLED")
        print("People counting: ENABLED")
        print("Security system: ENABLED")
        print("Smart Alert: ENABLED")
        print("Audio Alarm: ENABLED")
        print("Presence Timer: ENABLED")
        print("Event history: ENABLED")
        print("Presence History: ENABLED")
        print("Screenshot system: ENABLED")
        print("Auto Screenshot: ENABLED")
        print("Security Reports: ENABLED")
        print()
        print("Press Q or ESC to exit.")

        cv2.namedWindow(
            WINDOW_NAME,
            cv2.WINDOW_NORMAL
        )

        cv2.resizeWindow(
            WINDOW_NAME,
            FRAME_WIDTH,
            FRAME_HEIGHT
        )

        previous_time = time.time()

        fps = 0.0

        last_alert_screenshot = 0

        while True:

            try:

                frame = camera.read()

                if frame is None:

                    print(
                        "Camera returned empty frame."
                    )

                    time.sleep(0.1)

                    continue

                frame = prepare_frame(
                    frame
                )

                _, faces = (
                    detector.detect_faces(
                        frame
                    )
                )

                faces = normalize_faces(
                    faces
                )

                face_count = len(
                    faces
                )

                eyes = []

                try:

                    eyes = (
                        detector.detect_eyes(
                            frame,
                            faces
                        )
                    )

                    if eyes is None:
                        eyes = []

                except Exception as eye_error:

                    print(
                        "Eye detection warning: "
                        f"{eye_error}"
                    )

                    eyes = []

                security.person_detected(
                    face_count
                )

                alert_message = (
                    security.check_smart_alert(
                        face_count
                    )
                )

                if alert_message:

                    print(
                        f"SMART ALERT: "
                        f"{alert_message}"
                    )

                    current_alert_time = (
                        time.time()
                    )

                    if (
                        current_alert_time
                        - last_alert_screenshot
                        > 3
                    ):

                        try:

                            screenshot_path = (
                                security.save_screenshot(
                                    frame
                                )
                            )

                            if screenshot_path:

                                print(
                                    "📸 Security "
                                    "screenshot saved: "
                                    f"{screenshot_path}"
                                )

                                last_alert_screenshot = (
                                    current_alert_time
                                )

                        except Exception as screenshot_error:

                            print(
                                "Screenshot error: "
                                f"{screenshot_error}"
                            )

                    try:

                        alarm.play_alarm()

                    except Exception:

                        pass

                elif face_count == 0:

                    try:

                        alarm.stop_alarm()

                    except Exception:

                        pass

                camera_frame = frame.copy()

                try:

                    camera_frame = (
                        detector.draw_faces_and_eyes(
                            camera_frame,
                            faces,
                            eyes
                        )
                    )

                except Exception:

                    camera_frame = (
                        detector.draw_faces(
                            camera_frame,
                            faces
                        )
                    )

                canvas = frame.copy()

                overlay = canvas.copy()

                cv2.rectangle(
                    overlay,
                    (0, 0),
                    (
                        FRAME_WIDTH,
                        FRAME_HEIGHT
                    ),
                    (0, 0, 0),
                    -1
                )

                cv2.addWeighted(
                    overlay,
                    0.30,
                    canvas,
                    0.70,
                    0,
                    canvas
                )

                camera_x1 = 365
                camera_y1 = 85
                camera_x2 = 1245
                camera_y2 = 585

                camera_width = (
                    camera_x2
                    - camera_x1
                )

                camera_height = (
                    camera_y2
                    - camera_y1
                )

                try:

                    display_frame = cv2.resize(
                        camera_frame,
                        (
                            camera_width,
                            camera_height
                        )
                    )

                    canvas[
                        camera_y1:camera_y2,
                        camera_x1:camera_x2
                    ] = display_frame

                    cv2.rectangle(
                        canvas,
                        (
                            camera_x1,
                            camera_y1
                        ),
                        (
                            camera_x2,
                            camera_y2
                        ),
                        GREEN,
                        2
                    )

                    draw_camera_label(
                        canvas,
                        camera_x1,
                        camera_y1
                    )

                except Exception:

                    pass

                draw_header(
                    canvas
                )

                draw_panel(
                    canvas,
                    15,
                    80,
                    345,
                    535
                )

                draw_status(
                    canvas,
                    security,
                    face_count,
                    True
                )

                draw_statistics(
                    canvas,
                    security
                )

                draw_panel(
                    canvas,
                    15,
                    550,
                    345,
                    700
                )

                draw_events(
                    canvas,
                    security
                )

                draw_panel(
                    canvas,
                    365,
                    595,
                    1245,
                    700,
                    (70, 70, 70)
                )

                draw_presence_history(
                    canvas,
                    security
                )

                draw_camera_info(
                    canvas,
                    face_count,
                    fps
                )

                draw_alert(
                    canvas,
                    camera_x1,
                    camera_y1,
                    alert_message
                )

                current_time = time.time()

                delta = (
                    current_time
                    - previous_time
                )

                if delta > 0:

                    current_fps = (
                        1.0 / delta
                    )

                    fps = (
                        fps * 0.9
                        + current_fps * 0.1
                    )

                previous_time = (
                    current_time
                )

                cv2.imshow(
                    WINDOW_NAME,
                    canvas
                )

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if key in (
                    ord("q"),
                    ord("Q"),
                    27
                ):

                    break

            except Exception as loop_error:

                print(
                    "\n========== LOOP ERROR =========="
                )

                traceback.print_exc()

                print(
                    "================================\n"
                )

                if security:

                    security.log_event(
                        f"Loop error: "
                        f"{loop_error}"
                    )

                time.sleep(0.2)

    except Exception as error:

        print(
            "\n========== VISIONGUARD ERROR =========="
        )

        traceback.print_exc()

        print(
            "========================================\n"
        )

        if security:

            security.log_event(
                f"Unexpected error: "
                f"{error}"
            )

        print(
            f"Error: {error}"
        )

    finally:

        # ==================================
        # STOP ALARM
        # ==================================

        try:

            if alarm:
                alarm.stop_alarm()

        except Exception:

            pass

        # ==================================
        # GENERATE SECURITY REPORT
        # ==================================

        try:

            if report:

                report_path = (
                    report.save_report()
                )

                if report_path:

                    print(
                        "📄 Report created: "
                        f"{report_path}"
                    )

        except Exception as report_error:

            print(
                f"Report error: "
                f"{report_error}"
            )

        # ==================================
        # STOP SECURITY SYSTEM
        # ==================================

        try:

            if security:

                security.stop()

                security.log_event(
                    "VisionGuard stopped"
                )

        except Exception:

            pass

        # ==================================
        # RELEASE CAMERA
        # ==================================

        try:

            if camera:
                camera.release()

        except Exception:

            pass

        # ==================================
        # CLOSE WINDOWS
        # ==================================

        try:

            cv2.destroyAllWindows()

        except Exception:

            pass

        print(
            "VisionGuard stopped."
        )


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    main()