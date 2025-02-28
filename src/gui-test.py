import customtkinter as ctk
import tkinter as tk
from typing import List, Dict, Callable, Optional
import json
from ai.models.psatModel import QuestionModel, Choice, ALLOWED_CHOICES

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Solution(ctk.CTkFrame):
    """Component for displaying solution with show answer checkbox and explanation"""
    def __init__(self, master, model: QuestionModel):
        super().__init__(master, fg_color="transparent")
        self.model = model
        
        self._create_widgets()
        self._update_visibility()
    
    def _create_widgets(self):
        # Show answer checkbox
        self.show_answer_var = tk.BooleanVar(value=self.model.show_answer)
        self.show_answer_checkbox = ctk.CTkCheckBox(
            self,
            text="Show answer",
            variable=self.show_answer_var,
            command=self._on_show_answer_change,
            checkbox_width=20,
            checkbox_height=20
        )
        self.show_answer_checkbox.pack(anchor="w", padx=10, pady=5)
        
        # Explanation
        self.explanation_frame = ctk.CTkFrame(self)
        self.explanation_frame.pack(fill=tk.X, padx=0, pady=5)
        
        self.explanation_label = ctk.CTkLabel(
            self.explanation_frame, 
            text="Explanation:", 
            anchor="w",
            pady=5,
            padx=5
        )
        self.explanation_label.pack(anchor="w")
        
        self.explanation_text = ctk.CTkTextbox(self.explanation_frame, height=60)
        self.explanation_text.pack(fill=tk.X, padx=5, pady=5)
        self.explanation_text.insert("1.0", self.model.explanation)
        self.explanation_text.configure(state="disabled")
    
    def _on_show_answer_change(self):
        self.model.show_answer = self.show_answer_var.get()
        self._update_visibility()
    
    def _update_visibility(self):
        if self.model.show_answer:
            self.explanation_frame.pack(fill=tk.X, padx=0, pady=5)
        else:
            self.explanation_frame.pack_forget()
    
    def update_model(self, model: QuestionModel):
        """Update the solution component with a new model"""
        self.model = model
        
        # Update explanation text
        self.explanation_text.configure(state="normal")
        self.explanation_text.delete("1.0", tk.END)
        self.explanation_text.insert("1.0", self.model.explanation)
        self.explanation_text.configure(state="disabled")
        
        # Update show answer checkbox
        self.show_answer_var.set(self.model.show_answer)
        self._update_visibility()

