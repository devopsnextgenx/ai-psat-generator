import customtkinter as ctk
import tkinter as tk
from ai.models.psatModel import QuestionModel, Choice
from ai.ui.components.psat.questionTracker import QuestionTrackerView
from ai.ui.components.psat.question import QuestionView
import json

class QuestionPaperController(ctk.CTkFrame):
    """Controller class for the question paper UI"""
    def __init__(self, parent, status_bar, questions):
        super().__init__(parent, fg_color="transparent")
        self.status_bar = status_bar
        self.questions = questions
        self.is_evaluated = False
        
        # Create main container frame
        self.main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Add title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Question Paper",
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(pady=10)
        if len([q for q in self.questions if q.is_current]):
            current_q = [q for q in self.questions if q.is_current][0]
            if current_q is None:
                self.status_bar.update_status(4, "No questions found, setting current as first question.")
                self.questions[0].is_current = True
                current_q = self.questions[0]
            # Create question view
            self.question_view = QuestionView(
                self.main_frame, 
                [q for q in self.questions if q.is_current][0],
                self._on_selection_change
            )
            self.question_view.pack(fill=tk.BOTH, expand=True)
        else:
            self.status_bar.update_status(4, "No questions found, please load questions.")
            # Create question view
            self.question_view = QuestionView(
                self.main_frame, 
                None,
                self._on_selection_change
            )
            self.question_view.pack(fill=tk.BOTH, expand=True)
        
        # Create question tracker
        self.tracker_view = QuestionTrackerView(
            self,
            self.main_frame,
            self.questions,  # Pass the questions list instead of just the count
            self._on_question_select
        )
        self.tracker_view.pack(side="bottom", fill=tk.X)
        
        # Add evaluation checkbox
        self.eval_var = tk.BooleanVar(value=False)
        self.eval_checkbox = ctk.CTkCheckBox(
            self.main_frame,
            text="Show Results",
            variable=self.eval_var,
            command=self._toggle_evaluation
        )
        self.eval_checkbox.pack(pady=5)
        
        # Create score label
        self.score_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Arial", 12)
        )
        self.score_label.pack(pady=5)

    def _calculate_score(self):
        """Calculate the current score"""
        correct = sum(1 for q in self.questions if q.is_correct())
        total = len(self.questions)
        return correct, total

    def _update_progress_status(self):
        """Update progress bar and status text"""
        total = len(self.questions)
        
        # Handle case when there are no questions
        if total == 0:
            self.status_bar.update_status(0.0, "No questions loaded")
            return
            
        answered = sum(1 for q in self.questions if q.selected_choice is not None)
        correct, _ = self._calculate_score()
        progress = answered * 100 / total
        
        status_text = (f"Score: {correct}/{total} correct | "
                    f"Progress: {answered}/{total} answered")
        self.status_bar.update_status(progress, status_text)
    
    def _on_question_select(self, question_id: int):
        """Handle question selection from the tracker"""
        self.question_view.update_model([q for q in self.questions if q.question_id == question_id][0])
    
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
        self.status_bar.update_status(progress, status_text)
    
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

    def update_questions(self, questions_data):
        """Update the question paper with new questions
        
        Args:
            questions_data (list): List of dictionaries containing question data
        """
        # Convert dictionary to QuestionModel list
        question_models = []
        for q in questions_data:
            try:
                # Create Choice objects for each option
                choices = []
                for choice_dict in q["choices"]:
                    choices.append(Choice(key=choice_dict["key"].lower(), value=str(choice_dict["value"])))
                
                if not hasattr(q, "is_current"):
                    q["is_current"] = False

                # Create QuestionModel instance
                question_model = QuestionModel(
                    question_id=q["question_id"],
                    question_text=str(q["question_text"]),
                    choices=choices,
                    correct_answer=q["correct_answer"].lower(),  # Ensure lowercase
                    explanation=str(q["explanation"]),
                    show_answer=False,
                    is_current=q["is_current"]
                )

                question_models.append(question_model)
            except Exception as e:
                print(f"Error processing question: {e}")
                continue

        # Update the questions list
        self.questions = question_models
        
        # Update question view with first question
        if len(self.questions) > 0:
            for q in self.questions:
                if q.is_current:
                    self.question_view.update_model(q)
                    break
            
        # Update tracker view
        self.tracker_view.update_questions(self.questions)
        
        # Update status
        self._update_progress_status()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
    
    def _toggle_evaluation(self):
        """Toggle evaluation state and update UI"""
        self.is_evaluated = self.eval_var.get()
        
        # Update all question buttons in tracker
        for question in self.questions:
            self.tracker_view.update_question_state(
                question.question_id,
                question
            )
            
        # Update score display
        if self.is_evaluated:
            correct, total = self._calculate_score()
            self.score_label.configure(
                text=f"Score: {correct}/{total} ({(correct/total)*100:.1f}%)"
            )
        else:
            self.score_label.configure(text="")
