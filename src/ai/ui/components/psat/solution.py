import customtkinter as ctk
import tkinter as tk
from ai.models.psatModel import QuestionModel

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