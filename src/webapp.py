import os
import tempfile
import threading
from pathlib import Path

import cv2
from flask import Flask, Response, jsonify, render_template, request
from werkzeug.utils import secure_filename

from tracking import VEHICLE_PRICES


ALLOWED_VIDEO_EXTENSIONS = {".avi", ".mkv", ".mov", ".mp4"}


def _empty_stats():
    return {
        "total": 0,
        "going": 0,
        "returning": 0,
        "vehicle_counts": dict.fromkeys(VEHICLE_PRICES, 0),
    }


def _build_report(stats):
    counts = stats["vehicle_counts"]
    rows = [
        {
            "vehicle": vehicle,
            "count": counts.get(vehicle, 0),
            "unit_price": price,
            "subtotal": round(counts.get(vehicle, 0) * price, 2),
        }
        for vehicle, price in VEHICLE_PRICES.items()
    ]
    return {
        "rows": rows,
        "total_count": stats["total"],
        "total_revenue": round(sum(row["subtotal"] for row in rows), 2),
    }


class TrackingWebApp:

    def __init__(self, tracker):
        self.tracker = tracker
        self.condition = threading.Condition()
        self.stop_event = threading.Event()
        self.resume_event = threading.Event()
        self.resume_event.set()
        self.frame_sequence = 0
        self.latest_frame = None
        self.state = {
            "status": "ready",
            "running": False,
            "stats": _empty_stats(),
            "error": None,
            "center_line_percent": 50,
        }

    def start(self, video_path, center_line_percent):
        with self.condition:
            if self.state["running"]:
                return False

            self.stop_event.clear()
            self.resume_event.set()
            self.frame_sequence = 0
            self.latest_frame = None
            self.state.update({
                "status": "processing",
                "running": True,
                "stats": _empty_stats(),
                "error": None,
                "center_line_percent": center_line_percent,
            })

        worker = threading.Thread(
            target=self._track_video,
            args=(video_path, center_line_percent),
            daemon=True
        )
        worker.start()
        return True

    def _track_video(self, video_path, center_line_percent):
        try:
            self.tracker.center_line_ratio = center_line_percent / 100
            self.tracker.counted_ids.clear()
            self.tracker.previous_positions.clear()
            self.tracker.vehicle_speeds.clear()
            self.tracker.reported_violations.clear()
            self.tracker.total_count = 0
            self.tracker.going_count = 0
            self.tracker.returning_count = 0
            self.tracker.vehicle_counts = dict.fromkeys(VEHICLE_PRICES, 0)

            self.tracker.track(
                video_path,
                on_frame=self._on_frame,
                stop_event=self.stop_event,
                resume_event=self.resume_event,
            )

            status = "stopped" if self.stop_event.is_set() else "completed"
            with self.condition:
                self.state["status"] = status
        except Exception as error:
            with self.condition:
                self.state.update({
                    "status": "error",
                    "error": str(error),
                })
        finally:
            with self.condition:
                self.state["running"] = False
                self.condition.notify_all()
            try:
                os.remove(video_path)
            except OSError as error:
                with self.condition:
                    self.state["error"] = (
                        f"{self.state['error']}; " if self.state["error"] else ""
                    ) + f"Could not remove uploaded video: {error}"

    def _on_frame(self, frame, stats):
        encoded_ok, encoded = cv2.imencode(".jpg", frame)
        if not encoded_ok:
            raise RuntimeError("Could not encode the processed video frame.")

        with self.condition:
            self.latest_frame = encoded.tobytes()
            self.frame_sequence += 1
            self.state["stats"] = stats
            self.condition.notify_all()

    def stop(self):
        with self.condition:
            if not self.state["running"]:
                return False
            self.state["status"] = "stopping"
            self.stop_event.set()
            self.resume_event.set()
            self.condition.notify_all()
            return True

    def toggle_pause(self):
        with self.condition:
            if not self.state["running"] or self.state["status"] not in {
                "processing",
                "paused",
            }:
                return None

            if self.state["status"] == "paused":
                self.resume_event.set()
                self.state["status"] = "processing"
                paused = False
            else:
                self.resume_event.clear()
                self.state["status"] = "paused"
                paused = True

            self.condition.notify_all()
            return paused

    def video_stream(self):
        last_sequence = 0
        while True:
            with self.condition:
                while self.frame_sequence <= last_sequence:
                    if not self.state["running"] and self.state["status"] != "ready":
                        return
                    self.condition.wait()
                last_sequence = self.frame_sequence
                frame = self.latest_frame

            if frame is not None:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame
                    + b"\r\n"
                )


def create_app(tracker):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    tracking = TrackingWebApp(tracker)
    app.extensions["tracking"] = tracking

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/state")
    def get_state():
        with tracking.condition:
            return jsonify(tracking.state.copy())

    @app.get("/api/report")
    def get_report():
        with tracking.condition:
            report = _build_report(tracking.state["stats"])
        return jsonify(report)

    @app.post("/api/reset")
    def reset_counts():
        with tracking.condition:
            if tracking.state["running"]:
                return jsonify({"error": "Stop video processing before resetting counts."}), 409

            tracking.state["stats"] = _empty_stats()
            tracking.tracker.total_count = 0
            tracking.tracker.going_count = 0
            tracking.tracker.returning_count = 0
            tracking.tracker.vehicle_counts = dict.fromkeys(VEHICLE_PRICES, 0)
            tracking.tracker.counted_ids.clear()
            tracking.tracker.previous_positions.clear()
            tracking.tracker.vehicle_speeds.clear()
            tracking.tracker.reported_violations.clear()
            tracking.condition.notify_all()

        return jsonify({"status": "reset"})

    @app.post("/api/start")
    def start_tracking():
        upload = request.files.get("video")
        if upload is None or not upload.filename:
            return jsonify({"error": "Choose a video file first."}), 400

        safe_name = secure_filename(upload.filename)
        extension = Path(safe_name).suffix.lower()
        if extension not in ALLOWED_VIDEO_EXTENSIONS:
            return jsonify({
                "error": "Choose an MP4, AVI, MOV, or MKV video."
            }), 400

        try:
            center_line_percent = float(
                request.form.get("center_line_percent", "50")
            )
        except ValueError:
            return jsonify({"error": "Center-line position must be a number."}), 400

        if not 0 <= center_line_percent <= 100:
            return jsonify({
                "error": "Center-line position must be between 0 and 100."
            }), 400

        temporary_file = tempfile.NamedTemporaryFile(
            prefix="traffic-video-",
            suffix=extension,
            delete=False
        )
        video_path = temporary_file.name
        temporary_file.close()
        upload.save(video_path)

        if not tracking.start(video_path, center_line_percent):
            os.remove(video_path)
            return jsonify({"error": "Video processing is already running."}), 409

        return jsonify({"status": "processing"}), 202

    @app.post("/api/stop")
    def stop_tracking():
        if not tracking.stop():
            return jsonify({"error": "No video is currently being processed."}), 409

        with tracking.condition:
            report = _build_report(tracking.state["stats"])

        return jsonify({"status": "stopped", "report": report})

    @app.post("/api/pause")
    def toggle_pause():
        paused = tracking.toggle_pause()
        if paused is None:
            return jsonify({"error": "Video processing cannot be paused right now."}), 409
        return jsonify({"status": "paused" if paused else "processing"})

    @app.get("/video_feed")
    def video_feed():
        return Response(
            tracking.video_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
            headers={"Cache-Control": "no-cache"}
        )

    return app
