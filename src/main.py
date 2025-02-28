from threading import Thread
from dotenv import load_dotenv
from pathlib import Path
from ai.ui.mainFrame import MainFrame
import asyncio

# Get project base folder
BASE_DIR = Path(__file__).resolve().parent

# Load .env file from the base folder
load_dotenv(dotenv_path=f"{BASE_DIR}/.env")
class ThreadedGUI:
    def __init__(self):
        self.root = None
        
    def run_gui(self):
        self.root = MainFrame()
        self.root.mainloop()
    
    def update_status(self, status, requestResult=None):
        self.root.update_status(4, status, requestResult)

    def stop(self):
        if self.root:
            self.root.quit()
        self.gui_thread.join()
    def startUi(self):
        self.gui_thread = Thread(target=self.run_gui, daemon=True)
        self.gui_thread.start()

# Example usage
async def main():
    # Create and start GUI
    gui = ThreadedGUI()
    try:
        gui.startUi()       
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        print("\Stopping...")
        gui.stop()

if __name__ == "__main__":
    asyncio.run(main())
