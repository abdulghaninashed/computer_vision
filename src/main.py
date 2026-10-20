import threading
import webbrowser

from tracking import VehicleTracker
from webapp import create_app


def main():

    tracker = VehicleTracker(center_line_ratio=0.5)
    app = create_app(tracker)
    url = "http://127.0.0.1:5000"

    threading.Timer(1, webbrowser.open, args=(url,)).start()
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)


if __name__ == "__main__":
    main()
    