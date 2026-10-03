import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk


class TrafficGUI:

    def __init__(self, on_start):

        self.video_path = None
        self.on_start = on_start

        self.root = ctk.CTk()

        self.root.title("Traffic Monitoring System")
        self.root.geometry("1000x700")

        # Title
        title = tk.Label(
            self.root,
            text="Traffic Monitoring System",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Video area
        self.video_area = tk.Label(
            self.root,
            text="Video Preview",
            font=("Arial", 20),
            bg="black",
            fg="white"
        )
        self.video_area.pack(
            padx=20,
            pady=20,
            fill="both",
            expand=True
        )

        # Buttons frame
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=10)

        # Select video
        select_button = tk.Button(
            buttons_frame,
            text="Select Video",
            font=("Arial", 14),
            command=self.select_video
        )
        select_button.pack(side="left", padx=10)

        # Start
        start_button = tk.Button(
            buttons_frame,
            text="Start",
            font=("Arial", 14),
            command=self.start
        )
        start_button.pack(side="left", padx=10)

        # Stop
        stop_button = tk.Button(
            buttons_frame,
            text="Stop",
            font=("Arial", 14),
            command=self.stop
        )
        stop_button.pack(side="left", padx=10)

    def select_video(self):

        self.video_path = filedialog.askopenfilename(
            title="Select Traffic Video",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*")
            ]
        )

        if self.video_path:

            self.video_area.config(
                text=f"Selected:\n{self.video_path}"
            )

    def start(self):

        if self.video_path:
            self.on_start(self.video_path)
        else:
            print("Please select a video first")

    def stop(self):
        print("Stop pressed")

    def run(self):
        self.root.mainloop()
