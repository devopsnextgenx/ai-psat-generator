import customtkinter as ctk
import tkinter as tk
from typing import Callable, Dict, List
from ai.models.psatModel import QuestionModel

class QuestionTrackerButton(ctk.CTkButton):
    """Custom button for the question tracker"""
    def __init__(self, parent, master, question_id: int, is_current: bool = False, 
                 on_click: Callable = None, question_model: QuestionModel = None, **kwargs):
        self.parent = parent
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
            "answered": {"fg": "#3B8ED0", "hover": "#36719F"}, # Gray
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
        if self.question_model:
            # Get evaluated state from parent tracker
            is_evaluated = self.parent.is_evaluated
            
            if self.question_model.selected_choice is not None:
                if is_evaluated:
                    is_correct = self.question_model.selected_choice == self.question_model.correct_answer
                    return self.COLORS["correct"] if is_correct else self.COLORS["incorrect"]
                return self.COLORS["answered"]
            return self.COLORS["unanswered"]
        
        return self.COLORS["default"]
    
    def _on_button_click(self):
        if self.on_click:
            self.on_click(self.question_id)
    
    def update_state(self, is_current: bool, question_model: QuestionModel = None):
        """Update the button's appearance based on current state and question model"""
        try:
            self.is_current = is_current
            self.question_model = question_model
            colors = self._get_button_colors()
            
            # Add underline for current question
            text = str(self.question_id)
            if is_current:
                text = f"_{text}_"  # Add underscores to indicate current question
                
            self.configure(
                fg_color=colors["fg"], 
                hover_color=colors["hover"],
                text=text
            )
        except tk.TclError:
            pass  # Ignore if widget is already destroyed

class QuestionTrackerView(ctk.CTkFrame):
    """Component for tracking and navigating between questions"""
    def __init__(self, parent, master, questions: List[QuestionModel], on_question_select: Callable):
        super().__init__(master, fg_color="transparent")
        self.parent = parent
        self.questions = questions
        self.on_question_select = on_question_select
        self.buttons = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        tracker_label = ctk.CTkLabel(self, text="Question Tracker", anchor="w")
        tracker_label.pack(anchor="w", padx=10, pady=(5, 10))
        
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Calculate cols_per_row as 30% of total questions, minimum 5, maximum 10
        cols_per_row = max(5, min(10, round(len(self.questions) * 0.3)))
        
        for i, question in enumerate(self.questions, 1):
            row = (i - 1) // cols_per_row
            col = (i - 1) % cols_per_row
            is_current = question.is_current  # Get current status from model
            btn = QuestionTrackerButton(
                self.parent,
                buttons_frame,
                question_id=i,
                is_current=is_current,
                question_model=question,
                on_click=self._on_question_button_click
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.buttons.append(btn)
    
    def _on_question_button_click(self, question_id: int):
        # Update model and UI
        for i, question in enumerate(self.questions, 1):
            question.is_current = (i == question_id)
        self.update_all_buttons()
        if self.on_question_select:
            self.on_question_select(question_id)
    
    def update_question_state(self, question_id: int, question_model: QuestionModel):
        """Update the state of a specific question button"""
        self.buttons[question_id - 1].update_state(
            is_current=question_model.is_current,
            question_model=question_model
        )
    
    def set_current_question(self, question_id: int):
        """Update tracker to highlight the current question"""
        if 1 <= question_id <= len(self.questions):
            # Update model
            for i, question in enumerate(self.questions, 1):
                question.is_current = (i == question_id)
            self.update_all_buttons()

    def update_all_buttons(self):
        """Update all button states based on their respective models"""
        for i, btn in enumerate(self.buttons, 1):
            btn.update_state(
                is_current=self.questions[i-1].is_current,
                question_model=self.questions[i-1]
            )

    def update_questions(self, questions: List[QuestionModel]):
        """Update all questions in the tracker"""
        self.questions = questions
        
        # Remove old buttons properly using try-except
        for btn in self.buttons:
            try:
                btn.grid_forget()
                btn.destroy()
            except tk.TclError:
                pass  # Ignore if widget is already destroyed
        self.buttons.clear()
        
        # Clear any existing widgets in the frame
        for widget in self.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass
        
        # Recreate widgets with new questions
        self._create_widgets()
