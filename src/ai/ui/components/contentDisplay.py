import customtkinter as ctk
import tkinter as tk
from ai.ui.utils.parsers import parse_markdown

class ContentDisplay(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(side="bottom", fill="both", expand=True)
        self.content = ctk.CTkTextbox(self, wrap="word", height=250, state="disabled", fg_color="#1E1E1E", text_color="#EAEAEA", border_color="#444444")
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        self.content.configure(state="disabled")
        # Enhanced tag configurations with better color contrast and hierarchy
        text_configs = {
            "user": {
                "foreground": "#FF6B6B",  # Soft red for user messages
                "font": ("Inter", 12, "bold")
            },
            "bot": {
                "foreground": "#E0E0E0",  # Main text color
                "font": ("Inter", 12)
            },
            "x": {
                "foreground": "#E0E0E0",  # Main text color
                "font": ("Inter", 12)
            },
            "bot-msg": {
                "foreground": "#FFD93D",  # Warm yellow for bot messages
                "font": ("Inter", 11)
            },
            "bold": {
                "font": ("Inter", 12, "bold"),
                "foreground": "#4A9EFF"  # Bright blue for emphasis
            },
            "italic": {
                "font": ("Inter", 12, "italic"),
                "foreground": "#E0E0E0"
            },
            "code-inline": {
                "font": ("JetBrains Mono", 11),
                "background": "#2A2A2A",  # Subtle background for code
                "foreground": "red"  # Cyan for code
            },
            "code": {
                "font": ("JetBrains Mono", 11),
                "background": "#2A2A2A",  # Subtle background for code
                "foreground": "#56B6C2"  # Cyan for code
            },
            "monospace": {
                "font": ("JetBrains Mono", 11),
                "foreground": "#98C379"  # Light green for monospace
            },
            "heading1": {
                "font": ("Inter", 16, "bold"),
                "foreground": "#4A9EFF"  # Bright blue for main headings
            },
            "heading2": {
                "font": ("Inter", 14, "bold"),
                "foreground": "#61AFEF"  # Lighter blue for subheadings
            },
            "heading3": {
                "font": ("Inter", 12, "bold"),
                "foreground": "#56B6C2"  # Cyan for smaller headings
            },
            "heading": {
                "font": ("Inter", 14, "bold"),
                "foreground": "#4A9EFF"
            },
            "emoji": {
                "foreground": "#FFD93D",  # Warm yellow for emojis
                "font": ("Segoe UI Emoji", 16)
            },
            "table": {
                "font": ("Courier", 12, "bold"),
                "foreground": "#2cff05"  # Light green for tables
            }
        }
        
        # Apply tag configurations
        for tag, config in text_configs.items():
            self.content._textbox.tag_configure(tag, **config)
            
    def display_content(self, message, role = "bot"):
        self.content.configure(state="normal")
        # self.content.delete("1.0", tk.END)
        """Update the chat display."""
        prefix = "\n🧑 " if role == "user" else "\n🤖 "
        if not message.startswith("="):
            self.content._textbox.insert("end", prefix, "emoji")
        
        message = parse_markdown(message)
        
        for word, tag in message:
            self.content.insert("end", f"{word}", tag if tag else role)

        # self.chat_display._textbox.insert("end", f"{message}\n\n", role)
        
        self.content.see("end")
        self.content.configure(state="disabled")

    def reset(self):
        self.content.configure(state="normal")
        self.content.delete("1.0", tk.END)
        self.content.configure(state="disabled")
