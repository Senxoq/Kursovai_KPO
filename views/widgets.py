import customtkinter as ctk


class ProgressCard(ctk.CTkFrame):
    def __init__(self, parent, title, color, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.title = title
        self.color = color

        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x")
        ctk.CTkLabel(self.header, text=title, font=("Segoe UI", 12)).pack(side="left")
        self.percent_label = ctk.CTkLabel(self.header, text="0%", font=("Segoe UI", 11, "bold"), text_color=color)
        self.percent_label.pack(side="right")

        self.progress = ctk.CTkProgressBar(self, height=14, corner_radius=7, progress_color=color)
        self.progress.pack(pady=4)
        self.progress.set(0)

        self.value_label = ctk.CTkLabel(self, text="0 / 0", font=("Segoe UI", 10))
        self.value_label.pack()

    def update(self, current, target):
        percent = min(1.0, current / target) if target > 0 else 0
        self.progress.set(percent)
        self.percent_label.configure(text=f"{percent * 100:.0f}%")
        self.value_label.configure(text=f"{current:.0f} / {target:.0f}")