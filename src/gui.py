import os
import io
import base64
import threading
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

# =========================================================
# دعم اللغة العربية (تشكيل الحروف + اتجاه من اليمين لليسار)
# pip install arabic-reshaper python-bidi
# =========================================================

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC = True
except ImportError:
    HAS_ARABIC = False
    print(
        "تنبيه: لعرض العربية بشكل صحيح ثبّت المكتبتين:\n"
        "pip install arabic-reshaper python-bidi"
    )


def ar(text):
    """
    يجهّز النص العربي للعرض في Tkinter:
    يوصل الحروف ثم يعكس الترتيب البصري.
    يعمل سطراً سطراً ويترك الأسطر الإنجليزية كما هي.
    """

    if not HAS_ARABIC:
        return text

    lines = []

    for line in text.split("\n"):

        if any("\u0600" <= ch <= "\u06FF" for ch in line):
            line = get_display(arabic_reshaper.reshape(line))

        lines.append(line)

    return "\n".join(lines)


# =========================================================
# Font
# غيّر FONT_FAMILY إلى اسم الخط الذي تريده (مثل "Cairo" أو "Tajawal").
# طريقتان لتوفير الخط:
#  1) ثبّته في النظام (ملف .ttf ثم Install)
#  2) ضع ملفات .ttf داخل مجلد اسمه fonts بجانب هذا الملف
#     وسيُحمَّل تلقائياً.
# إن لم يوجد الخط يستخدم النظام خطاً بديلاً.
# =========================================================
FONT_FAMILY = "changa"  # غيّر هذا إلى اسم الخط الذي تريده

_FONTS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fonts"
)

if os.path.isdir(_FONTS_DIR):

    for _name in os.listdir(_FONTS_DIR):

        if _name.lower().endswith((".ttf", ".otf")):

            try:
                ctk.FontManager.load_font(
                    os.path.join(_FONTS_DIR, _name)
                )
            except Exception as e:
                print("Font load failed:", _name, e)

# =========================================================
# Color Palette
# =========================================================

WHITE = "#FFFFFF"          # البطاقات
BG = "#EEF2F9"             # الخلفية العامة
PANEL_BG = "#EAEFF8"       # خلفية اللوحات الداخلية
VIDEO_BG = "#DDE3F0"       # خلفية منطقة الفيديو
BORDER = "#D5DDEE"         # الإطارات الرفيعة

NAVY = "#0F2557"           # الأزرار الداكنة / بطاقة الإجمالي
NAVY_HOVER = "#1B3A80"
TEAL = "#3AA9C9"           # START / بطاقة العائدات
TEAL_HOVER = "#2D93B1"
BLUE = "#2A5298"           # نص الذهاب
PURPLE = "#6B3FA0"         # العناوين / نص الإياب

TEXT = "#14213D"           # نص داكن
SUBTEXT = "#3B4A6B"        # نص فرعي
MUTED = "#6B7280"          # نص خافت
DISABLED = "#A9AECF"       # نص الأزرار المعطلة
DANGER = "#C0392B"         # للتوقف / الأخطاء / OFFLINE
SUCCESS = "#2E9E4F"        # اكتمال المعالجة


# =========================================================
# Logo
# الشعار مضمَّن داخل الكود. إن وضعت ملف logo.png بجانب
# هذا الملف فسيُستخدم بدلاً من المضمَّن (لجودة أعلى).
# =========================================================

LOGO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logo.png"
)

