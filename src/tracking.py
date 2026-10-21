import math

import cv2
from ultralytics import YOLO

from send_to_police import PoliceTelegramNotifier


VEHICLE_PRICES = {
    "car": 1.0,
    "van": 1.5,
    "truck": 2.5,
    "bus": 2.0,
}

FAST_SPEED_FRAME_RATIO = 0.4


class VehicleTracker:

    def __init__(self, center_line_ratio=0.5):

        if not 0.0 <= center_line_ratio <= 1.0:
            raise ValueError("center_line_ratio must be between 0.0 and 1.0")

        self.model = YOLO("models/best(9).pt")
        self.center_line_ratio = center_line_ratio

        # Track IDs that already crossed the counting line
        self.counted_ids = set()

        # Previous position of every tracked vehicle
        self.previous_positions = {}
        self.vehicle_speeds = {}
        self.reported_violations = set()
        self.police_notifier = PoliceTelegramNotifier()

        # Total vehicles
        self.total_count = 0

        # Counts for vehicle types included in the revenue report
        self.vehicle_counts = dict.fromkeys(VEHICLE_PRICES, 0)

        # Count by direction
        self.going_count = 0
        self.returning_count = 0

    def track(self, source, on_frame=None, stop_event=None, resume_event=None):

        if stop_event is not None and stop_event.is_set():
            return

        video = cv2.VideoCapture(source)
        fps = video.get(cv2.CAP_PROP_FPS)
        video.release()
        if not math.isfinite(fps) or fps <= 0:
            fps = None

        results = self.model.track(
            source=source,
            persist=True,
            tracker="bytetrack.yaml",
            conf=0.40,
            imgsz=640,
            stream=True,
            verbose=False
        )

        result_iterator = iter(results)
        while stop_event is None or not stop_event.is_set():
            if resume_event is not None:
                resume_event.wait()

            if stop_event is not None and stop_event.is_set():
                break

            try:
                r = next(result_iterator)
            except StopIteration:
                break

            if stop_event is not None and stop_event.is_set():
                break

            frame = r.orig_img

            height, width = frame.shape[:2]

            # =====================================
            # Counting line
            # 25% from bottom
            # =====================================

            counting_line_y = int(height * 0.75)

            # =====================================
            # Center line
            # Separates going / returning
            # =====================================

            center_line_x = int(width * self.center_line_ratio)

            # =====================================
            # Process detected objects
            # =====================================

            if r.boxes.id is not None:

                for box in r.boxes:

                    track_id = int(box.id)

                    class_id = int(box.cls)

                    class_name = self.model.names[class_id]

                    # Bounding box
                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0]
                    )

                    # Bottom-center point
                    center_x = int((x1 + x2) / 2)
                    bottom_y = y2
                    current_position = (center_x, bottom_y)

                    # =================================
                    # Check previous position
                    # =================================

                    if track_id in self.previous_positions:

                        previous_x, previous_y = self.previous_positions[track_id]

                        if fps is not None:
                            distance = math.hypot(
                                center_x - previous_x,
                                bottom_y - previous_y
                            )
                            self.vehicle_speeds[track_id] = distance * fps

                    speed = self.vehicle_speeds.get(track_id)
                    is_motorcycle = (
                        "motorcycle" in str(class_name).lower()
                        or "motorsycle" in str(class_name).lower()
                    )
                    is_speeding_car = (
                        str(class_name).lower() == "car"
                        and speed is not None
                        and speed >= width * FAST_SPEED_FRAME_RATIO
                    )
                    direction = (
                        "GOING" if center_x < center_line_x else "RETURNING"
                    )

                    motorcycle_violation = (track_id, "motorcycle")
                    if (
                        is_motorcycle
                        and motorcycle_violation not in self.reported_violations
                    ):
                        self.reported_violations.add(motorcycle_violation)
                        self.police_notifier.send_violation(direction, "motorcycle")

                    speeding_violation = (track_id, "speeding_car")
                    if (
                        is_speeding_car
                        and speeding_violation not in self.reported_violations
                    ):
                        self.reported_violations.add(speeding_violation)
                        self.police_notifier.send_violation(
                            direction,
                            "speeding_car",
                            speed_px_per_second=speed,
                        )

                    # =================================
                    # Vehicle crossed counting line
                    # =================================

                    if track_id in self.previous_positions:
                        crossed_line = (
                            (previous_y < counting_line_y <= bottom_y)
                            or
                            (previous_y > counting_line_y >= bottom_y)
                        )

                        if crossed_line and track_id not in self.counted_ids:
                            self.counted_ids.add(track_id)
                            self.total_count += 1
                            if class_name in self.vehicle_counts:
                                self.vehicle_counts[class_name] += 1

                            if center_x < center_line_x:
                                self.going_count += 1
                                direction = "GOING"
                            else:
                                self.returning_count += 1
                                direction = "RETURNING"

                            print(
                                f"Vehicle {track_id} crossed | "
                                f"Class: {class_name} | "
                                f"Direction: {direction}"
                            )

                    # Save current position
                    self.previous_positions[track_id] = current_position

            # =====================================
            # Draw YOLO boxes
            # =====================================

            annotated_frame = r.plot()

            for box in r.boxes:
                class_name = str(self.model.names[int(box.cls)]).lower()
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                track_id = int(box.id) if box.id is not None else None
                speed = self.vehicle_speeds.get(
                    track_id) if track_id is not None else None
                is_motorcycle = (
                    "motorcycle" in class_name or "motorsycle" in class_name
                )
                is_fast = speed is not None and speed >= width * FAST_SPEED_FRAME_RATIO

                if is_motorcycle or is_fast:
                    cv2.rectangle(
                        annotated_frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 255),
                        3
                    )

                if speed is not None:
                    label = f"{speed:.0f} px/s"
                    cv2.putText(
                        annotated_frame,
                        label,
                        (x1, min(y2 + 20, height - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255) if is_motorcycle or is_fast else (
                            255, 255, 255),
                        2,
                        cv2.LINE_AA
                    )

            # =====================================
            # Draw counting line
            # =====================================

            cv2.line(
                annotated_frame,
                (0, counting_line_y),
                (width, counting_line_y),
                (255, 255, 0),
                3
            )

            # =====================================
            # Draw center line
            # =====================================

            cv2.line(
                annotated_frame,
                (center_line_x, 0),
                (center_line_x, height),
                (0, 255, 255),
                3
            )

            # =====================================
            # Send statistics to GUI
            # =====================================

            stats = {
                "total": self.total_count,
                "going": self.going_count,
                "returning": self.returning_count,
                "vehicle_counts": self.vehicle_counts.copy(),
            }

            if on_frame:

                on_frame(
                    annotated_frame,
                    stats
                )
