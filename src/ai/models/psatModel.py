from typing import List, Dict, Optional, Literal
from pydantic import BaseModel

ALLOWED_CHOICES = ['a', 'b', 'c', 'd']

class Answer(BaseModel):
    key: Literal['a', 'b', 'c', 'd']
    explanation: str

class Choice(BaseModel):
    key: str
    value: str

class QuestionModel(BaseModel):
    """Model class to hold question data"""
    question_id: int
    question_text: str
    choices: List[Choice]
    correct_answer: Literal['a', 'b', 'c', 'd']
    explanation: str
    selected_choice: Optional[Literal['a', 'b', 'c', 'd']] = None
    show_answer: bool = False  # Added this line
    
    def to_dict(self) -> Dict:
        return self.model_dump()
    
    def is_correct(self) -> bool:
        """Check if the selected answer is correct"""
        return self.selected_choice == self.correct_answer
