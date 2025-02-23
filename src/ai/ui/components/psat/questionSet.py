import sys
import os
import customtkinter as ctk
from question import QuestionDisplay

class QuestionGrid(ctk.CTkFrame):
    def __init__(self, master, questions):
        super().__init__(master)
        self.questions = questions
        self.current_question_index = None
        self.answered_questions = set()
        self.question_buttons = []
        self.user_selections = {i: None for i in range(len(questions))}
        self.create_widgets()

    def create_widgets(self):
        # Grid Frame
        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.pack(side=ctk.LEFT, padx=10, pady=10)

        # Question Display
        self.question_display = QuestionDisplay(self)
        self.question_display.pack(side=ctk.RIGHT, padx=10, pady=10)
        self.question_display.pack_forget()  # Hide initially

        # Navigation Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(side=ctk.BOTTOM, pady=5)

        self.submit_button = ctk.CTkButton(
            button_frame,
            text="Submit",
            command=self.submit_answer,
            state="disabled"
        )
        self.submit_button.pack(side=ctk.LEFT, padx=5)

        self.reset_button = ctk.CTkButton(
            button_frame,
            text="Reset",
            command=self.reset_selection,
            state="disabled"
        )
        self.reset_button.pack(side=ctk.LEFT, padx=5)

        # Create grid of question buttons
        self.question_buttons = []
        for i, _ in enumerate(self.questions):
            row, col = divmod(i, 5)
            button = ctk.CTkButton(
                self.grid_frame,
                text=str(i+1),
                width=50,
                height=50,
                command=lambda idx=i: self.select_question(idx),
                fg_color=("gray75", "gray30")
            )
            button.grid(row=row, column=col, padx=5, pady=5)
            self.question_buttons.append(button)

    def select_question(self, index):
        # Save current selection if there is one
        if self.current_question_index is not None:
            self.user_selections[self.current_question_index] = self.question_display.get_selected_choice()
            self.question_buttons[self.current_question_index].configure(
                fg_color=("gray75", "gray30")
            )

        # Set new selection
        self.current_question_index = index
        self.question_buttons[index].configure(
            fg_color="red"
        )
        
        # Update question display
        question = self.questions[index]
        self.question_display.update_question(
            question['question'],
            question['choices'],
            question['answer'],
            question['explanation'],
            self.user_selections[index]
        )
        self.question_display.pack(side=ctk.RIGHT, padx=10, pady=10)
        
        # Enable buttons
        self.submit_button.configure(state="normal")
        self.reset_button.configure(state="normal")

    def submit_answer(self):
        if self.current_question_index is not None:
            # Save the final selection
            self.user_selections[self.current_question_index] = self.question_display.get_selected_choice()
            self.answered_questions.add(self.current_question_index)
            
            # Update button color and hide question display
            self.question_buttons[self.current_question_index].configure(
                fg_color=("gray75", "gray30")
            )
            self.question_display.pack_forget()
            
            # Reset current state
            self.current_question_index = None
            self.submit_button.configure(state="disabled")
            self.reset_button.configure(state="disabled")

    def reset_selection(self):
        if self.current_question_index is not None:
            self.user_selections[self.current_question_index] = None
            self.question_display.reset()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("PSAT Question Display")

    questions = [
        {
            "question": "What is the capital of France?",
            "choices": ["Paris", "London", "Berlin", "Madrid"],
            "answer": "Paris",
            "explanation": "Paris is the capital and most populous city of France."
        },
        {
            "question": "What is the capital of India?",
            "choices": ["Kathmandu", "Delhi", "Dhaka", "Madrid"],
            "answer": "Delhi",
            "explanation": "Delhi is the capital city of India."
        },
    ]

    app = QuestionGrid(root, questions)
    app.pack(padx=10, pady=10)

    root.mainloop()