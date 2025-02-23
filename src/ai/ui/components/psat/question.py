import customtkinter as ctk

class QuestionDisplay(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_choice = ctk.StringVar()
        self.show_answer = ctk.BooleanVar()
        self.choice_buttons = []
        
        # Initialize empty attributes
        self.question = ""
        self.choices = []
        self.answer = ""
        self.explanation = ""
        
        self.create_widgets()

    def create_widgets(self):
        # Question Frame
        self.question_frame = ctk.CTkFrame(self)
        self.question_frame.pack(fill=ctk.X, pady=5)
        self.question_label = ctk.CTkLabel(self.question_frame, text="", wraplength=400)
        self.question_label.pack()

        # Choices Frame
        self.choices_frame = ctk.CTkFrame(self)
        self.choices_frame.pack(fill=ctk.X, pady=5)
        
        # Answer and Explanation Frame
        self.answer_frame = ctk.CTkFrame(self)
        self.answer_frame.pack(fill=ctk.X, pady=5)
        self.answer_label = ctk.CTkLabel(self.answer_frame, text="", wraplength=400)
        self.explanation_label = ctk.CTkLabel(self.answer_frame, text="", wraplength=400)
        
        # Toggle Button
        self.toggle_button = ctk.CTkCheckBox(
            self,
            text="Show Answer and Explanation",
            variable=self.show_answer,
            command=self.toggle_answer
        )
        self.toggle_button.pack(pady=5)

    def update_question(self, question, choices, answer, explanation, selected_choice=None):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.explanation = explanation
        
        # Update question text
        self.question_label.configure(text=question)
        
        # Clear and recreate choice buttons
        for widget in self.choices_frame.winfo_children():
            widget.destroy()
        self.choice_buttons = []
        
        # Set the selected choice
        if selected_choice is not None:
            self.selected_choice.set(selected_choice)
        else:
            self.selected_choice.set("")
            
        # Create new choice buttons
        for choice in choices:
            choice_button = ctk.CTkRadioButton(
                self.choices_frame, 
                text=choice,
                variable=self.selected_choice,
                value=choice
            )
            choice_button.pack(anchor=ctk.W, pady=2)
            self.choice_buttons.append(choice_button)
            
        # Update answer and explanation
        self.answer_label.configure(text=f"Answer: {answer}")
        self.explanation_label.configure(text=f"Explanation: {explanation}")
        
        # Reset answer visibility
        self.show_answer.set(False)
        self.toggle_answer()

    def toggle_answer(self):
        if self.show_answer.get():
            self.answer_label.pack()
            self.explanation_label.pack()
        else:
            self.answer_label.pack_forget()
            self.explanation_label.pack_forget()
            
    def reset(self):
        self.selected_choice.set("")
        self.show_answer.set(False)
        self.toggle_answer()

    def get_selected_choice(self):
        return self.selected_choice.get()
