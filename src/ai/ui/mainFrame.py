from ai.ui.components import MenuBar, StatusBar, UserPrompt, ContentDisplay
import customtkinter as ctk
import threading
import asyncio
import time
from ai.agent.SystemAgent import SystemAgent
from ai.ui.components.psat.questionPaper import QuestionPaperController
from ai.models.psatModel import QuestionModel, Choice
from ai.ui.utils.psatUtils import create_sample_questions
from ai.agent.utils.VoiceUtils import TTSQueue
from threading import Thread
from ai.agent.pts import process_audio

# Add after the imports
class ListeningIndicator(ctk.CTkCanvas):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, width=20, height=20, *args, **kwargs)
        self.configure(bg="#1E1E1E", highlightthickness=0)
        self.create_oval(5, 5, 15, 15, fill="#0000FF", outline="white", width=1)

    def set_listening(self, is_listening, is_playing=False):
        self.delete("all")
        if is_listening:
            color = "#FF0000"  # Red when listening
        elif is_playing:
            color = "#00FF00"  # Green when playing
        else:
            color = "#0000FF"  # Blue otherwise
        self.create_oval(5, 5, 15, 15, fill=color, outline="white", width=1)

# Set up the main app
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainFrame(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Initialize TTSQueue with status callback
        self.tts_queue = TTSQueue(status_callback=self.update_listening_indicator)
        self.tts_queue.start_processing()
        
        self.systemAgent = SystemAgent()
        self.audio_thread = None
        self.configure(bg="#1E1E1E")
        self.title("AgentX - Ollama Chatbot")
        self.geometry("900x800")
        
        # Create listening indicator before other widgets
        self.listening_indicator = ListeningIndicator(self)
        self.listening_indicator.pack(side="top", anchor="ne", padx=10, pady=5)
        
        # Create menu bar
        self.menu_bar = MenuBar(self)

        # Create status bar
        self.status_bar = StatusBar(self)

        # Create a scrollable frame to hold the content
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(side="top", fill="both", expand=True)

        # Create a container frame inside the scrollable frame
        self.content_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.content_container.pack(side="top", fill="both", expand=True)

        # Configure content_container to allocate equal space
        self.content_container.grid_rowconfigure(1, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)
        
        # Create QuestionGrid - allocate 50% of vertical space
        questions = []
        
        # Convert dictionary to QuestionModel list
        question_models = []
        for q in questions:
            # Create Choice objects for each option
            choices = [
                Choice(key='a', value=q["choices"][0]),
                Choice(key='b', value=q["choices"][1]),
                Choice(key='c', value=q["choices"][2]),
                Choice(key='d', value=q["choices"][3])
            ]
            
            # Find correct answer index to map to a,b,c,d
            correct_answer_idx = q["choices"].index(q["answer"])
            correct_answer = ['a', 'b', 'c', 'd'][correct_answer_idx]
            
            # Create QuestionModel instance
            question_model = QuestionModel(
                question_id=q["question_id"],
                question_text=q["question"],
                choices=choices,
                correct_answer=correct_answer,
                explanation=q["explanation"],
                show_answer=False
            )
            question_models.append(question_model)

        # Create question paper in the top half of content_container
        self.question_paper = QuestionPaperController(self.content_container, self.status_bar, question_models)
        
        self.question_paper.update_questions(create_sample_questions())

        # Create main container frame in the bottom half of content_container
        self.main_container = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew")

        # Configure main_container to allocate equal space
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Create UserPrompt at the bottom of main_container
        self.user_prompt = UserPrompt(self.main_container, self)
        
        # Create ContentDisplay in the remaining space of main_container
        self.content_display = ContentDisplay(self.main_container)
        self.content_display.display_content("## Welcome to AgentX - Ollama Chatbot!\n\nPlease type your message in the box below and press `'Submit'` to chat with the chatbot.")

        # Start audio processing
        self.start_audio_processing()

    def process_audio_callback(self, text, is_listening, is_playing):
        """Callback function to handle the recognized text and listening state."""
        self.listening_indicator.set_listening(is_listening, is_playing)
        if text:
            self.handle_user_input(text)
            
    def start_audio_processing(self):
        """Start audio processing in a separate thread."""
        self.audio_thread = Thread(
            target=process_audio,
            args=(self.process_audio_callback,),
            daemon=True
        )
        self.audio_thread.start()

    def update_status(self, progress, status, requestResult=None):
        self.status_bar.update_status(progress, status)
        # if requestResult:
        #     self.content_display.display_content(requestResult)

    def handle_user_input(self, input_text):
        def actionQuestions():
            self.update_status(50, "Sent Request")
            response = self.systemAgent.executeQuery(input_text)
            
            questions = response.content

            # Update QuestionGrid with new questions
            self.question_paper.update_questions(questions)
            
            # Update content display with generated questions summary
            summary = f"Generated `{len(questions)}` questions based on your input:\n"
            summary += "## Questions have been loaded into the question grid above."
            self.content_display.display_content(summary)

            self.update_status(100, "Completed")
            
        def action():
            self.update_status(50, "Processing Request")
            response = self.systemAgent.executeQuery(input_text)

            responseText = response.content
            
            if self.tts_queue:
                for sentence in responseText.split('.'):
                    self.tts_queue.add_text(sentence)
                    time.sleep(0.3)
            self.content_display.display_content(responseText, "user")

            self.update_status(100, "Completed")
        
        # Start the action in a new thread
        threading.Thread(target=action).start()

    def reset_content_display(self):
        # self.content_display.reset()
        pass

    def destroy(self):
        """Clean up resources before destroying the window."""
        if self.audio_thread:
            self.audio_thread.join(timeout=1)
        if self.tts_queue:
            self.tts_queue.stop_processing()
        super().destroy()

    def update_listening_indicator(self, is_playing):
        """Update the listening indicator based on TTSQueue status."""
        # Remove reference to listening_indicator before destruction
        if hasattr(self, 'listening_indicator'):
            self.listening_indicator.set_listening(is_listening=False, is_playing=is_playing)

async def main():
    app = MainFrame()
    app.mainloop()

# Run the app
if __name__ == "__main__": 
    asyncio.run(main())