LOGO_B64 = """
iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAB/lBMVEXv4NPg07Tj0rKmjGny6NHOt5zu5M60n4bKtZzi1LP37dzE
rpfm16qtlmypjmq9qIy4pId/fwCYWiigk2m6qIt/AABsSSe/fz+WdUc/Pz+ZZmb/AP//f//Msn/lrn/QuqEAAADo1rL258nQt46T
Z0mKVzV2Ryupd1KxiGm1lnDbyqbYxJjOqIn89NTnyqiXdU+RZTnHmHWshVhrNhrIpnlvOiPx47qDSy16VTGLXEP//v6ibEvw3MLd
0axlKxTkt5aofGS7o3Xjx5u6pIeYeGS3moNaJw7+9+XHnIPUu6NxRRrDi2t6WUSag1Kcg2mhajqqqqr9+en9/O9/f3/MsXxcNRT/
/7W/v7//f3+xl3ORcT2qqlX/+u2rkV3hrY3//39cNyZ8Y0qCTBv//wDpvqO/f3+ylnSncTzCqo/j1bdTHQaulnK/v3/88bz69d3+
+/CymXf/qqrz583++O1+YTm1mHTHrJHayqz/AAD/v7/x59Hy5tJ/fz+qVVXTupvVxpwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADHzVpgAAAAgHRSTlMXI5qcrJ7YmitYblDkZtQr5QL/EWQC/wSqBAUBAgr/2AD+/v7+
/v7+/v7+/v7+/v7+/v7+/v/+//7/A//+/v////7+/f7+//v//v7//v/9/wOvMgL+/gMEArD/A0r//wL///8B/wTV/7Cv/zIE/oiL
RwMy0v6PMFABBEaMBAPRrkAQmYIAAB1JSURBVHjatVsHm9tGkqWCkxw33O7lI3IDBJEIgmCYYZ4hJ0myghWsZMlyOOdsr3f91++9
apDDkWRL9vrwSaMRNWK/rnpV9aq6Wav/iuf+hUv/It988/Kr18+ciavHi//1X8+8+tn/yj/94a837/+a96w9+4/e/FHW/vNz1x/6
vq+ykw9eenj9jEbx483fH8ClC/zhl79+qBSWln2ffAhCAdZrX3/2X0R76XcFcAFb6n125jUsrpfyCOFGsn5i/Mo0BljizKv/Dgg3
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
"""


def load_logo():

    if os.path.exists(LOGO_PATH):
        return Image.open(LOGO_PATH).convert("RGBA")

    data = base64.b64decode(LOGO_B64)
    return Image.open(io.BytesIO(data)).convert("RGBA")


