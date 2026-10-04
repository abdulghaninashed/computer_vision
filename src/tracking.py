from ultralytics import YOLO


class VehicleTracker:

    def __init__(self):

        self.model = YOLO("models/yolo11n.pt")

        # Track IDs that already crossed the counting line
        self.counted_ids = set()

        # Previous position of every tracked vehicle
        self.previous_positions = {}

        # Total vehicles
        self.total_count = 0

        # Count by direction
        self.going_count = 0
        self.returning_count = 0

    def track(self, source, on_frame=None):

        results = self.model.track(
            source=source,
            persist=True,
            tracker="bytetrack.yaml",
            conf=0.3,
            imgsz=640,
            stream=True,
            verbose=False
        )

        for r in results:

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

            center_line_x = int(width * 0.50)

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

                    # =================================
                    # Check previous position
                    # =================================

                    if track_id in self.previous_positions:

                        previous_y = self.previous_positions[track_id]

                        # =================================
                        # Vehicle crossed counting line
                        # =================================

                        crossed_line = (
                            (previous_y < counting_line_y <= bottom_y)
                            or
                            (previous_y > counting_line_y >= bottom_y)
                        )

                        if crossed_line and track_id not in self.counted_ids:

                            # Mark as counted
                            self.counted_ids.add(track_id)

                            self.total_count += 1

                            # =================================
                            # Determine direction
                            # =================================

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
                    self.previous_positions[track_id] = bottom_y

            # =====================================
            # Draw YOLO boxes
            # =====================================

            annotated_frame = r.plot()

            # =====================================
            # Draw counting line
            # =====================================

            import cv2

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
                "returning": self.returning_count
            }

            if on_frame:

                on_frame(
                    annotated_frame,
                    stats
                )
