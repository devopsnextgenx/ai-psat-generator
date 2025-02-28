import customtkinter as ctk
import tkinter as tk
from typing import Callable
from ai.models.psatModel import QuestionModel
from ai.ui.components.psat.solution import Solution

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
        self.question_frame = ctk.CTkFrame(self.content_frame, corner_radius=0, fg_color="transparent")
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
        self.choices_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
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