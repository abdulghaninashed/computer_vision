from tracking import VehicleTracker
from gui import TrafficGUI


def main():

    tracker = VehicleTracker()

    def start_tracking(video_path):
        tracker.track(video_path)

    # The connection between the GUI and the tracking function
    gui = TrafficGUI(
        on_start=start_tracking
    )

    gui.run()


if __name__ == "__main__":
    main()