class QuestionView(ctk.CTkFrame):
    """Question view component that displays a single question"""
    def __init__(self, master, model: QuestionModel, on_selection_change: Callable = None):
        super().__init__(master, fg_color="transparent")
        self.model = model
        self.on_selection_change = on_selection_change
        self.choice_vars = []
        
        self._create_widgets()
        self._update_view()
        
    def _create_widgets(self):
        # Top section for question and choices
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Question text
        self.question_frame = ctk.CTkFrame(self.content_frame, corner_radius=0)
        self.question_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.question_label = ctk.CTkLabel(
            self.question_frame, 
            text=f"Question #{self.model.question_id}:", 
            anchor="w",
            pady=5,
            padx=5
        )
        self.question_label.pack(anchor="w")
        
        self.question_text = ctk.CTkTextbox(self.question_frame, height=60)
        self.question_text.pack(fill=tk.X, padx=5, pady=5)
        self.question_text.insert("1.0", self.model.question_text)
        self.question_text.configure(state="disabled")
        
        # Choices
        self.choices_frame = ctk.CTkFrame(self.content_frame)
        self.choices_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.choice_var = tk.StringVar(value="")
        
        for choice in self.model.choices:
            choice_btn = ctk.CTkRadioButton(
                self.choices_frame,
                text=choice.value,
                variable=self.choice_var,
                value=choice.key,
                command=self._on_choice_selection
            )
            choice_btn.pack(anchor="w", padx=20, pady=5)
            self.choice_vars.append(choice_btn)
        
        # Bottom section for Solution and Save button
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        # Solution component (contains show answer and explanation)
        self.solution = Solution(self.bottom_frame, self.model)
        self.solution.pack(fill=tk.X, side=tk.TOP, expand=True)
        
        # Save button
        self.save_btn = ctk.CTkButton(
            self.bottom_frame,
            text="Save",
            width=90,
            height=30,
            corner_radius=8,
            command=self._on_save_click
        )
        self.save_btn.pack(side=tk.BOTTOM, padx=10)
        
    def _on_save_click(self):
        # Trigger save functionality in the parent controller
        if hasattr(self.master, '_save_answers'):
            self.master._save_answers()
        
    def _on_choice_selection(self):
        selected = self.choice_var.get() if self.choice_var.get() else None
        self.model.selected_choice = selected
        if self.on_selection_change:
            self.on_selection_change(self.model)
    
    def _update_view(self):
        if self.model.selected_choice is not None:
            self.choice_var.set(self.model.selected_choice)
        # Update solution component
        self.solution.update_model(self.model)
    
    def update_model(self, model: QuestionModel):
        """Update the view with a new model"""
        self.model = model
        
        # Update question text
        self.question_text.configure(state="normal")
        self.question_text.delete("1.0", tk.END)
        self.question_text.insert("1.0", self.model.question_text)
        self.question_text.configure(state="disabled")
        
        # Update question number in label
        self.question_label.configure(text=f"Question #{self.model.question_id}:")
        
        # Reset choice selection
        self.choice_var.set("")
        
        # Update choices text
        for i, choice_btn in enumerate(self.choice_vars):
            if i < len(self.model.choices):
                choice_btn.configure(text=self.model.choices[i].value)
                choice_btn.pack(anchor="w", padx=20, pady=5)
            else:
                choice_btn.pack_forget()  # Hide extra choices if any
        
        # Set the selected choice if there is one
        if self.model.selected_choice is not None:
            self.choice_var.set(self.model.selected_choice)
        
        # Update solution component
        self.solution.update_model(self.model)


class QuestionTrackerButton(ctk.CTkButton):
    """Custom button for the question tracker"""
    def __init__(self, master, question_id: int, is_current: bool = False, 
                 on_click: Callable = None, question_model: QuestionModel = None, **kwargs):
        self.question_id = question_id
        self.is_current = is_current
        self.on_click = on_click
        self.question_model = question_model
        
        # Define colors for different states
        # self.COLORS = {
        #     "current": {"fg": "#3B8ED0", "hover": "#36719F"},  # Blue
        #     "correct": {"fg": "#32CD32", "hover": "#228B22"},  # Green
        #     "incorrect": {"fg": "#FF4444", "hover": "#CC0000"},  # Red
        #     "unanswered": {"fg": "#2B2B2B", "hover": "#1F1F1F"},  # gray
        #     "default": {"fg": "#2B2B2B", "hover": "#1F1F1F"}  # Dark gray
        # }
        
        self.COLORS = {
            "current": {"fg": "#3B8ED0", "hover": "#36719F"},     # Blue
            "correct": {"fg": "#28A745", "hover": "#218838"},     # Green
            "incorrect": {"fg": "#DC3545", "hover": "#C82333"},   # Red
            "unanswered": {"fg": "#6C757D", "hover": "#5A6268"}, # Gray
            "default": {"fg": "#6C757D", "hover": "#5A6268"}     # Gray
        }
        
        # Get initial colors based on state
        colors = self._get_button_colors()
        
        super().__init__(
            master, 
            text=str(question_id),
            width=30,
            height=30,
            corner_radius=5,
            fg_color=colors["fg"],
            hover_color=colors["hover"],
            command=self._on_button_click,
            **kwargs
        )
    
    def _get_button_colors(self) -> Dict[str, str]:
        """Determine button colors based on current state"""
        if self.is_current:
            return self.COLORS["current"]
        
        if self.question_model:
            if self.question_model.selected_choice is not None:
                is_correct = self.question_model.selected_choice == self.question_model.correct_answer
                return self.COLORS["correct"] if is_correct else self.COLORS["incorrect"]
            return self.COLORS["unanswered"]
        
        return self.COLORS["default"]
    
    def _on_button_click(self):
        if self.on_click:
            self.on_click(self.question_id)
    
    def update_state(self, is_current: bool, question_model: QuestionModel = None):
        """Update the button's appearance based on current state and question model"""
        self.is_current = is_current
        self.question_model = question_model
        colors = self._get_button_colors()
        self.configure(fg_color=colors["fg"], hover_color=colors["hover"])


