from ultralytics import YOLO


class VehicleTracker:

    def __init__(self):

        self.model = YOLO("models/yolo11n.pt")

    def track(self, source, on_frame=None):
        results = self.model.track(
            source=source,
            persist=True,
            tracker="bytetrack.yaml",
            conf=0.15,
            imgsz=640,
            stream=True,
            verbose=False
        )

        for r in results:

            # الصورة الأصلية بعد معالجة YOLO
            annotated_frame = r.plot()

            # إرسال الفريم إلى GUI
            if on_frame:
                on_frame(annotated_frame)
