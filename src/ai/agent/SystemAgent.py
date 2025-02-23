import logging
from ai.agent.Agent import Agent
from ai.config.AgentXSchema import LlmConfig
from ai.models.schema import AgentResponse
from ai.operators.executer import ALLOWED_COMMANDS
from pydantic import BaseModel, Field, RootModel
from typing import List, Literal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_CHOICES = ['a', 'b', 'c', 'd']

class Answer(BaseModel):
    key: Literal['a', 'b', 'c', 'd']
    explaination: str

class Choice(BaseModel):
    key: Literal['a', 'b', 'c', 'd']
    value: str

class Question(BaseModel):
    question: str
    answer: Answer
    choices: List[Choice] = Field(..., min_items=2, max_items=4)

class ResponseSchema(RootModel):
    root: List[Question] = Field(..., min_items=1)

class SystemAgent:
    def __init__(self):
        self.agents = {
            "bot": Agent(
                agentName="qwen2.5-coder"
            )
        }

    def executeQuery(self, prompt: str) -> str:
        """Query the LLM with a prompt and return the response"""

        # print a physics question for friction, body, accelaration and force interation
        # list 5 questions on friction topic with different level of complexity and hardness, have couple of questions with true false 
        agentPrompt = f"""
            Build a multiple choice questions based on the following prompt:
            {prompt}

            Create exact number of questions based on the prompt.
            Make sure question is formatted in multiline markdown format, with numbers and key data elements as code.

            Provide the question, correct answer, and choices in the JSON format.
        """

        action_response: AgentResponse  = self.agents['bot'].timed_generate(agentPrompt, ResponseSchema.model_json_schema())
        print(action_response)

        return action_response