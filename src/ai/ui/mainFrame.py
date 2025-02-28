from ai.ui.components import MenuBar, StatusBar, UserPrompt, ContentDisplay
import customtkinter as ctk
import threading
import time  # For simulating progress updates
import asyncio
import re
import tkinter as tk

from ai.agent.SystemAgent import SystemAgent
from ai.ui.components.psat.questionPaper import QuestionPaperController
from ai.models.psatModel import QuestionModel, Choice

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

        # Create QuestionGrid
        questions = [{
            "question_id": 1,
            "question": "What is the capital of India?",
            "choices": ["Kathmandu", "Delhi", "Dhaka", "Madrid"],
            "answer": "Delhi",
            "explanation": "Delhi is the capital city of India."
        }]
        
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

        self.question_grid = QuestionPaperController(self, self.status_bar, question_models)
        self.question_grid.pack(fill="both", expand=True)

        # Create UserPrompt
        self.user_prompt = UserPrompt(self)
        self.user_prompt.pack(fill="x", pady=10)
        
        # Create ContentDisplay
        self.content_display = ContentDisplay(self)
        self.content_display.pack(fill="both", expand=True)
        self.content_display.display_content("bash Welcome to AgentX - Ollama Chatbot!\n\nPlease type your message in the box below and press 'Submit' to chat with the chatbot.")


    def update_status(self, progress, status, requestResult=None):
        self.status_bar.update_status(progress, status)
        # if requestResult:
        #     self.content_display.display_content(requestResult)

    def handle_user_input(self, input_text):
        # Placeholder for the action to be invoked
        def action():
            self.update_status(50, "Sent Request")
            response = self.systemAgent.executeQuery(input_text)
            
            questions = response.content

            # Update QuestionGrid with new questions
            self.question_grid.update_questions(questions)

            self.update_status(100, "Completed")
        
        # Start the action in a new thread
        threading.Thread(target=action).start()

    def reset_content_display(self):
        # self.content_display.reset()
        pass

async def main():
    app = MainFrame()
    app.mainloop()

# Run the app
if __name__ == "__main__":
    asyncio.run(main())
