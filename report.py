from datetime import datetime
from pathlib import Path


class SecurityReport:

    def __init__(self, security_system):

        self.security = security_system

        self.report_directory = Path("reports")
        self.report_directory.mkdir(exist_ok=True)

    def generate_report(self):

        stats = self.security.get_statistics()

        now = datetime.now()

        report = []

        report.append("=" * 50)
        report.append("           VISIONGUARD SECURITY REPORT")
        report.append("=" * 50)

        report.append("")

        report.append(
            f"Date: {now.strftime('%Y-%m-%d')}"
        )

        report.append(
            f"Time: {now.strftime('%H:%M:%S')}"
        )

        report.append("")

        report.append("-" * 50)
        report.append("SESSION STATISTICS")
        report.append("-" * 50)

        report.append(
            f"Uptime           : {stats['uptime']}"
        )

        report.append(
            f"Total Detections : {stats['detections']}"
        )

        report.append(
            f"Security Alerts  : {stats['alerts']}"
        )

        report.append(
            f"Screenshots      : {stats['screenshots']}"
        )

        report.append(
            f"Presence Events  : {stats['presence_events']}"
        )

        report.append(
            f"Current Presence : {stats['presence']}"
        )

        report.append("")

        report.append("-" * 50)
        report.append("PRESENCE HISTORY")
        report.append("-" * 50)

        history = (
            self.security.get_presence_history()
        )

        if not history:

            report.append(
                "No presence events recorded."
            )

        else:

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

                report.append(
                    f"{event_type:<8} "
                    f"{event_time:<10} "
                    f"Duration: {duration}"
                )

        report.append("")

        report.append("-" * 50)
        report.append("RECENT EVENTS")
        report.append("-" * 50)

        logs = self.security.read_logs(10)

        if not logs:

            report.append(
                "No events recorded."
            )

        else:

            for log in logs:

                report.append(log)

        report.append("")

        report.append("-" * 50)
        report.append("SYSTEM STATUS")
        report.append("-" * 50)

        if self.security.is_active:

            report.append(
                "Security System : ONLINE"
            )

        else:

            report.append(
                "Security System : OFFLINE"
            )

        report.append(
            "Face Detection  : ENABLED"
        )

        report.append(
            "Smart Alert     : ENABLED"
        )

        report.append(
            "Screenshot      : ENABLED"
        )

        report.append(
            "Audio Alarm     : ENABLED"
        )

        report.append("")

        report.append("=" * 50)
        report.append("              END OF REPORT")
        report.append("=" * 50)

        return "\n".join(report)

    def save_report(self):

        report_text = self.generate_report()

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        filename = (
            f"security_report_{timestamp}.txt"
        )

        filepath = (
            self.report_directory / filename
        )

        try:

            with open(
                filepath,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(report_text)

            print(
                f"📄 Security report saved: {filepath}"
            )

            return filepath

        except OSError as error:

            print(
                f"Report save error: {error}"
            )

            return None