class QuestionTrackerView(ctk.CTkFrame):
    """Component for tracking and navigating between questions"""
    def __init__(self, master, questions: List[QuestionModel], on_question_select: Callable):
        super().__init__(master)
        self.questions = questions
        self.on_question_select = on_question_select
        self.current_question = 1
        self.buttons = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        tracker_label = ctk.CTkLabel(self, text="Question Tracker", anchor="w")
        tracker_label.pack(anchor="w", padx=10, pady=(5, 10))
        
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for i, question in enumerate(self.questions, 1):
            is_current = i == self.current_question
            btn = QuestionTrackerButton(
                buttons_frame,
                question_id=i,
                is_current=is_current,
                question_model=question,
                on_click=self._on_question_button_click
            )
            btn.grid(row=0, column=i-1, padx=2, pady=2)
            self.buttons.append(btn)
    
    def _on_question_button_click(self, question_id: int):
        self.set_current_question(question_id)
        if self.on_question_select:
            self.on_question_select(question_id)
    
    def update_question_state(self, question_id: int, question_model: QuestionModel):
        """Update the state of a specific question button"""
        if 0 <= question_id - 1 < len(self.buttons):
            self.buttons[question_id - 1].update_state(
                is_current=question_id == self.current_question,
                question_model=question_model
            )
    
    def set_current_question(self, question_id: int):
        """Update tracker to highlight the current question"""
        if 1 <= question_id <= len(self.questions):
            self.current_question = question_id
            for i, btn in enumerate(self.buttons, 1):
                btn.update_state(
                    is_current=(i == question_id),
                    question_model=self.questions[i-1]
                )


class ChatInputView(ctk.CTkFrame):
    """Component for chat/prompt input"""
    def __init__(self, master, on_submit: Callable = None, placeholder_text: str = ""):
        super().__init__(master)
        self.on_submit = on_submit
        self.placeholder_text = placeholder_text
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Chat label
        self.chat_label = ctk.CTkLabel(self, text="Chat TextBox", anchor="w")
        self.chat_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Chat text input frame
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Chat textbox
        self.chat_textbox = ctk.CTkTextbox(
            self.chat_frame, 
            height=80,
            corner_radius=8,
            border_width=2,
            border_color="#3F3F3F"
        )
        self.chat_textbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add placeholder text
        if self.placeholder_text:
            self.chat_textbox.insert("1.0", self.placeholder_text)
        
        # Add Reset and Submit buttons
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.pack(fill=tk.X, pady=5)
        
        self.reset_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Reset",
            width=90,
            height=30,
            corner_radius=8,
            fg_color="#FF7744",
            hover_color="#E66633",
            command=self._on_reset_click
        )
        self.reset_btn.pack(side=tk.LEFT, padx=10)
        
        self.submit_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Submit",
            width=90,
            height=30,
            corner_radius=8,
            command=self._on_submit_click
        )
        self.submit_btn.pack(side=tk.RIGHT, padx=10)
    
    def _on_reset_click(self):
        """Reset the chat input to placeholder text"""
        self.chat_textbox.delete("1.0", tk.END)
        if self.placeholder_text:
            self.chat_textbox.insert("1.0", self.placeholder_text)
    
    def _on_submit_click(self):
        """Submit the prompt text for processing"""
        prompt_text = self.chat_textbox.get("1.0", tk.END).strip()
        if self.on_submit and prompt_text:
            self.on_submit(prompt_text)
    
    def get_prompt_text(self) -> str:
        """Get the current prompt text"""
        return self.chat_textbox.get("1.0", tk.END).strip()
    
    def set_prompt_text(self, text: str):
        """Set the prompt text"""
        self.chat_textbox.delete("1.0", tk.END)
        self.chat_textbox.insert("1.0", text)


