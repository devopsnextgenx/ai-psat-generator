import customtkinter as ctk

class StatusBar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, height=30)
        self.pack(side="bottom", fill="x")
        self.grid_columnconfigure(1, weight=1)
        self.pack_propagate(False)

        # Create progress label
        self.progress_label = ctk.CTkLabel(self, text="Status: Idle", anchor="w")
        self.progress_label.pack(side="left", padx=10, pady=5, expand=True, fill="x")

        # Create progress bar
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate")
        self.progress_bar.pack(side="right", fill="x", padx=10, pady=5)
        self.progress_bar.set(0)

    def update_status(self, progress, status):
        self.progress_label.configure(text=f"Status: {status}")
        self.progress_bar.set(progress / 100)
