import requests


class TelegramAlert:

    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

        self.url = (
            f"https://api.telegram.org/"
            f"bot{self.bot_token}/sendPhoto"
        )

    def send_alert(self, photo_path, message):

        try:

            with open(photo_path, "rb") as photo:

                response = requests.post(
                    self.url,
                    data={
                        "chat_id": self.chat_id,
                        "caption": message
                    },
                    files={
                        "photo": photo
                    },
                    timeout=15
                )

            if response.ok:

                print(
                    "Telegram alert sent successfully."
                )

                return True

            print(
                "Telegram error:",
                response.text
            )

            return False

        except Exception as error:

            print(
                f"Telegram alert error: {error}"
            )

            return False