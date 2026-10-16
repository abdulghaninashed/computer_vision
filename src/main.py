from tracking import VehicleTracker
from gui import TrafficGUI


def main():

    tracker = VehicleTracker(center_line_ratio=0.5)

    def start_tracking(video_path, on_frame, stop_event, center_line_ratio):
        tracker.center_line_ratio = center_line_ratio
        tracker.track(
            video_path,
            on_frame,
            stop_event
        )

    gui = TrafficGUI(
        on_start=start_tracking
    )

    gui.run()


if __name__ == "__main__":
    main()
