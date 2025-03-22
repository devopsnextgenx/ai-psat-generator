from ai.models.psatModel import QuestionModel, Choice

def create_sample_questions():
    """Create sample question data using the new QuestionModel format"""
    questions = []
    questions.append(QuestionModel(
        question_id=1,
        question_text="What is friction?",
        choices=[
            Choice(key='a', value="A force that opposes motion between surfaces in contact"),
            Choice(key='b', value="A force that accelerates objects"),
            Choice(key='c', value="A type of energy conversion"),
            Choice(key='d', value="A form of mechanical advantage")
        ],
        correct_answer='a',
        explanation="Friction is a force that opposes the relative motion between two surfaces in contact.",
        is_current=True
    ))

    questions.append(QuestionModel(
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
    
    questions.append(QuestionModel(
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
    
    questions.append(QuestionModel(
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
    
    questions.append(QuestionModel(
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
    
    questions.append(QuestionModel(
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


    return convert_questions_to_json(questions)

def convert_questions_to_json(questions):
    """Convert QuestionModel objects to JSON-compatible dictionary format"""
    json_questions = []
    for q in questions:
        question_dict = {
            "question_id": q.question_id,
            "question_text": q.question_text,
            "choices": [{"key": choice.key, "value": choice.value} for choice in q.choices],
            "correct_answer": q.correct_answer,
            "explanation": q.explanation
        }
        json_questions.append(question_dict)
    return json_questions