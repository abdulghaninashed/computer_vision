import json
import logging
import os
import queue
import threading
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from dotenv import load_dotenv


# .env.example is only a template. Copy it to the project-root .env file;
# load_dotenv does not load the example file or rename it automatically.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


LOGGER = logging.getLogger(__name__)
BOT_SETTINGS = {
    "GOING": ("TELEGRAM_GOING_BOT_TOKEN", "TELEGRAM_GOING_CHAT_ID", "ذهاب"),
    "RETURNING": (
        "TELEGRAM_RETURNING_BOT_TOKEN",
        "TELEGRAM_RETURNING_CHAT_ID",
        "إياب",
    ),
}
VIOLATION_LABELS = {
    "speeding_car": "سيارة مسرعة",
    "motorcycle": "دراجة نارية",
}


class PoliceTelegramNotifier:
    def __init__(self):
        self._messages = queue.Queue()
        self._worker = None
        self._worker_lock = threading.Lock()
        self._reported_configuration_errors = set()

    def send_violation(self, direction, violation, speed_px_per_second=None):
        if direction not in BOT_SETTINGS:
            raise ValueError(f"Unsupported traffic direction: {direction}")
        if violation not in VIOLATION_LABELS:
            raise ValueError(f"Unsupported violation type: {violation}")

        token_variable, chat_variable, direction_label = BOT_SETTINGS[direction]
        token = os.environ.get(token_variable)
        chat_id = os.environ.get(chat_variable)
        if not token or not chat_id:
            if direction not in self._reported_configuration_errors:
                LOGGER.error(
                    "Telegram notifications for %s are disabled; configure %s and %s.",
                    direction_label,
                    token_variable,
                    chat_variable,
                )
                self._reported_configuration_errors.add(direction)
            return False

        message = (
            "تنبيه مخالفة مرورية\n"
            f"المخالفة: {VIOLATION_LABELS[violation]}\n"
            f"الاتجاه: {direction_label}"
        )
        if speed_px_per_second is not None:
            message += f"\nالسرعة التقديرية: {speed_px_per_second:.0f} بكسل/ثانية"

        self._ensure_worker()
        self._messages.put((direction, token, chat_id, message))
        return True

    def _ensure_worker(self):
        with self._worker_lock:
            if self._worker is None or not self._worker.is_alive():
                self._worker = threading.Thread(
                    target=self._send_messages,
                    name="telegram-police-notifier",
                    daemon=True,
                )
                self._worker.start()

    def _send_messages(self):
        while True:
            direction, token, chat_id, message = self._messages.get()
            try:
                self._send_message(direction, token, chat_id, message)
            finally:
                self._messages.task_done()

    @staticmethod
    def _send_message(direction, token, chat_id, message):
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        body = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": message,
        }).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
            if not isinstance(result, dict) or not result.get("ok"):
                LOGGER.error(
                    "Telegram rejected a %s violation notification.",
                    direction,
                )
        except (
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
            UnicodeDecodeError,
            OSError,
        ) as error:
            LOGGER.error(
                "Could not deliver a %s violation notification to Telegram "
                "(%s).",
                direction,
                type(error).__name__,
            )