class StatusBarView(ctk.CTkFrame):
    """Component for displaying status and progress"""
    def __init__(self, master):
        super().__init__(master)
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Status frame
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status: Ready to begin...",
            anchor="w"
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.progress_bar = ctk.CTkProgressBar(
            self.status_frame, 
            width=200,
            height=12,
            border_width=1,
            progress_color="#32CD32"  # Green color for progress
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=10)
        self.progress_bar.set(0)  # Initialize at 0%
    
    def update_status(self, status_text: str, progress_value: float):
        """Update the status text and progress bar"""
        self.status_label.configure(text=f"Status: {status_text}")
        self.progress_bar.set(progress_value)


class QuestionPaperController:
    """Controller class for the question paper UI"""
    def __init__(self, title="Physics Question Paper for PSAT"):
        self.title = title
        self.questions = []
        self.current_question_id = 1
        
        # Create sample questions
        self._create_sample_questions()
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title(self.title)
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # Create main container frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text=self.title,
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Create question view
        self.question_view = QuestionView(
            self.main_frame, 
            self.questions[self.current_question_id - 1],
            self._on_selection_change
        )
        self.question_view.pack(fill=tk.BOTH, expand=True)
        
        # Create question tracker
        self.tracker_view = QuestionTrackerView(
            self.main_frame,
            self.questions,  # Pass the questions list instead of just the count
            self._on_question_select
        )
        self.tracker_view.pack(fill=tk.X, pady=10)
        
        # Create chat input view with reset and submit buttons
        self.chat_input = ChatInputView(
            self.main_frame, 
            self._on_prompt_submit,
            "Create a Physics Question Paper for PSAT"
        )
        self.chat_input.pack(fill=tk.X, pady=10)
        
        # Create status bar
        self.status_bar = StatusBarView(self.main_frame)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _calculate_score(self):
        """Calculate the current score"""
        correct = sum(1 for q in self.questions if q.is_correct())
        total = len(self.questions)
        return correct, total

    def _update_progress_status(self):
        """Update progress bar and status text"""
        answered = sum(1 for q in self.questions if q.selected_choice is not None)
        correct, total = self._calculate_score()
        progress = answered / total
        
        status_text = (f"Score: {correct}/{total} correct | "
                    f"Progress: {answered}/{total} answered")
        self.status_bar.update_status(status_text, progress)

    def _create_sample_questions(self):
        """Create sample question data using the new QuestionModel format"""
        self.questions.append(QuestionModel(
            question_id=1,
            question_text="What is friction?",
            choices=[
                Choice(key='a', value="A force that opposes motion between surfaces in contact"),
                Choice(key='b', value="A force that accelerates objects"),
                Choice(key='c', value="A type of energy conversion"),
                Choice(key='d', value="A form of mechanical advantage")
            ],
            correct_answer='a',
            explanation="Friction is a force that opposes the relative motion between two surfaces in contact."
        ))

        self.questions.append(QuestionModel(
            question_id=2,
            question_text="Which of Newton's laws states that for every action, there is an equal and opposite reaction?",
            choices=[
                Choice(key='a', value="First law"),
                Choice(key='b', value="Second law"),
                Choice(key='c', value="Third law"),
                Choice(key='d', value="Fourth law")
            ],
            correct_answer='c',
            explanation="Newton's Third Law states that for every action, there is an equal and opposite reaction. This means that forces always occur in pairs."
        ))
        
        self.questions.append(QuestionModel(
            question_id=3,
            question_text="What is the SI unit of electric current?",
            choices=[
                Choice(key='a', value="Volt"),
                Choice(key='b', value="Ohm"),
                Choice(key='c', value="Ampere"),
                Choice(key='d', value="Coulomb")
            ],
            correct_answer='c',
            explanation="The SI unit of electric current is the ampere (A), which measures the rate of flow of electric charge."
        ))
        
        self.questions.append(QuestionModel(
            question_id=4,
            question_text="What is the formula for calculating work?",
            choices=[
                Choice(key='a', value="W = m × g"),
                Choice(key='b', value="W = F × d × cos(θ)"),
                Choice(key='c', value="W = 1/2 × m × v²"),
                Choice(key='d', value="W = P × t")
            ],
            correct_answer='b',
            explanation="Work is calculated as force times displacement times the cosine of the angle between them: W = F × d × cos(θ)."
        ))
        
        self.questions.append(QuestionModel(
            question_id=5,
            question_text="Which of the following is a vector quantity?",
            choices=[
                Choice(key='a', value="Mass"),
                Choice(key='b', value="Temperature"),
                Choice(key='c', value="Time"),
                Choice(key='d', value="Acceleration")
            ],
            correct_answer='d',
            explanation="Acceleration is a vector quantity because it has both magnitude and direction. Mass, temperature, and time are scalar quantities."
        ))
        
        self.questions.append(QuestionModel(
            question_id=6,
            question_text="What causes the tides on Earth?",
            choices=[
                Choice(key='a', value="Earth's rotation"),
                Choice(key='b', value="Solar winds"),
                Choice(key='c', value="Gravitational pull of the Moon and Sun"),
                Choice(key='d', value="Ocean currents")
            ],
            correct_answer='c',
            explanation="Tides on Earth are primarily caused by the gravitational pull of the Moon and to a lesser extent, the Sun."
        ))
    
    def _on_question_select(self, question_id: int):
        """Handle question selection from the tracker"""
        self.current_question_id = question_id
        self.question_view.update_model(self.questions[question_id - 1])
    
    def _on_selection_change(self, updated_model: QuestionModel):
        """Handle answer selection in current question"""
        # Update tracker button state
        self.tracker_view.update_question_state(
            updated_model.question_id,
            updated_model
        )
        
        # Calculate progress and update status bar
        answered_count = sum(1 for q in self.questions if q.selected_choice is not None)
        progress = answered_count / len(self.questions)
        
        status_text = (f"Progress: {answered_count} of {len(self.questions)} "
                    f"questions answered ({progress:.0%})")
        self.status_bar.update_status(status_text, progress)
    
    def _on_prompt_submit(self, prompt_text: str):
        """Handle prompt submission from chat input"""
        # Here you would normally process the prompt and generate questions
        # For this example, we'll just update the status
        self.status_bar.update_status(f"Processing prompt: {prompt_text[:30]}...", 0.2)
        
        # In a real implementation, you might call an AI model or API here
        # to generate questions based on the prompt
        print(f"Prompt submitted: {prompt_text}")
    
    def _save_answers(self):
        """Save the current answers and update status"""
        correct, total = self._calculate_score()
        answered = sum(1 for q in self.questions if q.selected_choice is not None)
        progress = answered / total
        
        status_text = (f"Saved! Score: {correct}/{total} ({(correct/total):.0%}) | "
                    f"Completed: {answered}/{total} ({progress:.0%})")
        self.status_bar.update_status(status_text, progress)
        
        # Save answers to JSON
        answers_data = {
            "title": self.title,
            "questions": [q.to_dict() for q in self.questions],
            "prompt": self.chat_input.get_prompt_text(),
            "score": {
                "correct": correct,
                "total": total,
                "percentage": (correct/total) * 100
            }
        }
        
        try:
            with open("physics_answers.json", "w") as f:
                json.dump(answers_data, f, indent=2)
            print("Answers saved successfully")
        except Exception as e:
            print(f"Error saving answers: {e}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = QuestionPaperController()
    app.run()