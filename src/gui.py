import customtkinter as ctk
from tkinter import filedialog
import threading

from PIL import Image


class TrafficGUI:

    def __init__(self, on_start):

        self.video_path = None
        self.on_start = on_start
        self.running = False

        # Main Window
        self.root = ctk.CTk()

        self.root.title("Traffic Monitoring System")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        # =========================
        # Header
        # =========================
        self.header = ctk.CTkFrame(
            self.root,
            corner_radius=15
        )

        self.header.pack(
            fill="x",
            padx=20,
            pady=(20, 10)
        )

        self.title = ctk.CTkLabel(
            self.header,
            text="TRAFFIC MONITORING SYSTEM",
            font=("Arial", 26, "bold")
        )

        self.title.pack(
            side="left",
            padx=20,
            pady=15
        )

        self.status = ctk.CTkLabel(
            self.header,
            text="● OFFLINE",
            text_color="red",
            font=("Arial", 16, "bold")
        )

        self.status.pack(
            side="right",
            padx=20
        )

        # =========================
        # Main Content
        # =========================

        self.content = ctk.CTkFrame(
            self.root,
            corner_radius=15
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # =========================
        # Video Area
        # =========================

        self.video_frame = ctk.CTkFrame(
            self.content,
            corner_radius=15
        )

        self.video_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.video_title = ctk.CTkLabel(
            self.video_frame,
            text="VIDEO PREVIEW",
            font=("Arial", 20, "bold")
        )

        self.video_title.pack(pady=15)

        self.video_area = ctk.CTkLabel(
            self.video_frame,
            text="No video selected",
            font=("Arial", 22)
        )

        self.video_area.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # =========================
        # Statistics Panel
        # =========================

        self.stats_frame = ctk.CTkFrame(
            self.content,
            width=280,
            corner_radius=15
        )

        self.stats_frame.pack(
            side="right",
            fill="y",
            padx=10,
            pady=10
        )

        self.stats_frame.pack_propagate(False)

        self.stats_title = ctk.CTkLabel(
            self.stats_frame,
            text="LIVE STATISTICS",
            font=("Arial", 19, "bold")
        )

        self.stats_title.pack(pady=20)

        self.create_stat("Cars", "0")
        self.create_stat("Vans", "0")
        self.create_stat("Buses", "0")
        self.create_stat("Trucks", "0")
        self.create_stat("Motorcycles", "0")

        # =========================
        # Total Vehicles
        # =========================

        self.total_label = ctk.CTkLabel(
            self.stats_frame,
            text="TOTAL VEHICLES\n0",
            font=("Arial", 19, "bold")
        )

        self.total_label.pack(pady=20)

        # =========================
        # Going
        # =========================

        self.going_label = ctk.CTkLabel(
            self.stats_frame,
            text="GOING\n0",
            font=("Arial", 17, "bold")
        )

        self.going_label.pack(pady=10)

        # =========================
        # Returning
        # =========================

        self.returning_label = ctk.CTkLabel(
            self.stats_frame,
            text="RETURNING\n0",
            font=("Arial", 17, "bold")
        )

        self.returning_label.pack(pady=10)

        # =========================
        # Revenue
        # =========================

        self.revenue_label = ctk.CTkLabel(
            self.stats_frame,
            text="REVENUE\n$0.00",
            font=("Arial", 19, "bold")
        )

        self.revenue_label.pack(pady=15)

        # =========================
        # Control Area
        # =========================

        self.controls = ctk.CTkFrame(
            self.root,
            corner_radius=15
        )

        self.controls.pack(
            fill="x",
            padx=20,
            pady=(10, 20)
        )

        # =========================
        # Select Video
        # =========================

        self.select_button = ctk.CTkButton(
            self.controls,
            text="Select Video",
            width=150,
            height=40,
            command=self.select_video
        )

        self.select_button.pack(
            side="left",
            padx=10,
            pady=15
        )

        # =========================
        # Start
        # =========================

        self.start_button = ctk.CTkButton(
            self.controls,
            text="▶  START",
            width=150,
            height=40,
            command=self.start
        )

        self.start_button.pack(
            side="left",
            padx=10
        )

        # =========================
        # Stop
        # =========================

        self.stop_button = ctk.CTkButton(
            self.controls,
            text="■  STOP",
            width=150,
            height=40,
            command=self.stop,
            state="disabled"
        )

        self.stop_button.pack(
            side="left",
            padx=10
        )

        # =========================
        # Processing Status
        # =========================

        self.progress_label = ctk.CTkLabel(
            self.controls,
            text="",
            font=("Arial", 14)
        )

        self.progress_label.pack(
            side="right",
            padx=20
        )

    # =====================================================
    # Statistics
    # =====================================================

    def create_stat(self, name, value):

        label = ctk.CTkLabel(
            self.stats_frame,
            text=f"{name}:  {value}",
            font=("Arial", 16)
        )

        label.pack(
            anchor="w",
            padx=30,
            pady=7
        )

    # =====================================================
    # Select Video
    # =====================================================

    def select_video(self):

        self.video_path = filedialog.askopenfilename(
            title="Select Traffic Video",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*")
            ]
        )

        if self.video_path:

            self.video_area.configure(
                text=f"Selected:\n{self.video_path}",
                image=None
            )

            self.status.configure(
                text="● READY",
                text_color="orange"
            )

    # =====================================================
    # Start
    # =====================================================

    def start(self):

        if not self.video_path:

            self.status.configure(
                text="● NO VIDEO",
                text_color="red"
            )

            self.progress_label.configure(
                text="Select a video first"
            )

            return

        if self.running:
            return

        self.running = True

        self.status.configure(
            text="● RUNNING",
            text_color="green"
        )

        self.progress_label.configure(
            text="Processing..."
        )

        self.select_button.configure(
            state="disabled"
        )

        self.start_button.configure(
            state="disabled"
        )

        self.stop_button.configure(
            state="normal"
        )

        # تشغيل YOLO في Thread منفصل
        thread = threading.Thread(
            target=self.run_tracking,
            daemon=True
        )

        thread.start()

    # =====================================================
    # Run Tracking
    # =====================================================

    def run_tracking(self):

        try:

            self.on_start(
                self.video_path,
                self.update_frame
            )

            self.root.after(
                0,
                self.processing_done
            )

        except Exception as e:

            error_message = str(e)

            self.root.after(
                0,
                lambda: self.processing_error(error_message)
            )

    # =====================================================
    # Receive Frame From YOLO
    # =====================================================

    def update_frame(self, frame, stats):

        # لأن YOLO يعمل في Thread منفصل،
        # لا نعدل GUI مباشرة.

        self.root.after(
            0,
            lambda: self.display_frame(frame, stats)
        )

    # =====================================================
    # Display Frame
    # =====================================================

    def display_frame(self, frame, stats):

        # =========================
        # Update Statistics
        # =========================

        self.total_label.configure(
            text=f"TOTAL VEHICLES\n{stats['total']}"
        )

        self.going_label.configure(
            text=f"GOING\n{stats['going']}"
        )

        self.returning_label.configure(
            text=f"RETURNING\n{stats['returning']}"
        )

        # =========================
        # Convert BGR → RGB
        # =========================

        frame_rgb = frame[:, :, ::-1]

        image = Image.fromarray(frame_rgb)

        # =========================
        # Video Area Size
        # =========================

        width = self.video_area.winfo_width()
        height = self.video_area.winfo_height()

        if width <= 1 or height <= 1:

            width = 800
            height = 500

        # =========================
        # Keep Aspect Ratio
        # =========================

        image.thumbnail(
            (width, height),
            Image.Resampling.LANCZOS
        )

        # =========================
        # Create CTk Image
        # =========================

        self.video_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size
        )

        # =========================
        # Display Frame
        # =========================

        self.video_area.configure(
            image=self.video_image,
            text=""
        )

    # =====================================================
    # Processing Done
    # =====================================================

    def processing_done(self):

        self.running = False

        self.status.configure(
            text="● DONE ✓",
            text_color="green"
        )

        self.progress_label.configure(
            text="Processing completed"
        )

        self.start_button.configure(
            state="normal"
        )

        self.select_button.configure(
            state="normal"
        )

        self.stop_button.configure(
            state="disabled"
        )

    # =====================================================
    # Processing Error
    # =====================================================

    def processing_error(self, error):

        self.running = False

        self.status.configure(
            text="● ERROR",
            text_color="red"
        )

        self.progress_label.configure(
            text="Processing failed"
        )

        print("Error:", error)

        self.start_button.configure(
            state="normal"
        )

        self.select_button.configure(
            state="normal"
        )

        self.stop_button.configure(
            state="disabled"
        )

    # =====================================================
    # Stop
    # =====================================================

    def stop(self):

        self.running = False

        self.status.configure(
            text="● STOPPED",
            text_color="red"
        )

        self.progress_label.configure(
            text="Stopped"
        )

    # =====================================================
    # Run GUI
    # =====================================================

    def run(self):

        self.root.mainloop()
