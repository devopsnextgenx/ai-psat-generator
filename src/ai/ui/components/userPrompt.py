import customtkinter as ctk
import tkinter as tk

class UserPrompt(ctk.CTkFrame):
    def __init__(self, master, parent):
        super().__init__(master, fg_color="transparent")
        self.parent = parent
        self.pack(side="bottom", fill="both", padx=10, pady=5, expand=True)

        # Create input textbox
        self.prompt = ctk.CTkTextbox(self, height=300)  # Approx 4 lines
        self.prompt.pack(side="top", fill="both", expand=True)
        self.prompt.pack_propagate(False)
        self.prompt.configure(font=("Arial", 14))  # Adjust text size

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=5)

        # Create reset and submit buttons
        self.reset_button = ctk.CTkButton(self.button_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side="left", padx=5, pady=5)

        self.submit_button = ctk.CTkButton(self.button_frame, text="Submit", command=self.submit)
        self.submit_button.pack(side="right", padx=5, pady=5)

        # Bind the event to dynamically resize the textbox
        self.prompt.bind("<KeyRelease>", self.resize_textbox)

        # Bind Shift+Enter to submit input
        self.prompt.bind("<Shift-Return>", self.submit)

    def resize_textbox(self, event=None):
        lines = int(self.prompt.index('end-1c').split('.')[0])
        new_height = min(max(lines * 25, 100), 250)  # Adjust pixel scaling
        self.prompt.configure(height=new_height)

    def reset(self):
        self.prompt.delete("1.0", tk.END)
        self.parent.reset_content_display()

    def submit(self, event=None):
        input_text = self.prompt.get("1.0", tk.END).strip()
        if input_text:
            # Call the handle_user_input method from MainFrame
            self.parent.handle_user_input(input_text)
            self.reset()