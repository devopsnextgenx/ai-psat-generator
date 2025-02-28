import customtkinter as ctk
import tkinter as tk
from ai.models.psatModel import QuestionModel, Choice
from ai.ui.components.psat.questionGrid import QuestionTrackerView
from ai.ui.components.psat.question import QuestionView
import json

class QuestionPaperController(ctk.CTkFrame):
    """Controller class for the question paper UI"""
    def __init__(self, master, status_bar, questions):
        super().__init__(master)
        self.status_bar = status_bar
        self.questions = questions
        self.current_question_id = 1
        
        # Create sample questions
        self._create_sample_questions()
        
        # Create main container frame
        self.main_frame = ctk.CTkFrame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Question Paper",
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
        self.tracker_view.pack(fill=tk.X)

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
                
                # Create QuestionModel instance
                question_model = QuestionModel(
                    question_id=q["question_id"],
                    question_text=str(q["question_text"]),
                    choices=choices,
                    correct_answer=q["correct_answer"].lower(),  # Ensure lowercase
                    explanation=str(q["explanation"]),
                    show_answer=False
                )
                question_models.append(question_model)
            except Exception as e:
                print(f"Error processing question: {e}")
                continue

        # Update the questions list
        self.questions = question_models
        
        # Reset UI
        self.current_question_id = 1
        
        # Update question view with first question
        if len(self.questions) > 0:
            self.question_view.update_model(self.questions[0])
            
        # Update tracker view
        self.tracker_view.update_questions(self.questions)
        
        # Update status
        self._update_progress_status()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
