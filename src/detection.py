from ultralytics import YOLO


class VehicleDetector:

    def __init__(self):
        self.model = YOLO("yolo11n.pt")

    def detect(self, source):
        return self.model.predict(
            source=source,
            save=True
        )