class TrafficGUI:

    def __init__(self, on_start, on_report=None):

        self.video_path = None
        self.on_start = on_start
        self.on_report = on_report      # اختياري: دالة عرض التقرير
        self.running = False
        self.stop_event = threading.Event()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Main Window
        self.root = ctk.CTk(fg_color=BG)

        # شريط العنوان يعرض العربية بشكل صحيح من النظام نفسه
        self.root.title("برنامج الخوارزمي - Traffic Monitoring System")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)

        # =========================
        # Header
        # =========================
        self.header = ctk.CTkFrame(
            self.root,
            corner_radius=18,
            fg_color=WHITE,
            border_width=1,
            border_color=BORDER
        )

        self.header.pack(
            fill="x",
            padx=20,
            pady=(20, 10)
        )

        # Logo (يمين)
        logo = load_logo()

        self.logo_image = ctk.CTkImage(
            light_image=logo,
            dark_image=logo,
            size=(84, 84)
        )

        self.logo_label = ctk.CTkLabel(
            self.header,
            text="",
            image=self.logo_image
        )

        self.logo_label.pack(
            side="right",
            padx=(0, 15),
            pady=8
        )

        # Title + Subtitle (يمين بجانب الشعار)
        self.title_box = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        self.title_box.pack(
            side="right",
            padx=(0, 12),
            pady=8
        )

        self.title = ctk.CTkLabel(
            self.title_box,
            text=ar("برنامج الخوارزمي"),
            text_color=NAVY,
            font=(FONT_FAMILY, 32, "bold")
        )

        self.title.pack(anchor="e")

        self.subtitle = ctk.CTkLabel(
            self.title_box,
            text=ar("لتحليل واستشعار حركة المرور"),
            text_color=SUBTEXT,
            font=(FONT_FAMILY, 16)
        )

        self.subtitle.pack(anchor="e")

        # Status (يسار)
        self.status = ctk.CTkLabel(
            self.header,
            text="OFFLINE ●",
            text_color=DANGER,
            font=(FONT_FAMILY, 15, "bold")
        )

        self.status.pack(
            side="left",
            padx=30
        )

        # =========================
        # Main Content
        # =========================

        self.content = ctk.CTkFrame(
            self.root,
            corner_radius=18,
            fg_color=WHITE,
            border_width=1,
            border_color=BORDER
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # =========================
        # Statistics Panel (يمين)
        # =========================

        self.stats_frame = ctk.CTkFrame(
            self.content,
            width=280,
            corner_radius=15,
            fg_color=PANEL_BG
        )

        self.stats_frame.pack(
            side="right",
            fill="y",
            padx=(5, 12),
            pady=12
        )

        self.stats_frame.pack_propagate(False)

        self.stats_title = ctk.CTkLabel(
            self.stats_frame,
            text=ar("الإحصائيات المباشرة"),
            text_color=PURPLE,
            font=(FONT_FAMILY, 19, "bold")
        )

        self.stats_title.pack(pady=(18, 10))

        # Total Vehicles
        (self.total_card,
         self.total_label,
         self.total_value) = self.create_stat_card(
            "إجمالي المركبات\nTOTAL VEHICLES",
            fg=NAVY,
            text_color=WHITE,
            border=False
        )

        # Going
        (self.going_card,
         self.going_label,
         self.going_value) = self.create_stat_card(
            "الذهاب\nGOING",
            fg=WHITE,
            text_color=BLUE,
            border=True
        )

        # Returning
        (self.returning_card,
         self.returning_label,
         self.returning_value) = self.create_stat_card(
            "الإياب\nRETURNING",
            fg=WHITE,
            text_color=PURPLE,
            border=True
        )

        # Revenue
        (self.revenue_card,
         self.revenue_label,
         self.revenue_value) = self.create_stat_card(
            "العائدات\nREVENUE",
            fg=TEAL,
            text_color=WHITE,
            border=False
        )

        # =========================
        # Video Area (يسار)
        # =========================

        self.video_frame = ctk.CTkFrame(
            self.content,
            corner_radius=15,
            fg_color=PANEL_BG
        )

        self.video_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(12, 5),
            pady=12
        )

        self.video_title = ctk.CTkLabel(
            self.video_frame,
            text=ar("عرض الفيديو"),
            text_color=PURPLE,
            font=(FONT_FAMILY, 19, "bold")
        )

        self.video_title.pack(pady=(18, 10))

        self.video_area = ctk.CTkLabel(
            self.video_frame,
            text=ar("لم يتم تحديد فيديو\nNo video selected"),
            text_color=MUTED,
            font=(FONT_FAMILY, 18),
            fg_color=VIDEO_BG,
            corner_radius=12
        )

        self.video_area.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18)
        )

        # =========================
        # Control Area
        # =========================

        self.controls = ctk.CTkFrame(
            self.root,
            corner_radius=18,
            fg_color=WHITE,
            border_width=1,
            border_color=BORDER
        )

        self.controls.pack(
            fill="x",
            padx=20,
            pady=(10, 20)
        )

        # Select Video
        self.select_button = ctk.CTkButton(
            self.controls,
            text=ar("Select / اختيار فيديو"),
            width=150,
            height=38,
            corner_radius=8,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            text_color=WHITE,
            text_color_disabled=DISABLED,
            font=(FONT_FAMILY, 13, "bold"),
            command=self.select_video
        )

        self.select_button.pack(
            side="left",
            padx=(12, 8),
            pady=15
        )

        # Start
        self.start_button = ctk.CTkButton(
            self.controls,
            text=ar("▶  START / بدء"),
            width=150,
            height=38,
            corner_radius=8,
            fg_color=TEAL,
            hover_color=TEAL_HOVER,
            text_color=WHITE,
            text_color_disabled=DISABLED,
            font=(FONT_FAMILY, 13, "bold"),
            command=self.start
        )

        self.start_button.pack(
            side="left",
            padx=8
        )

        # Stop
        self.stop_button = ctk.CTkButton(
            self.controls,
            text=ar("إيقاف  ■"),
            width=130,
            height=38,
            corner_radius=8,
            fg_color=WHITE,
            border_width=1,
            border_color=DANGER,
            hover_color="#FDECEC",
            text_color=DANGER,
            text_color_disabled=DISABLED,
            font=(FONT_FAMILY, 13, "bold"),
            command=self.stop,
            state="disabled"
        )

        self.stop_button.pack(
            side="left",
            padx=8
        )

        # View Report
        self.report_button = ctk.CTkButton(
            self.controls,
            text=ar("View Report / عرض التقرير"),
            width=190,
            height=38,
            corner_radius=8,
            fg_color=NAVY,
            hover_color=NAVY_HOVER,
            text_color=WHITE,
            text_color_disabled=DISABLED,
            font=(FONT_FAMILY, 13, "bold"),
            command=self.view_report
        )

        self.report_button.pack(
            side="left",
            padx=8
        )

        # Processing Status
        self.progress_label = ctk.CTkLabel(
            self.controls,
            text="",
            text_color=MUTED,
            font=(FONT_FAMILY, 14)
        )

        self.progress_label.pack(
            side="right",
            padx=20
        )

    # =====================================================
    # Statistics Card
    # =====================================================

    def create_stat_card(self, text, fg, text_color, border):

        card = ctk.CTkFrame(
            self.stats_frame,
            height=64,
            corner_radius=10,
            fg_color=fg,
            border_width=1 if border else 0,
            border_color=BORDER
        )

        card.pack(
            fill="x",
            padx=18,
            pady=7
        )

        card.pack_propagate(False)

        # العنوان (عربي + إنجليزي) في المنتصف
        label = ctk.CTkLabel(
            card,
            text=ar(text),
            text_color=text_color,
            font=(FONT_FAMILY, 15, "bold")
        )

        label.pack(expand=True)

        # القيمة الرقمية على الطرف الأيسر (فارغة في البداية)
        value = ctk.CTkLabel(
            card,
            text="",
            text_color=text_color,
            font=(FONT_FAMILY, 22, "bold")
        )

        value.place(
            relx=0.05,
            rely=0.5,
            anchor="w"
        )

        return card, label, value

    def create_stat(self, name, value):

        label = ctk.CTkLabel(
            self.stats_frame,
            text=f"{name}:  {value}",
            text_color=TEXT,
            font=(FONT_FAMILY, 16)
        )

        label.pack(
            anchor="w",
            padx=30,
            pady=7
        )

    # =====================================================
    # View Report
    # =====================================================

    def view_report(self):

        if self.on_report:
            self.on_report()
            return

        self.progress_label.configure(
            text=ar("Report not available yet / التقرير غير متاح بعد")
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
                text=ar("تم اختيار الفيديو / Selected:")
                + "\n" + self.video_path,
                text_color=TEXT,
                image=None
            )

            self.status.configure(
                text="READY ●",
                text_color=BLUE
            )

    # =====================================================
    # Start
    # =====================================================

    def start(self):

        if not self.video_path:

            self.status.configure(
                text="NO VIDEO ●",
                text_color=DANGER
            )

            self.progress_label.configure(
                text=ar("Select a video first / اختر فيديو أولاً")
            )

            return

        if self.running:
            return

        self.stop_event.clear()
        self.running = True

        self.status.configure(
            text="RUNNING ●",
            text_color=TEAL
        )

        self.progress_label.configure(
            text=ar("Processing... / جارٍ المعالجة")
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
                self.update_frame,
                self.stop_event
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

        self.total_value.configure(
            text=f"{stats['total']}"
        )

        self.going_value.configure(
            text=f"{stats['going']}"
        )

        self.returning_value.configure(
            text=f"{stats['returning']}"
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

        stopped = self.stop_event.is_set()
        self.status.configure(
            text="STOPPED ●" if stopped else "DONE ✓ ●",
            text_color=DANGER if stopped else SUCCESS
        )

        self.progress_label.configure(
            text=ar(
                "Stopped / تم الإيقاف" if stopped
                else "Processing completed / اكتملت المعالجة"
            )
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
            text="ERROR ●",
            text_color=DANGER
        )

        self.progress_label.configure(
            text=ar("Processing failed / فشلت المعالجة")
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

        if not self.running:
            return

        self.stop_event.set()

        self.status.configure(
            text="STOPPING ●",
            text_color=DANGER
        )

        self.progress_label.configure(
            text=ar("Stopping after the current frame... / جارٍ الإيقاف")
        )

        self.stop_button.configure(
            state="disabled"
        )

    # =====================================================
    # Run GUI
    # =====================================================

    def run(self):

        self.root.mainloop()
