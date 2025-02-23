from ai.ui.components import MenuBar, StatusBar, UserPrompt, ContentDisplay
import customtkinter as ctk
import threading
import time  # For simulating progress updates
import asyncio
import re
import tkinter as tk

from ai.agent.SystemAgent import SystemAgent
# Set up the main app
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainFrame(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.systemAgent = SystemAgent()
        self.configure(bg="#1E1E1E")
        self.title("AgentX - Ollama Chatbot")
        self.geometry("900x800")
        # Create menu bar
        self.menu_bar = MenuBar(self)

        # Create status bar
        self.status_bar = StatusBar(self)

        # Create ContentDisplay
        self.content_display = ContentDisplay(self)
        self.content_display.pack(fill="both", expand=True)
        self.content_display.display_content("bash Welcome to AgentX - Ollama Chatbot!\n\nPlease type your message in the box below and press 'Submit' to chat with the chatbot.")

        # Create UserPrompt
        self.user_prompt = UserPrompt(self)

    def update_status(self, progress, status, requestResult=None):
        self.status_bar.update_status(progress, status)
        if requestResult:
            self.content_display.display_content(requestResult)

    def handle_user_input(self, input_text):
        # Placeholder for the action to be invoked
        def action():
            # Simulate processing time
            self.content_display.display_content(f"\n--- --- --- --- ---")
            self.content_display.display_content(f"User: {input_text}")
            self.update_status(50, "Sent Request")
            response = self.systemAgent.executeQuery(input_text)
            
            # Update status bar
            for content in response.content:
                self.content_display.display_content(f"---")
                self.content_display.display_content(f"Question: {content['question']}")
                for choice in content['choices']:
                    self.content_display.display_content(f"** {choice['key']}. {choice['value']}")
                
                self.content_display.display_content(f"Answer: {content['answer']['key']}. {content['answer']['explaination']}")
            self.update_status(100, "Completed")
        
        # Start the action in a new thread
        threading.Thread(target=action).start()

    def reset_content_display(self):
        self.content_display.reset()

async def main():
    app = MainFrame()
    app.mainloop()

# Run the app
if __name__ == "__main__":
    asyncio.run(main())
