from ultralytics import YOLO


class VehicleTracker:

    def __init__(self):
        self.model = YOLO("yolo11n.pt")

    def track(self, source):
        return self.model.track(
            source=source,
            persist=True,
            tracker="bytetrack.yaml",
            conf=0.3,
            imgsz=1280,
            save=True
        )

        for r in results:
            boxes = r.boxes

            for box in boxes:
                print("Class:", int(box.cls))
                print("Confidence:", float(box.conf))

            if box.id is not None:
                print("Track ID:", int(box.id))

            print("Box:", box.xyxy)
            print("----------------")

        return results
