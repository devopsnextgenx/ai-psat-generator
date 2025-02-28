import logging
from ai.agent.Agent import Agent
from ai.models.schema import AgentResponse
from pydantic import Field, RootModel
from typing import List
from ai.models.psatModel import QuestionModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseSchema(RootModel):
    root: List[QuestionModel] = Field(..., min_items=1)

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
            Make sure answer and explaination for each question is accurately provided.
            Make sure question is formatted in multiline markdown format, with numbers and key data elements as code.

            Provide the question, correct answer, and choices in the JSON format.
        """

        action_response: AgentResponse  = self.agents['bot'].timed_generate(agentPrompt, ResponseSchema.model_json_schema())

        return action_response