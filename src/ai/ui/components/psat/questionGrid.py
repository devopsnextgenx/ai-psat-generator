import customtkinter as ctk
import tkinter as tk
from typing import Callable, Dict, List
from ai.models.psatModel import QuestionModel

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
        try:
            self.is_current = is_current
            self.question_model = question_model
            colors = self._get_button_colors()
            self.configure(fg_color=colors["fg"], hover_color=colors["hover"])
        except tk.TclError:
            pass  # Ignore if widget is already destroyed

class QuestionTrackerView(ctk.CTkFrame):
    """Component for tracking and navigating between questions"""
    def __init__(self, master, questions: List[QuestionModel], on_question_select: Callable):
        super().__init__(master, fg_color="transparent")
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
            
            # Update states of existing buttons instead of recreating them
            for i, btn in enumerate(self.buttons, 1):
                btn.update_state(
                    is_current=(i == question_id),
                    question_model=self.questions[i-1]
                )

    def update_questions(self, questions: List[QuestionModel]):
        """Update all questions in the tracker"""
        self.questions = questions
        self.current_question = 1
        
        # Remove old buttons properly using try-except
        for btn in self.buttons:
            try:
                btn.grid_forget()  # Remove from grid instead of pack
                btn.destroy()
            except tk.TclError:
                pass  # Ignore if widget is already destroyed
        self.buttons.clear()
        
        # Clear any existing widgets in the frame
        for widget in self.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass  # Ignore if widget is already destroyed
        
        # Recreate widgets with grid layout
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create new tracker label
        tracker_label = ctk.CTkLabel(self, text="Question Tracker", anchor="w")
        tracker_label.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Create new buttons
        cols_per_row = 10  # Number of buttons per row
        for i, question in enumerate(self.questions, 1):
            row = (i - 1) // cols_per_row
            col = (i - 1) % cols_per_row
            
            btn = QuestionTrackerButton(
                buttons_frame,
                question_id=i,
                is_current=(i == 1),  # First question is current
                question_model=question,
                on_click=self._on_question_button_click
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.buttons.append(btn)
