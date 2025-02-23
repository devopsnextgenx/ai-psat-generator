import tkinter as tk

class MenuBar(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)
        parent.config(menu=self)

        # Common style options
        menu_options = {
            'activebackground': '#d0e7ff',
            'activeforeground': '#000000',
            'background': '#b0c4de',
            'foreground': '#000000',
            'font': ('Helvetica', 10),
            'tearoff': 0
        }

        # Add file menu
        self.file_menu = tk.Menu(self, **menu_options)
        self.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New")
        self.file_menu.add_command(label="Open")
        self.file_menu.add_command(label="Save")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=parent.quit)

        # Add edit menu
        self.edit_menu = tk.Menu(self, **menu_options)
        self.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo")
        self.edit_menu.add_command(label="Redo")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut")
        self.edit_menu.add_command(label="Copy")
        self.edit_menu.add_command(label="Paste")
