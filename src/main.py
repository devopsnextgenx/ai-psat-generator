from threading import Thread
from dotenv import load_dotenv
from pathlib import Path
from ai.ui.mainFrame import MainFrame
import asyncio
import tkinter as tk

# Get project base folder
BASE_DIR = Path(__file__).resolve().parent

# Load .env file from the base folder
load_dotenv(dotenv_path=f"{BASE_DIR}/.env")

class ThreadedGUI:
    def __init__(self):
        self.root = None
        
    def run_gui(self):
        """Run the GUI in the main thread."""
        self.root = MainFrame()
        self.root.mainloop()
    
    def update_status(self, status, requestResult=None):
        if self.root:
            self.root.update_status(4, status, requestResult)

    def stop(self):
        if self.root:
            self.root.destroy()

async def main():
    try:
        # Create and run GUI
        app = MainFrame()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        print("\nStopping...")
        if app:
            app.destroy()

if __name__ == "__main__":
    asyncio.run(main())
